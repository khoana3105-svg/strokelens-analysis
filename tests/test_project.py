"""Real persisted-pipeline/API tests and synthetic leakage stress tests."""
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split

from backend.app import app
from backend.schema import FEATURES, NUMERIC, validate_dataset
from backend.train import SEED, choose_threshold, make_pipeline

ROOT = Path(__file__).resolve().parents[1]
PROFILE = {'age': 25, 'hypertension': 0, 'heart_disease': 0, 'avg_glucose_level': 85,
           'bmi': 22, 'gender': 'Female', 'ever_married': 'No', 'work_type': 'Private',
           'Residence_type': 'Rural', 'smoking_status': 'never smoked'}


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c


def test_artifact_and_real_inference(client):
    bundle = joblib.load(ROOT / 'artifacts/model.joblib')
    response = client.post('/api/predict', json=PROFILE)
    assert response.status_code == 200
    payload = response.json()
    score = bundle['pipeline'].predict_proba(pd.DataFrame([PROFILE], columns=FEATURES))[0, 1]
    assert payload['score'] == pytest.approx(score)
    assert payload['above_threshold'] == (score >= bundle['threshold'])
    assert payload['version'] == bundle['version']
    if payload['local'] is not None:
        terms = sum(term['value'] for term in payload['local']) + payload['intercept']
        assert terms == pytest.approx(payload['log_odds'])
        assert 1 / (1 + np.exp(-terms)) == pytest.approx(score)


@pytest.mark.parametrize('path', ['/api/health', '/api/overview', '/api/metrics', '/api/eda'])
def test_endpoints(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')


@pytest.mark.parametrize('changes', [ {'age': 188}, {'age': -1}, {'avg_glucose_level': 9297},
    {'bmi': 0}, {'gender': 'invalid'}, {'work_type': 'invalid'}, {'hypertension': 2},
    {'heart_disease': True}, {'age': '25'}, {'extra': 1}, {'smoking_status': None} ])
def test_invalid_inputs(client, changes):
    response = client.post('/api/predict', json={**PROFILE, **changes})
    assert response.status_code == 422
    assert 'input' not in response.text


def test_missing_required_and_malformed_json(client):
    assert client.post('/api/predict', json={}).status_code == 422
    assert client.post('/api/predict', content='{', headers={'content-type': 'application/json'}).status_code == 422


def test_missing_bmi_and_rare_categories(client):
    response = client.post('/api/predict', json={**PROFILE, 'bmi': None, 'gender': 'Other', 'smoking_status': 'Unknown'}).json()
    assert np.isfinite(response['score'])
    assert response['bmi_imputed']
    assert 'rare_category' in response['warnings']


def test_no_spa_for_api_or_missing_assets(client):
    for path in ['/api', '/api/unknown', '/api/predict/unknown', '/missing.js']:
        assert client.get(path).status_code == 404
    assert client.post('/api/unknown', json={}).status_code in [404, 405]


def test_unified_static_build(client):
    # This check intentionally requires a real production build, not a mock.
    assert (ROOT / 'frontend/dist/index.html').is_file()
    for path in ['/', '/explore']:
        response = client.get(path)
        assert response.status_code == 200
        assert '<div id="root">' in response.text
    asset = next((ROOT / 'frontend/dist/assets').glob('*.js'))
    assert client.get('/assets/' + asset.name).status_code == 200


def synthetic_frame():
    # Synthetic test input only; never used for experiment results.
    rows = [{**PROFILE, 'id': i, 'stroke': i % 2, 'age': 20 + i,
             'bmi': np.nan if i % 3 == 0 else 20 + i} for i in range(12)]
    return pd.DataFrame(rows)


@pytest.mark.parametrize('kind', ['missing_column', 'duplicate_id', 'decimal_corruption', 'invalid_target', 'missing_category', 'infinite'])
def test_dataset_contract(kind):
    frame = synthetic_frame()
    if kind == 'missing_column': frame = frame.drop(columns='age')
    elif kind == 'duplicate_id': frame.loc[1, 'id'] = 0
    elif kind == 'decimal_corruption': frame.loc[0, 'avg_glucose_level'] = 9297
    elif kind == 'invalid_target': frame.loc[0, 'stroke'] = 2
    elif kind == 'missing_category': frame.loc[0, 'gender'] = None
    elif kind == 'infinite': frame.loc[0, 'bmi'] = np.inf
    with pytest.raises(ValueError): validate_dataset(frame)


def test_fold_preprocessing_never_fits_validation():
    frame = synthetic_frame()
    for train, val in StratifiedKFold(3).split(frame, frame.stroke):
        pipeline = make_pipeline(LogisticRegression()).fit(frame.iloc[train][FEATURES], frame.iloc[train].stroke)
        prep = pipeline.named_steps['preprocess'].named_transformers_['numeric']
        medians = frame.iloc[train][NUMERIC].median().to_numpy()
        np.testing.assert_allclose(prep.named_steps['impute'].statistics_, medians)
        before = prep.named_steps['scale'].mean_.copy()
        extreme = frame.iloc[val][FEATURES].copy()
        extreme['age'] = 1000000
        extreme['gender'] = 'unseen_test_category'
        pipeline.predict_proba(extreme)
        np.testing.assert_array_equal(prep.named_steps['scale'].mean_, before)
        assert prep.named_steps['scale'].n_samples_seen_ == len(train)


def test_threshold_recall_constraint():
    labels = np.array([0, 0, 0, 1, 1, 1, 1])
    scores = np.array([.1, .3, .6, .2, .4, .7, .9])
    threshold = choose_threshold(labels, scores)
    assert ((scores >= threshold) & (labels == 1)).sum() / labels.sum() >= .75


def test_real_development_fit_and_provenance():
    path = ROOT / 'data/raw/healthcare-dataset-stroke-data.csv'
    if not path.exists():
        pytest.skip('Raw dataset intentionally not redistributed; run download_data.py for source reconciliation.')
    provenance = json.loads((ROOT / 'docs/provenance.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == provenance['sha256']
    frame = pd.read_csv(path).sort_values('id').reset_index(drop=True)
    validate_dataset(frame)
    train, holdout = train_test_split(np.arange(len(frame)), test_size=.2, random_state=SEED, stratify=frame.stroke)
    assert not set(train) & set(holdout)
    bundle = joblib.load(ROOT / 'artifacts/model.joblib')
    prep = bundle['pipeline'].named_steps['preprocess'].named_transformers_['numeric']
    np.testing.assert_allclose(prep.named_steps['impute'].statistics_, frame.iloc[train][NUMERIC].median())
    assert prep.named_steps['scale'].n_samples_seen_ == len(train)
    expected = frame.iloc[train][NUMERIC].fillna(frame.iloc[train][NUMERIC].median()).mean()
    np.testing.assert_allclose(prep.named_steps['scale'].mean_, expected)


def test_artifact_metrics_reconciliation(client):
    report = client.get('/api/metrics').json()
    eda = client.get('/api/eda').json()
    assert report['split']['development_rows'] + report['split']['holdout_rows'] == eda['rows']
    assert sum(sum(row) for row in report['holdout']['confusion']) == report['split']['holdout_rows']
    assert sum(report['holdout']['confusion'][1]) == report['split']['holdout_positive']
    for variable, bins in eda['histograms'].items():
        assert sum(row['count'] for row in bins) + eda['missing'][variable] == eda['rows']
