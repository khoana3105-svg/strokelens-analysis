# Source audit

Read: all 31 PDF pages, all 22 notebook cells, stored text/HTML outputs and chart-generating code. Original documents remain outside this project. Local full-text extracts and merged drafts are ignored under `data/raw/`. SHA-256 digests in `source_integrity.json` attest source preservation; the master prompt has not been edited.

## Historical experiment, not a validated benchmark

- Source: Fedesoriano's Stroke Prediction Dataset, 5,110 rows, 12 columns. One row is an observational patient record; unique `id`, binary recorded `stroke` label. Ten predictors exclude identifier and target.
- Notebook: fill BMI with whole-data median 28.1, delete one `Other` gender row, nominal LabelEncoder, stratified 80/20 split (4,087/1,022 after deletion), training-fitted StandardScaler, ordinary SMOTE on all encoded features.
- Five families: Logistic Regression, KNN (k=5), RBF SVM, Tree (depth=6), Forest (100 trees). Evaluation used accuracy, precision, recall, F1; no training CV, AP, calibration evaluation, or training-only threshold selection.
- Stored claims (accuracy / precision / recall / F1): LR .7280/.1369/.8600/.2363; KNN .8063/.1064/.4000/.1681; SVM .7808/.1217/.5600/.2000; Tree .8004/.1709/.8000/.2817; Forest .9188/.1633/.1600/.1616. These figures are reference claims only, never used as generated UI scores.
- Whole-data BMI imputation leaks information; nominal integer codes invent distances/order; plain SMOTE can create fractional category codes. Removing `Other` is not justified by rarity alone. Recall alone and high accuracy do not validate clinical use.
- PDF p.8 says 70/30; p.12 and notebook cell 8 code/output show 80/20. Executable evidence resolves the historical split as 80/20.
- PDF p.27–28 uses an RF example score of 35% and checkup advice; notebook cell 19 uses LR with different example inputs/scores. They are not equivalent experiments or validated CDSS outputs. The new demo excludes medical recommendations and future-risk claims.
- Historical RF impurity importances (age .3454 etc.) explain RF, not the historical recommended LR. New importance is recomputed for the actual selected model on development validation folds.

## Decimal corruption investigation

The notebook has age mean 45.3154598826 and max 188; glucose mean 9622.80919765 and max 27174. The exact authoritative CSV has age mean 43.2266144814, range .08–82; glucose mean 106.1476771037, range 55.12–271.74.

Normalize each numeric value to its shortest decimal string (remove trailing fractional zeroes), then remove the decimal point: this reproduces **both** notebook means and age maximum exactly. In five notebook-displayed rows matched by identifier, source glucose 92.97, 85.81, 89.17, 98.53, 108.89 became 9297, 8581, 8917, 9853, 10889. Source age 1.88 can become 188. This strongly supports decimal-separator loss during conversion/import; the Excel file is missing, so the precise software step cannot be proven.

**Correction:** obtain unmodified publisher CSV version 1 and rebuild from it. Do not repair corrupted Excel by dividing everything by 100: integer or one-decimal values would be changed incorrectly. No source row was clipped, deleted, deduplicated, or imputed before splitting.

## Validated source contract

- 5,110 rows; 249 positives (4.8728%); 4,861 negatives.
- Missing BMI: 201 (3.9335%); no other missing predictor. Median imputation is fit within development folds and final development refit only.
- Zero duplicate identifiers and zero full-row duplicates. No rows removed. Reconciled development 4,088 + holdout 1,022 = 5,110, positives 199 + 50 = 249.
- Gender Female/Male/Other; married No/Yes; work Govt_job/Never_worked/Private/Self-employed/children; residence Rural/Urban; smoking Unknown/formerly smoked/never smoked/smokes. Categories come from the publisher schema, not held-out outcomes. `Other` is retained in a fixed one-hot vocabulary; with one row, subgroup performance is unknowable. `Unknown` is recorded unavailable smoking information, not a missing numeric value.
- BMI range 10.3–97.6: extremes retained without unsupported medical correction. API ranges deliberately stay within observed source support; they are not clinical admissibility rules.
- Age includes fractional years. BMI is interpreted as kg/m². Publisher does not specify glucose units, timing or assay; mg/dL is a reference-report convention only. UI explicitly discloses this assumption and keeps unaltered source values end-to-end.
- Confidential original sampling source, unclear collection dates, no validated prediction horizon or prospective sampling design. No causal inference, clinical screening, diagnosis, or general-population risk interpretation is warranted.

## Provenance and rights

Direct publisher: [Fedesoriano, Kaggle, version 1](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset), released 2021-01-26. Exact download URL, CSV SHA-256, byte count, extraction and unit assumptions: `provenance.json`. License metadata says **Data files © Original Authors** and description permits **educational purposes only**, with author credit. This is not an MIT/CC0 dataset. Raw files are excluded from public Git; publication/commercial reuse requires a separate rights review. The project is delivered locally, not published.
