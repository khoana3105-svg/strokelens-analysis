"""Offline experiment. The final holdout is used only after selection."""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from backend.schema import CATEGORIES, FEATURES, NUMERIC, RANGES, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
POLICY = {
    'split': '80% development / 20% final holdout, stratified, seed=42; sort by id first',
    'cv': '3-fold shuffled stratified CV on development only, seed=42',
    'threshold': 'For each candidate, maximize precision subject to pooled OOF recall >= 0.75; tie: highest threshold.',
    'model': 'Prefer candidates with OOF precision >= 0.10 at recall >= 0.75; maximize OOF average precision. Within 0.01 AP of best, prefer Logistic Regression, then KNN, SVM, Tree, Forest in candidate order. If none qualify, use best AP and disclose failure.',
    'calibration': 'Assess OOF Brier score and 5 quantile-bin reliability. No post-hoc calibration: only 199 development positives; scores are educational outputs, never validated personal probabilities.',
    'holdout': 'Fit winner once on all development rows; compute final predictions once. No holdout tuning. CV selection estimates are optimistic after selection.',
    'importance': 'Mean AP decrease across 3 development validation folds, 5 permutations per raw feature; never used to select model.',
}


def make_pipeline(model):
    numeric = Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())])
    categorical = OneHotEncoder(categories=list(CATEGORIES.values()), handle_unknown='ignore', sparse_output=False)
    prep = ColumnTransformer([('numeric', numeric, NUMERIC), ('category', categorical, list(CATEGORIES))])
    return Pipeline([('preprocess', prep), ('model', model)])


def candidates():
    for c in [0.1, 1.0]:
        yield 'Logistic Regression', {'C': c, 'class_weight': 'balanced'}, LogisticRegression(C=c, class_weight='balanced', max_iter=2000, random_state=SEED)
    for k in [15, 35]:
        yield 'KNN', {'n_neighbors': k, 'weights': 'uniform'}, KNeighborsClassifier(n_neighbors=k)
    for c in [0.1, 1.0]:
        yield 'RBF SVM', {'C': c, 'class_weight': 'balanced', 'gamma': 'scale'}, SVC(C=c, class_weight='balanced', probability=True, random_state=SEED)
    for depth in [3, 5]:
        yield 'Decision Tree', {'max_depth': depth, 'min_samples_leaf': 30, 'class_weight': 'balanced'}, DecisionTreeClassifier(max_depth=depth, min_samples_leaf=30, class_weight='balanced', random_state=SEED)
    for depth in [5, 10]:
        yield 'Random Forest', {'max_depth': depth, 'n_estimators': 150, 'min_samples_leaf': 10, 'class_weight': 'balanced_subsample'}, RandomForestClassifier(max_depth=depth, n_estimators=150, min_samples_leaf=10, class_weight='balanced_subsample', random_state=SEED, n_jobs=1)


def choose_threshold(y, scores):
    precision, recall, thresholds = precision_recall_curve(y, scores)
    eligible = np.flatnonzero(recall[:-1] >= 0.75)
    index = max(eligible, key=lambda i: (precision[i], thresholds[i]))
    return float(thresholds[index])


def metrics(y, scores, threshold):
    labels = scores >= threshold
    return {'ap': float(average_precision_score(y, scores)), 'recall': float(recall_score(y, labels, zero_division=0)),
            'precision': float(precision_score(y, labels, zero_division=0)), 'f1': float(f1_score(y, labels, zero_division=0)),
            'roc_auc': float(roc_auc_score(y, scores)), 'accuracy': float(accuracy_score(y, labels)),
            'brier': float(brier_score_loss(y, scores)), 'confusion': confusion_matrix(y, labels, labels=[0, 1]).tolist()}


def curve_summary(y, scores):
    precision, recall, thresholds = precision_recall_curve(y, scores)
    indices = np.unique(np.linspace(0, len(thresholds) - 1, min(60, len(thresholds)), dtype=int))
    observed, predicted = calibration_curve(y, scores, n_bins=5, strategy='quantile')
    return {'pr': [{'recall': float(recall[i]), 'precision': float(precision[i])} for i in indices],
            'thresholds': [{'threshold': float(thresholds[i]), 'recall': float(recall[i]), 'precision': float(precision[i])} for i in indices],
            'calibration': [{'predicted': float(p), 'observed': float(o)} for p, o in zip(predicted, observed)]}


def histogram(series, target, bins):
    data = []
    for low, high in zip(bins[:-1], bins[1:]):
        included = series.ge(low) & (series.lt(high) if high != bins[-1] else series.le(high))
        n = int(included.sum())
        positives = int(target[included].sum())
        data.append({'label': f'{low:g}–{high:g}', 'count': n, 'positive': positives,
                     'rate': positives / n if n else None})
    return data


def eda(df):
    return {'rows': len(df), 'positive': int(df.stroke.sum()), 'prevalence': float(df.stroke.mean()),
            'missing': {column: int(df[column].isna().sum()) for column in FEATURES},
            'duplicates': int(df.duplicated().sum()), 'duplicate_ids': int(df.id.duplicated().sum()),
            'numeric': {column: {'min': float(df[column].min()), 'max': float(df[column].max()),
                                'mean': float(df[column].mean())} for column in NUMERIC},
            'histograms': {'age': histogram(df.age, df.stroke, np.array([0, 20, 40, 60, 83])),
                           'avg_glucose_level': histogram(df.avg_glucose_level, df.stroke, np.array([55, 90, 125, 160, 195, 230, 272])),
                           'bmi': histogram(df.bmi, df.stroke, np.array([10, 20, 30, 40, 50, 70, 98]))},
            'category_counts': {column: {v: int((df[column] == v).sum()) for v in values} for column, values in CATEGORIES.items()}}


