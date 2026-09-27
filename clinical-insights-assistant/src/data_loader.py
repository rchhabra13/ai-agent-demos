"""
Data Loader Module
==================
Handles generation and loading of synthetic clinical trial datasets.
Provides utilities for data ingestion, validation, and preprocessing.
"""

import pandas as pd
import numpy as np
import os
from typing import Optional, Tuple


def generate_synthetic_data(
    num_patients: int = 200,
    days_per_patient: int = 30,
    seed: int = 42,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Generate a synthetic clinical trial dataset.

    Parameters
    ----------
    num_patients : int
        Number of patients to simulate.
    days_per_patient : int
        Number of trial days per patient.
    seed : int
        Random seed for reproducibility.
    output_path : str, optional
        If provided, saves the CSV to this path.

    Returns
    -------
    pd.DataFrame
        Synthetic clinical trial DataFrame with columns:
        patient_id, trial_day, dosage_mg, compliance_pct,
        adverse_event_flag, doctor_notes, outcome_score, cohort, visit_date
    """
    np.random.seed(seed)

    patient_ids = [f"P{str(i).zfill(3)}" for i in range(1, num_patients + 1)]
    cohorts = ['A', 'B']

    notes_templates = [
        "Patient stable, no complaints.",
        "Mild headache reported, advised rest.",
        "Fatigue noted, monitoring ongoing.",
        "Symptoms improving with current dosage.",
        "Adverse reaction observed, dosage adjustment needed.",
        "Blood pressure slightly elevated, continue monitoring.",
        "Patient reports improved sleep quality.",
        "Nausea reported after medication intake.",
        "Lab results within normal range.",
        "Patient missed previous appointment, compliance concern.",
    ]
    notes_probs = [0.30, 0.15, 0.12, 0.10, 0.05, 0.08, 0.07, 0.05, 0.05, 0.03]

    records = []
    for pid in patient_ids:
        cohort = np.random.choice(cohorts)
        base_compliance = np.random.normal(90, 8)

        for day in range(1, days_per_patient + 1):
            dosage = np.random.choice([50, 75, 100])
            # Compliance drifts over time with some noise
            compliance = np.clip(
                base_compliance + np.random.normal(0, 5) - (day * 0.1),
                50, 100
            )
            adverse_event = np.random.choice([0, 1], p=[0.9, 0.1])

            # Outcome score model
            base_score = (
                80
                + (dosage - 50) * 0.2
                + (compliance - 90) * 0.3
                - adverse_event * 15
                + (5 if cohort == 'A' else 0)  # Cohort A has slight advantage
            )
            outcome = np.clip(np.random.normal(base_score, 5), 40, 100)

            notes = np.random.choice(notes_templates, p=notes_probs)
            visit_date = pd.Timestamp('2024-01-01') + pd.Timedelta(days=day - 1)

            records.append([
                pid, day, dosage, round(compliance, 1), adverse_event,
                notes, round(outcome, 2), cohort, visit_date.strftime('%Y-%m-%d')
            ])

    df = pd.DataFrame(records, columns=[
        'patient_id', 'trial_day', 'dosage_mg', 'compliance_pct',
        'adverse_event_flag', 'doctor_notes', 'outcome_score',
        'cohort', 'visit_date'
    ])

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Dataset saved to {output_path} ({len(df)} rows)")

    return df


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load clinical trial data from a CSV file.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded and type-cast DataFrame.
    """
    df = pd.read_csv(filepath)
    df['visit_date'] = pd.to_datetime(df['visit_date'])
    df['adverse_event_flag'] = df['adverse_event_flag'].astype(int)
    df['dosage_mg'] = df['dosage_mg'].astype(int)
    return df


def validate_data(df: pd.DataFrame) -> dict:
    """
    Run validation checks on the clinical trial dataset.

    Returns a dict with validation results and any issues found.
    """
    issues = []

    required_cols = [
        'patient_id', 'trial_day', 'dosage_mg', 'compliance_pct',
        'adverse_event_flag', 'doctor_notes', 'outcome_score', 'cohort', 'visit_date'
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
        # Return early if columns are missing - can't validate further
        return {
            'valid': False,
            'num_rows': len(df),
            'num_patients': df['patient_id'].nunique() if 'patient_id' in df.columns else 0,
            'num_cohorts': df['cohort'].nunique() if 'cohort' in df.columns else 0,
            'date_range': None,
            'issues': issues
        }

    if df.isnull().sum().sum() > 0:
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        issues.append(f"Null values found: {null_cols}")

    if (df['compliance_pct'] < 0).any() or (df['compliance_pct'] > 100).any():
        issues.append("compliance_pct contains values outside 0-100 range")

    if (df['outcome_score'] < 0).any() or (df['outcome_score'] > 100).any():
        issues.append("outcome_score contains values outside 0-100 range")

    if not set(df['adverse_event_flag'].unique()).issubset({0, 1}):
        issues.append("adverse_event_flag contains values other than 0 and 1")

    return {
        'valid': len(issues) == 0,
        'num_rows': len(df),
        'num_patients': df['patient_id'].nunique(),
        'num_cohorts': df['cohort'].nunique(),
        'date_range': (str(df['visit_date'].min()), str(df['visit_date'].max())),
        'issues': issues
    }


def get_patient_summary(df: pd.DataFrame, patient_id: str) -> dict:
    """Get a summary for a specific patient."""
    patient_df = df[df['patient_id'] == patient_id]
    if patient_df.empty:
        return {'error': f'Patient {patient_id} not found'}

    return {
        'patient_id': patient_id,
        'cohort': patient_df['cohort'].iloc[0],
        'num_visits': len(patient_df),
        'avg_compliance': round(patient_df['compliance_pct'].mean(), 1),
        'avg_outcome': round(patient_df['outcome_score'].mean(), 2),
        'total_adverse_events': int(patient_df['adverse_event_flag'].sum()),
        'dosages_used': sorted(patient_df['dosage_mg'].unique().tolist()),
        'date_range': (
            str(patient_df['visit_date'].min()),
            str(patient_df['visit_date'].max())
        )
    }


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    output = os.path.join(data_dir, 'clinical_trial_data.csv')
    df = generate_synthetic_data(output_path=output)
    validation = validate_data(df)
    print(f"Validation: {validation}")
