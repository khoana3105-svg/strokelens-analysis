"""Single-service API and SPA. Inference only; load local trusted artifact once."""
from contextlib import asynccontextmanager
import hashlib
import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from sklearn.linear_model import LogisticRegression

from backend.schema import FEATURES

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'artifacts'
DIST = ROOT / 'frontend/dist'


class Profile(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    age: float = Field(ge=.08, le=82, strict=True)
    hypertension: int = Field(ge=0, le=1, strict=True)
    heart_disease: int = Field(ge=0, le=1, strict=True)
    avg_glucose_level: float = Field(ge=55.12, le=271.74, strict=True)
    bmi: float | None = Field(default=None, ge=10.3, le=97.6, strict=True)
    gender: Literal['Female', 'Male', 'Other']
    ever_married: Literal['No', 'Yes']
    work_type: Literal['Govt_job', 'Never_worked', 'Private', 'Self-employed', 'children']
    Residence_type: Literal['Rural', 'Urban']
    smoking_status: Literal['Unknown', 'formerly smoked', 'never smoked', 'smokes']


class Contribution(BaseModel):
    feature: str
    value: float


class Prediction(BaseModel):
    score: float
    above_threshold: bool
    threshold: float
    version: str
    family: str
    bmi_imputed: bool
    local: list[Contribution] | None
    intercept: float | None
    log_odds: float | None
    warnings: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not (ARTIFACTS / 'model.joblib').exists():
        raise RuntimeError('Missing model. Run python -m backend.train offline first.')
    content = {key: json.loads((ARTIFACTS / f'{key}.json').read_text(encoding='utf-8')) for key in ['metrics', 'eda', 'schema']}
    actual_hash = hashlib.sha256((ARTIFACTS / 'model.joblib').read_bytes()).hexdigest()
    if actual_hash != content['metrics']['artifact_sha256']:
        raise RuntimeError('Model checksum mismatch. Use a reviewed matching artifact bundle.')
    # Checksums detect accidental drift; never load an artifact supplied by a request.
    app.state.bundle = joblib.load(ARTIFACTS / 'model.joblib')
    app.state.content = content
    yield


app = FastAPI(title='StrokeLens', lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def invalid_profile(request: Request, exc: RequestValidationError):
    # Do not echo submitted health data or arbitrary raw values in errors.
    errors = [{'field': str(e['loc'][-1]), 'code': e['type']} for e in exc.errors()]
    return JSONResponse(status_code=422, content={'detail': errors})


@app.get('/api/health')
def health(request: Request):
    bundle = request.app.state.bundle
    return {'status': 'ok', 'version': bundle['version'], 'threshold': bundle['threshold'], 'family': bundle['family']}


@app.get('/api/overview')
def overview(request: Request):
    return {**health(request), 'schema': request.app.state.content['schema'],
            'provenance': json.loads((ROOT / 'docs/provenance.json').read_text(encoding='utf-8'))}


@app.get('/api/metrics')
def model_metrics(request: Request):
    return request.app.state.content['metrics']


@app.get('/api/eda')
def data_explorer(request: Request):
    return request.app.state.content['eda']


def linear_contributions(pipeline, frame):
    model = pipeline.named_steps['model']
    if not isinstance(model, LogisticRegression):
        return None, None, None
    prep = pipeline.named_steps['preprocess']
    transformed = prep.transform(frame)[0]
    terms = transformed * model.coef_[0]
    result = []
    numeric = prep.transformers_[0][2]
    for i, feature in enumerate(numeric):
        result.append({'feature': feature, 'value': float(terms[i])})
    offset = len(numeric)
    encoder = prep.named_transformers_['category']
    for feature, categories in zip(prep.transformers_[1][2], encoder.categories_):
        size = len(categories)
        result.append({'feature': feature, 'value': float(terms[offset:offset+size].sum())})
        offset += size
    intercept = float(model.intercept_[0])
    return result, intercept, float(intercept + terms.sum())


@app.post('/api/predict', response_model=Prediction)
def predict(profile: Profile, request: Request):
    bundle = request.app.state.bundle
    values = profile.model_dump()
    values['bmi'] = np.nan if values['bmi'] is None else values['bmi']
    frame = pd.DataFrame([values], columns=FEATURES)
    score = float(bundle['pipeline'].predict_proba(frame)[0, 1])
    local, intercept, log_odds = linear_contributions(bundle['pipeline'], frame)
    warnings = ['educational_only', 'not_future_probability', 'unit_assumption']
    if profile.gender == 'Other':
        warnings.append('rare_category')
    if profile.bmi is None:
        warnings.append('bmi_imputed')
    if (profile.age < 18 and (profile.ever_married == 'Yes' or profile.work_type != 'children')) or (profile.age >= 18 and profile.work_type == 'children'):
        warnings.append('unusual_combination')
    return Prediction(score=score, above_threshold=score >= bundle['threshold'],
                      threshold=bundle['threshold'], version=bundle['version'], family=bundle['family'],
                      bmi_imputed=profile.bmi is None, local=local, intercept=intercept, log_odds=log_odds, warnings=warnings)


if (DIST / 'assets').is_dir():
    app.mount('/assets', StaticFiles(directory=DIST / 'assets'), name='assets')


@app.get('/api/{path:path}', include_in_schema=False)
def unknown_api(path: str):
    raise HTTPException(status_code=404, detail='Unknown API endpoint')


@app.get('/{path:path}', include_in_schema=False)
def spa(path: str):
    if path.startswith('api/') or path == 'api':
        raise HTTPException(status_code=404)
    if not (DIST / 'index.html').exists():
        raise HTTPException(status_code=503, detail='Frontend not built. Run npm run build in frontend.')
    candidate = (DIST / path).resolve()
    if candidate.is_relative_to(DIST.resolve()) and candidate.is_file():
        return FileResponse(candidate)
    if Path(path).suffix:
        raise HTTPException(status_code=404, detail='Asset not found')
    return FileResponse(DIST / 'index.html')