def wilson(success, total):
    p, z = success / total, 1.96
    center = (p + z*z/(2*total)) / (1 + z*z/total)
    half = z * np.sqrt(p*(1-p)/total + z*z/(4*total*total)) / (1 + z*z/total)
    return [float(center-half), float(center+half)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'data/raw/healthcare-dataset-stroke-data.csv')
    args = parser.parse_args()
    artifacts = ROOT / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    provenance = json.loads((ROOT / 'docs/provenance.json').read_text(encoding='utf-8'))
    data_hash = hashlib.sha256(args.data.read_bytes()).hexdigest()
    if data_hash != provenance['sha256']:
        raise ValueError('CSV hash differs from recorded authoritative source. Review provenance first.')
    df = pd.read_csv(args.data).sort_values('id').reset_index(drop=True)
    validate_dataset(df)
    (artifacts / 'experiment_policy.json').write_text(json.dumps(POLICY, indent=2), encoding='utf-8')
    X, y = df[FEATURES], df.stroke
    development, holdout = train_test_split(np.arange(len(df)), test_size=.20, random_state=SEED, stratify=y)
    X_dev, y_dev = X.iloc[development], y.iloc[development]
    folds = list(StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED).split(X_dev, y_dev))
    trials, pipelines, predictions = [], [], []
    for family, params, model in candidates():
        pipeline = make_pipeline(model)
        scores = cross_val_predict(pipeline, X_dev, y_dev, cv=folds, method='predict_proba', n_jobs=1)[:, 1]
        threshold = choose_threshold(y_dev, scores)
        result = {'family': family, 'params': params, 'threshold': threshold, **metrics(y_dev, scores, threshold)}
        result['fold_ap'] = [float(average_precision_score(y_dev.iloc[val], scores[val])) for _, val in folds]
        trials.append(result)
        pipelines.append(pipeline)
        predictions.append(scores)
        print(f'{family} {params}: AP={result["ap"]:.4f}, recall={result["recall"]:.4f}, precision={result["precision"]:.4f}', flush=True)
    eligible = [i for i, t in enumerate(trials) if t['precision'] >= .10 and t['recall'] >= .75]
    constraint_met = bool(eligible)
    eligible = eligible or list(range(len(trials)))
    best_ap = max(trials[i]['ap'] for i in eligible)
    winner = min(i for i in eligible if trials[i]['ap'] >= best_ap - .01)
    chosen = trials[winner]
    threshold = chosen['threshold']
    importance = []
    for train, val in folds:
        fitted = clone(pipelines[winner]).fit(X_dev.iloc[train], y_dev.iloc[train])
        importance.append(permutation_importance(fitted, X_dev.iloc[val], y_dev.iloc[val],
                                                scoring='average_precision', n_repeats=5, random_state=SEED).importances)
    permutation = np.concatenate(importance, axis=1)
    pipeline = pipelines[winner].fit(X_dev, y_dev)
    test_scores = pipeline.predict_proba(X.iloc[holdout])[:, 1]
    test_metrics = metrics(y.iloc[holdout], test_scores, threshold)
    cm = test_metrics['confusion']
    test_metrics['recall_wilson_95'] = wilson(cm[1][1], sum(cm[1]))
    baseline = make_pipeline(DummyClassifier(strategy='most_frequent')).fit(X_dev, y_dev)
    baseline_scores = baseline.predict_proba(X.iloc[holdout])[:, 1]
    model_version = 'v1-' + data_hash[:10] + '-' + hashlib.sha256(json.dumps(chosen, sort_keys=True).encode()).hexdigest()[:8]
    split = {'development_rows': len(development), 'holdout_rows': len(holdout),
             'development_positive': int(y_dev.sum()), 'holdout_positive': int(y.iloc[holdout].sum()),
             'development_index_sha256': hashlib.sha256(development.tobytes()).hexdigest(),
             'holdout_index_sha256': hashlib.sha256(holdout.tobytes()).hexdigest()}
    report = {'version': model_version, 'selected': chosen, 'selection_constraint_met': constraint_met,
              'cv_trials': trials, 'holdout': test_metrics, 'baseline': metrics(y.iloc[holdout], baseline_scores, .5),
              'curves': {'oof': curve_summary(y_dev, predictions[winner]), 'holdout': curve_summary(y.iloc[holdout], test_scores)},
              'importance': [{'feature': f, 'mean': float(permutation[i].mean()), 'std': float(permutation[i].std())} for i, f in enumerate(FEATURES)],
              'split': split, 'policy': POLICY, 'data_sha256': data_hash,
              'environment': {'python': platform.python_version(), 'sklearn': sklearn.__version__, 'pandas': pd.__version__, 'numpy': np.__version__}}
    joblib.dump({'pipeline': pipeline, 'threshold': threshold, 'version': model_version,
                 'family': chosen['family'], 'features': FEATURES}, artifacts / 'model.joblib', compress=3)
    report['artifact_sha256'] = hashlib.sha256((artifacts / 'model.joblib').read_bytes()).hexdigest()
    for filename, value in [('metrics.json', report), ('eda.json', eda(df)),
                            ('schema.json', {'features': FEATURES, 'categories': CATEGORIES, 'ranges': RANGES, 'units': provenance['units']})]:
        (artifacts / filename).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    print(json.dumps({'selected': chosen, 'holdout': test_metrics, 'split': split}, indent=2))


if __name__ == '__main__':
    main()
