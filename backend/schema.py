"""Shared contract: no identifier or target in model features."""
import numpy as np
import pandas as pd

NUMERIC = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']
CATEGORIES = {
    'gender': ['Female', 'Male', 'Other'],
    'ever_married': ['No', 'Yes'],
    'work_type': ['Govt_job', 'Never_worked', 'Private', 'Self-employed', 'children'],
    'Residence_type': ['Rural', 'Urban'],
    'smoking_status': ['Unknown', 'formerly smoked', 'never smoked', 'smokes'],
}
FEATURES = NUMERIC + list(CATEGORIES)
RANGES = {'age': (0.08, 82), 'avg_glucose_level': (55.12, 271.74), 'bmi': (10.3, 97.6)}


def validate_dataset(df: pd.DataFrame) -> None:
    required = set(FEATURES + ['id', 'stroke'])
    if set(df.columns) != required:
        raise ValueError(f'Expected exactly these columns: {sorted(required)}')
    if df.empty or df['id'].isna().any() or df['id'].duplicated().any():
        raise ValueError('Dataset must have nonempty unique row identifiers.')
    for column in NUMERIC + ['stroke']:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f'{column}: expected numeric dtype.')
        if column != 'bmi' and df[column].isna().any():
            raise ValueError(f'{column}: missing values are not authorized.')
        if not np.isfinite(df[column].dropna()).all():
            raise ValueError(f'{column}: nonfinite value.')
    for column in ['hypertension', 'heart_disease', 'stroke']:
        if not df[column].isin([0, 1]).all():
            raise ValueError(f'{column}: expected 0/1.')
    if df['stroke'].nunique() != 2:
        raise ValueError('Both target classes are required.')
    for column, (low, high) in RANGES.items():
        if not df[column].dropna().between(low, high).all():
            raise ValueError(f'{column}: outside verified source range [{low}, {high}].')
    for column, values in CATEGORIES.items():
        if not df[column].isin(values).all():
            raise ValueError(f'{column}: unrecognized or missing category.')
