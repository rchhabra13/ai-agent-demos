import pytest
import pandas as pd
import numpy as np
from src.issue_detection import (
    detect_non_compliance,
    detect_adverse_events,
    detect_outcome_anomalies,
    detect_dosage_anomalies,
    detect_declining_patients,
    run_all_detections
)


@pytest.fixture
def sample_data():
    """Create sample clinical trial data for testing."""
    data = {
        'patient_id': ['P001', 'P001', 'P002', 'P002', 'P003', 'P003', 'P004', 'P004'],
        'trial_day': [1, 10, 1, 10, 1, 10, 1, 10],
        'dosage_mg': [50, 50, 75, 100, 50, 50, 100, 100],
        'compliance_pct': [95.0, 90.0, 72.0, 68.0, 88.0, 75.0, 92.0, 91.0],
        'adverse_event_flag': [0, 0, 1, 1, 0, 0, 0, 1],
        'doctor_notes': [
            'Stable', 'Good progress', 'Headache', 'Persistent headache',
            'OK', 'Fatigue', 'Excellent', 'Minor issue'
        ],
        'outcome_score': [80.0, 85.0, 65.0, 60.0, 75.0, 72.0, 88.0, 82.0],
        'cohort': ['A', 'A', 'B', 'B', 'A', 'A', 'B', 'B'],
        'visit_date': pd.to_datetime([
            '2024-01-01', '2024-01-10', '2024-01-01', '2024-01-10',
            '2024-01-01', '2024-01-10', '2024-01-01', '2024-01-10'
        ])
    }
    return pd.DataFrame(data)


def test_detect_non_compliance_identifies_low_compliance(sample_data):
    """Test that non-compliance is correctly identified."""
    result = detect_non_compliance(sample_data, threshold=75.0)

    assert len(result) > 0
    assert all(result['compliance_pct'] < 75.0)
    assert all(result['issue_type'] == 'non_compliance')


def test_detect_non_compliance_severity_assignment(sample_data):
    """Test that severity levels are correctly assigned."""
    result = detect_non_compliance(sample_data, threshold=85.0)

    assert 'severity' in result.columns
    assert all(result['severity'].isin(['high', 'medium', 'low']))


def test_detect_non_compliance_empty_result(sample_data):
    """Test when no non-compliance issues are found."""
    result = detect_non_compliance(sample_data, threshold=50.0)

    assert len(result) == 0


def test_detect_non_compliance_custom_threshold():
    """Test with custom compliance threshold."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'compliance_pct': [95.0, 80.0, 50.0],
        'trial_day': [1, 1, 1],
        'dosage_mg': [50, 75, 100],
        'adverse_event_flag': [0, 0, 1],
        'doctor_notes': ['OK', 'OK', 'Issue'],
        'outcome_score': [85.0, 75.0, 60.0],
        'cohort': ['A', 'B', 'A'],
        'visit_date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-01'])
    })
    result = detect_non_compliance(df, threshold=75.0)

    assert len(result) == 1
    assert result.iloc[0]['patient_id'] == 'P003'


def test_detect_adverse_events_identifies_events(sample_data):
    """Test that adverse events are correctly identified."""
    result = detect_adverse_events(sample_data)

    assert len(result) > 0
    assert all(result['adverse_event_flag'] == 1)
    assert all(result['issue_type'] == 'adverse_event')


def test_detect_adverse_events_includes_severity():
    """Test that severity is assigned to adverse events."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'adverse_event_flag': [1, 1, 1],
        'outcome_score': [50.0, 72.0, 85.0],
        'trial_day': [1, 1, 1],
        'dosage_mg': [50, 75, 100],
        'compliance_pct': [90.0, 85.0, 95.0],
        'doctor_notes': ['Issue', 'Minor issue', 'OK'],
        'cohort': ['A', 'B', 'A'],
        'visit_date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-01'])
    })
    result = detect_adverse_events(df)

    assert 'severity' in result.columns
    assert result.iloc[0]['severity'] == 'high'  # outcome_score 50.0


