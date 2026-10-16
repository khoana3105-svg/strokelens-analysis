# Delivery and verification

Verified locally on **2026-10-14, Asia/Saigon**, with Python 3.14.8, Node 24.21.0, scikit-learn 1.9.1. Project saved inside the requested Machine Learning folder. Local Git repository initialized on `main`; no remote, commit, push, or hosted publication was performed.

## Actual status

| Check | Status | Evidence / limit |
|---|---|---|
| Read original references | PASS | 31 PDF pages, 22 notebook cells and stored textual/HTML outputs; source audit |
| Source preservation | PASS | Master Markdown, PDF, notebook SHA-256 unchanged after implementation |
| Authoritative dataset acquisition | PASS | Publisher version 1, educational-use terms, 316,971 original CSV bytes, exact SHA-256 |
| Decimal anomaly investigation | PASS | Removing decimal separators reproduces notebook age maximum and both suspect means; exact Excel import step unknown |
| Offline five-family experiment | PASS | Ten configurations, CV exclusively within 4,088 development rows, 1,022 final holdout, saved complete pipeline |
| API through real persisted pipeline | PASS | TestClient + real browser; load-once model version `v1-644d473b05-b0c0d19c` |
| Focused backend tests | PASS | **30 passed**, zero skips locally; final command `python -m pytest -q -p no:cacheprovider` |
| Translation parity | PASS | **131** nonempty EN/VI keys; typed dictionary; actual VI form/error and preference persistence |
| TypeScript / production build | PASS | Includes unused-local/parameter checks; Vite build, static assets served by FastAPI |
| Frontend formatting | PASS | `npm run check:format` |
| Dependency consistency | PASS | `python -m pip check`: no broken requirements |
| Browser interaction and responsive checks | PASS | Real headless Edge; five sections, two distinct-profile scores, null BMI, invalid age, global/local explanations, EDA selectors, OOF threshold slider, no page exceptions; widths **320/390/768** and desktop **1440** |
| Screenshots | PASS | Captured from the running production application; desktop EN and mobile VI copied into docs; additional captures in ignored outputs |
| Unified local production service | PASS | Actual GET `/api/health` status `ok`, actual SPA/static API/browser integration |
| Git/privacy exclusions | PASS | Raw CSV, reference extracts, merged drafts, venv, dependencies and local QA outputs ignored; source scan found no student identifiers/private machine paths in public project files |
| GitHub Actions remote execution | NOT RUN | Workflow configured; no remote repository/publication was requested |
| Docker image build/run | NOT RUN | Docker command unavailable in this environment; Dockerfile is provided, not a verified container deployment |
| Hosted URL / external medical validation | NOT RUN | Local delivery only; no clinical validation or publication claims |

One deprecation warning remains: Starlette 1.8.0 accepts `httpx` TestClient but recommends `httpx2` for future releases. Tests passed using the recorded locked stack. Training also reports scikit-learn's planned removal of `SVC(probability=True)` in 1.11; the bounded comparison uses pinned 1.9.1, and the deployed model is Logistic Regression. Do not upgrade those dependencies without rerunning validation/retraining as appropriate. Warnings are disclosed, not suppressed.

Browser automation waits for ResizeObserver to settle after viewport changes; instant measurement of a chart at its previous width is not a valid responsive-layout check. These browser checks are smoke tests, not exhaustive assistive-technology or cross-browser certification.

## Commands

From the `strokelens` folder in Windows PowerShell:

```powershell
# Dependencies and source (already supplied locally; needed on a fresh checkout)
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
& .\.venv\Scripts\python.exe scripts/download_data.py

# Reproduce the fixed experiment; never retune from holdout results
& .\.venv\Scripts\python.exe -m backend.train

# Frontend
Set-Location frontend
npm.cmd ci
npm.cmd run check:i18n
npm.cmd run check:format
npm.cmd run build
Set-Location ..

# Backend checks and local production service
& .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
& .\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` after the start command. The verification server is stopped at handoff; it is not a hosted URL.

Optional browser checks, with the app running in another terminal:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements-browser.txt
& .\.venv\Scripts\python.exe scripts/browser_smoke.py
```

## Deployment

Build frontend, keep the trusted matching model/JSON bundle, install the Python lock, and start `python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000`. Health endpoint: `/api/health`. No required secrets/env vars. A container alternative is documented in README; Docker execution remains unverified. Review dataset rights separately before public or commercial reuse; the original source permits educational use only.

## Observed results and caveats

Selected balanced Logistic Regression C=.1; threshold .5365964849. Holdout AP .1715, recall .82, precision .1470, F1 .2492, ROC-AUC .8534. Confusion TN=734, FP=238, FN=9, TP=41. Recall Wilson 95% interval .6920–.9023. Brier .1737 exceeds majority baseline .0489, so the score must not be treated as a calibrated future-risk probability. No validated forecast horizon, uncertain source units, sampling bias, one rare-category record and no external validation remain material limitations.

The missing source Excel file prevents proving the precise import operation. Decimal-loss reconstruction and authoritative reloading resolve the dataset used by this project without inventing corrected rows.

## Portfolio handoff

English/Vietnamese descriptions, three CV bullets and five interview points: `PORTFOLIO.md`. Full master-prompt requirement mapping: `REQUIREMENTS.md`. Read those with the audit and run/review the project before presenting personal contributions. No patient benefit or commercial impact was measured.
