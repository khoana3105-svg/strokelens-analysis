# Master prompt traceability

The original `StrokeLens_Universal_Master_Prompt.md` remains in the parent Machine Learning folder, byte-for-byte preserved (SHA-256 recorded in `source_integrity.json`). Nothing in the source prompt was shortened or overwritten. The project implements its phases as follows.

| Requirement group | Implementation / evidence |
|---|---|
| Full PDF/notebook audit, historical scores, conflicting splits | `SOURCE_AUDIT.md`; ignored complete source extracts; 31 pages / 22 cells; source hashes |
| Authoritative dataset, rights, exact version and conversion | `provenance.json`; direct Kaggle version 1 downloader; original CSV checksum; raw records ignored |
| Decimal anomalies, missingness, ranges, duplicate keys, rare/Unknown categories | `SOURCE_AUDIT.md`, `backend/schema.py`, generated `eda.json`, schema/total tests |
| Training-only preprocessing, CV, stratified untouched holdout | `backend/train.py`; imputer/scaler/one-hot pipeline; fold leakage stress test and real development-fit reconciliation |
| Five model families + majority baseline, bounded settings, imbalance | Ten settings; balanced weights where supported; no nominal-unsafe SMOTE; `metrics.json` |
| Predeclared AP/recall/precision selection and OOF threshold | Policy persisted before fit; chosen LR; `experiment_policy.json`, all trials/OOF thresholds |
| Once-after-selection holdout, complete artifact, schema, version | `model.joblib`, matching JSON/hash; 4,088 development and 1,022 holdout; final pipeline excludes holdout |
| Calibration assessment and honest uncertainty | OOF reliability/Brier, holdout Brier versus baseline, no post-hoc calibration claim; Wilson recall interval; bilingual limitations |
| Truthful global/local explanations | Development validation-fold permutation AP importance; exact LR transformed coefficients grouped by raw feature; score reconstruction test |
| Real typed inference API, load once, validation, SPA protection | `backend/app.py`; Pydantic profile/prediction; API and serialized-model tests; no request-time training |
| Five editorial responsive sections, real chart/form interactions | React section components; one chart library, native fetch; browser smoke evidence |
| Complete EN/VI, English default, persisted preference, translated errors | Typed dictionaries, 131-key parity, real browser language/error/persistence checks |
| Health/research framing, no diagnosis/causal/CDSS claims | Bilingual prominent safety notice, model card, score semantics and unit caveats |
| Backend tests, production build, translation check, lean CI | `tests/test_project.py`, TypeScript build with unused-code checks; `.github/workflows/ci.yml`; `DELIVERY.md` distinguishes executed checks from remote CI |
| Single-service deployment and health check | Static FastAPI serving, README commands, one multi-stage Dockerfile; container execution status disclosed |
| English README, screenshots only from running app | `README.md`, browser-captured local outputs; no hosted URL or synthetic screenshots |
| EN/VI portfolio, 2–3 CV bullets, five interview points | `PORTFOLIO.md`; measured outcomes only; AI assistance and ownership guidance |
| Public repository privacy, lean code, no stale claims | Reference files/raw/draft backups excluded; inactive draft components archived; no public student metadata/private paths; no publication performed |

Remaining scope/verification limits are recorded in `DELIVERY.md`. A configured CI workflow or Dockerfile is not evidence of a remote CI pass or live deployment. Local artifact/test/browser checks are separate.