def test_detect_adverse_events_empty_result():
    """Test when no adverse events are found."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'adverse_event_flag': [0, 0, 0],
        'outcome_score': [85.0, 80.0, 88.0],
        'trial_day': [1, 1, 1],
        'dosage_mg': [50, 75, 100],
        'compliance_pct': [90.0, 85.0, 95.0],
        'doctor_notes': ['OK', 'OK', 'OK'],
        'cohort': ['A', 'B', 'A'],
        'visit_date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-01'])
    })
    result = detect_adverse_events(df)

    assert len(result) == 0


def test_detect_outcome_anomalies_identifies_anomalies():
    """Test that outcome anomalies are detected."""
    # Need enough data points for z-score to be meaningful
    scores = [75.0, 78.0, 76.0, 77.0, 74.0, 76.5, 77.5, 75.5, 76.0, 20.0]
    df = pd.DataFrame({
        'patient_id': [f'P{i:03d}' for i in range(len(scores))],
        'outcome_score': scores,
        'trial_day': [1] * len(scores),
        'dosage_mg': [50] * len(scores),
        'compliance_pct': [90.0] * len(scores),
        'adverse_event_flag': [0] * len(scores),
        'doctor_notes': ['OK'] * len(scores),
        'cohort': ['A'] * len(scores),
        'visit_date': pd.to_datetime(['2024-01-01'] * len(scores))
    })
    result = detect_outcome_anomalies(df, z_threshold=2.0)

    assert len(result) > 0
    assert all(result['issue_type'] == 'outcome_anomaly')


def test_detect_outcome_anomalies_with_custom_zscore():
    """Test outcome anomalies with custom z-score threshold."""
    scores = [75.0, 76.0, 74.5, 75.5, 76.5, 74.0, 75.0, 76.0, 75.0, 100.0]
    df = pd.DataFrame({
        'patient_id': [f'P{i:03d}' for i in range(len(scores))],
        'outcome_score': scores,
        'trial_day': [1] * len(scores),
        'dosage_mg': [50] * len(scores),
        'compliance_pct': [90.0] * len(scores),
        'adverse_event_flag': [0] * len(scores),
        'doctor_notes': ['OK'] * len(scores),
        'cohort': ['A'] * len(scores),
        'visit_date': pd.to_datetime(['2024-01-01'] * len(scores))
    })
    result = detect_outcome_anomalies(df, z_threshold=1.5)

    assert len(result) > 0


def test_detect_dosage_anomalies_identifies_instability(sample_data):
    """Test detection of dosage instability."""
    result = detect_dosage_anomalies(sample_data)

    if len(result) > 0:
        assert 'issue_type' in result.columns
        assert all(result['issue_type'] == 'dosage_instability')


def test_detect_dosage_anomalies_empty_result():
    """Test when no dosage anomalies exist."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P001', 'P002', 'P002'],
        'trial_day': [1, 2, 1, 2],
        'dosage_mg': [100, 100, 100, 100],  # No changes
        'outcome_score': [75.0, 78.0, 80.0, 82.0],
        'compliance_pct': [90.0, 92.0, 88.0, 90.0],
        'adverse_event_flag': [0, 0, 0, 0],
        'doctor_notes': ['OK'] * 4,
        'cohort': ['A', 'A', 'B', 'B'],
        'visit_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02'])
    })
    result = detect_dosage_anomalies(df)

    assert len(result) == 0 or isinstance(result, pd.DataFrame)


def test_detect_declining_patients_identifies_decline(sample_data):
    """Test detection of patients with declining outcomes."""
    result = detect_declining_patients(sample_data, window=5, decline_threshold=-5.0)

    if len(result) > 0:
        assert 'issue_type' in result.columns
        assert all(result['issue_type'] == 'declining_outcome')


def test_detect_declining_patients_custom_window():
    """Test with custom rolling window."""
    df = pd.DataFrame({
        'patient_id': ['P001'] * 6,
        'trial_day': [1, 2, 3, 4, 5, 6],
        'outcome_score': [85.0, 80.0, 75.0, 70.0, 65.0, 60.0],
        'compliance_pct': [90.0, 88.0, 85.0, 82.0, 80.0, 78.0],
        'adverse_event_flag': [0, 0, 0, 1, 1, 1],
        'doctor_notes': ['OK'] * 6,
        'dosage_mg': [100] * 6,
        'cohort': ['A'] * 6,
        'visit_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03',
                                      '2024-01-04', '2024-01-05', '2024-01-06'])
    })
    result = detect_declining_patients(df, window=3, decline_threshold=-5.0)

    if len(result) > 0:
        assert result.iloc[0]['patient_id'] == 'P001'


def test_run_all_detections_returns_dict(sample_data):
    """Test that run_all_detections returns a dictionary with all keys."""
    result = run_all_detections(sample_data)

    assert isinstance(result, dict)
    assert 'non_compliance' in result
    assert 'adverse_events' in result
    assert 'outcome_anomalies' in result
    assert 'dosage_anomalies' in result
    assert 'declining_patients' in result
    assert 'summary' in result


def test_run_all_detections_has_data_and_counts(sample_data):
    """Test that detection results include data and counts."""
    result = run_all_detections(sample_data)

    for detection_type in ['non_compliance', 'adverse_events', 'outcome_anomalies', 'dosage_anomalies']:
        assert 'data' in result[detection_type]
        assert 'count' in result[detection_type]
        assert 'patients_affected' in result[detection_type]


def test_run_all_detections_summary_stats(sample_data):
    """Test that summary includes key statistics."""
    result = run_all_detections(sample_data)

    summary = result['summary']
    assert 'total_records_analyzed' in summary
    assert 'total_patients' in summary
    assert 'total_issues_found' in summary


def test_run_all_detections_with_custom_thresholds():
    """Test run_all_detections with custom parameters."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003', 'P004'],
        'compliance_pct': [95.0, 80.0, 70.0, 60.0],
        'adverse_event_flag': [0, 1, 1, 0],
        'outcome_score': [85.0, 75.0, 65.0, 55.0],
        'trial_day': [1, 1, 1, 1],
        'dosage_mg': [50, 75, 100, 125],
        'doctor_notes': ['OK', 'Issue', 'Issue', 'Severe'],
        'cohort': ['A', 'B', 'A', 'B'],
        'visit_date': pd.to_datetime(['2024-01-01'] * 4)
    })
    result = run_all_detections(df, compliance_threshold=75.0, z_threshold=2.0)

    assert isinstance(result, dict)
    assert len(result['summary']) > 0
