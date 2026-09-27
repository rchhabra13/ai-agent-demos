import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from src.data_loader import (
    generate_synthetic_data,
    load_data,
    validate_data,
    get_patient_summary
)


@pytest.fixture
def sample_data():
    """Create sample clinical trial data for testing."""
    data = {
        'patient_id': ['P001', 'P001', 'P002', 'P002', 'P003'],
        'trial_day': [1, 2, 1, 2, 1],
        'dosage_mg': [50, 75, 100, 75, 50],
        'compliance_pct': [95.5, 92.3, 88.5, 85.2, 78.0],
        'adverse_event_flag': [0, 0, 1, 0, 0],
        'doctor_notes': [
            'Patient stable, no complaints.',
            'Mild headache reported, advised rest.',
            'Symptoms improving with current dosage.',
            'Patient stable, no complaints.',
            'Fatigue noted, monitoring ongoing.'
        ],
        'outcome_score': [85.2, 87.5, 72.1, 75.3, 68.9],
        'cohort': ['A', 'A', 'B', 'B', 'A'],
        'visit_date': pd.to_datetime([
            '2024-01-01', '2024-01-02', '2024-01-01',
            '2024-01-02', '2024-01-01'
        ])
    }
    return pd.DataFrame(data)


def test_generate_synthetic_data_basic():
    """Test basic synthetic data generation."""
    df = generate_synthetic_data(num_patients=10, days_per_patient=5, seed=42)

    assert len(df) == 50
    assert df['patient_id'].nunique() == 10
    assert set(df['cohort'].unique()).issubset({'A', 'B'})


def test_generate_synthetic_data_compliance_range():
    """Test that compliance values are within valid range."""
    df = generate_synthetic_data(num_patients=20, days_per_patient=5, seed=42)

    assert all(0 <= c <= 100 for c in df['compliance_pct'])
    assert all(0 <= o <= 100 for o in df['outcome_score'])


def test_generate_synthetic_data_adverse_events():
    """Test adverse event flags are binary."""
    df = generate_synthetic_data(num_patients=15, days_per_patient=4, seed=42)

    assert set(df['adverse_event_flag'].unique()).issubset({0, 1})


def test_generate_synthetic_data_with_output_file():
    """Test synthetic data generation with CSV output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'test_data.csv')
        df = generate_synthetic_data(num_patients=5, days_per_patient=3, output_path=output_path)

        assert os.path.exists(output_path)
        loaded_df = pd.read_csv(output_path)
        assert len(loaded_df) == 15


def test_validate_data_valid(sample_data):
    """Test validation on valid data."""
    result = validate_data(sample_data)

    assert result['valid'] is True
    assert result['num_rows'] == 5
    assert result['num_patients'] == 3


def test_validate_data_missing_columns(sample_data):
    """Test validation detects missing columns."""
    df = sample_data.drop('compliance_pct', axis=1)
    result = validate_data(df)

    assert result['valid'] is False
    assert any('Missing columns' in issue for issue in result['issues'])


def test_validate_data_null_values(sample_data):
    """Test validation detects null values."""
    df = sample_data.copy()
    df.loc[0, 'outcome_score'] = None
    result = validate_data(df)

    assert result['valid'] is False
    assert any('Null values' in issue for issue in result['issues'])


def test_validate_data_compliance_range(sample_data):
    """Test validation detects out-of-range compliance."""
    df = sample_data.copy()
    df.loc[0, 'compliance_pct'] = 125.0
    result = validate_data(df)

    assert result['valid'] is False
    assert any('compliance_pct' in issue for issue in result['issues'])


def test_validate_data_outcome_range(sample_data):
    """Test validation detects out-of-range outcome."""
    df = sample_data.copy()
    df.loc[0, 'outcome_score'] = -5.0
    result = validate_data(df)

    assert result['valid'] is False
    assert any('outcome_score' in issue for issue in result['issues'])


def test_validate_data_adverse_flag_invalid(sample_data):
    """Test validation detects invalid adverse event flags."""
    df = sample_data.copy()
    df.loc[0, 'adverse_event_flag'] = 2
    result = validate_data(df)

    assert result['valid'] is False
    assert any('adverse_event_flag' in issue for issue in result['issues'])


def test_get_patient_summary_valid_patient(sample_data):
    """Test getting summary for a valid patient."""
    summary = get_patient_summary(sample_data, 'P001')

    assert summary['patient_id'] == 'P001'
    assert summary['cohort'] == 'A'
    assert summary['num_visits'] == 2
    assert summary['total_adverse_events'] == 0


def test_get_patient_summary_nonexistent_patient(sample_data):
    """Test getting summary for non-existent patient."""
    summary = get_patient_summary(sample_data, 'P999')

    assert 'error' in summary


def test_load_data_from_csv():
    """Test loading data from CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'test_data.csv')
        df_original = generate_synthetic_data(num_patients=5, days_per_patient=3, output_path=output_path)

        df_loaded = load_data(output_path)

        assert len(df_loaded) == 15
        assert df_loaded['visit_date'].dtype == 'datetime64[ns]'
        assert df_loaded['adverse_event_flag'].dtype == 'int64'
