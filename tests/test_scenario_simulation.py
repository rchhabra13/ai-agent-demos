import pytest
import pandas as pd
import numpy as np
from src.scenario_simulation import (
    simulate_dosage_change,
    simulate_compliance_intervention,
    run_dosage_sensitivity_analysis,
    simulate_scenario
)


@pytest.fixture
def sample_data():
    """Create sample clinical trial data for testing."""
    data = {
        'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'trial_day': [5, 5, 5, 5, 5],
        'dosage_mg': [50, 50, 75, 75, 100],
        'compliance_pct': [95.0, 75.0, 88.0, 65.0, 92.0],
        'adverse_event_flag': [0, 1, 0, 1, 0],
        'doctor_notes': ['OK', 'Issue', 'OK', 'Issue', 'OK'],
        'outcome_score': [85.0, 65.0, 80.0, 60.0, 88.0],
        'cohort': ['A', 'B', 'A', 'B', 'A'],
        'visit_date': pd.to_datetime(['2024-01-05'] * 5)
    }
    return pd.DataFrame(data)


def test_simulate_dosage_change_returns_dataframe(sample_data):
    """Test that simulate_dosage_change returns a DataFrame."""
    result = simulate_dosage_change(sample_data, new_dosage=75)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_data)


def test_simulate_dosage_change_updates_dosage(sample_data):
    """Test that new dosage is applied."""
    result = simulate_dosage_change(sample_data, new_dosage=100)

    assert all(result['new_dosage'] == 100)


def test_simulate_dosage_change_preserves_original_data(sample_data):
    """Test that original values are preserved."""
    result = simulate_dosage_change(sample_data, new_dosage=75)

    assert 'original_dosage' in result.columns
    assert 'original_outcome' in result.columns
    assert 'original_compliance' in result.columns
    assert all(result['original_dosage'] == sample_data['dosage_mg'])


def test_simulate_dosage_change_calculates_outcome_change(sample_data):
    """Test that outcome change is calculated."""
    result = simulate_dosage_change(sample_data, new_dosage=75)

    assert 'outcome_change' in result.columns
    assert 'projected_outcome' in result.columns


def test_simulate_dosage_change_with_compliance_change(sample_data):
    """Test dosage change with compliance change."""
    result = simulate_dosage_change(sample_data, new_dosage=100, compliance_change=5.0)

    assert 'new_compliance' in result.columns
    assert all(result['new_compliance'] >= sample_data['compliance_pct'])


def test_simulate_dosage_change_single_patient(sample_data):
    """Test simulation for a single patient."""
    result = simulate_dosage_change(sample_data, patient_id='P001', new_dosage=100)

    assert len(result) == 1
    assert result.iloc[0]['patient_id'] == 'P001'


def test_simulate_dosage_change_projected_outcome_bounds(sample_data):
    """Test that projected outcomes stay within bounds."""
    result = simulate_dosage_change(sample_data, new_dosage=75)

    assert all(40 <= score <= 100 for score in result['projected_outcome'])


def test_simulate_compliance_intervention_returns_dict(sample_data):
    """Test that simulate_compliance_intervention returns a dictionary."""
    result = simulate_compliance_intervention(sample_data, compliance_boost=10.0)

    assert isinstance(result, dict)
    assert 'before' in result
    assert 'after' in result


def test_simulate_compliance_intervention_includes_metrics(sample_data):
    """Test that before/after metrics are included."""
    result = simulate_compliance_intervention(sample_data, compliance_boost=10.0)

    assert 'mean_compliance' in result['before']
    assert 'mean_outcome' in result['before']
    assert 'mean_compliance' in result['after']
    assert 'mean_outcome' in result['after']


def test_simulate_compliance_intervention_improves_outcome(sample_data):
    """Test that intervention improves projected outcomes."""
    result = simulate_compliance_intervention(sample_data, compliance_boost=10.0)

    after_outcome = result['after']['mean_outcome']
    before_outcome = result['before']['mean_outcome']
    assert after_outcome >= before_outcome


def test_simulate_compliance_intervention_targets_low_compliance(sample_data):
    """Test that low-compliance patients are targeted."""
    result = simulate_compliance_intervention(sample_data)

    # Default targets patients with compliance < 80%
    target_ids = result['target_patients']
    low_comp_patients = sample_data[sample_data['compliance_pct'] < 80]['patient_id'].unique()
    assert all(pid in low_comp_patients for pid in target_ids)


def test_simulate_compliance_intervention_custom_targets(sample_data):
    """Test with custom patient targets."""
    targets = ['P001', 'P003']
    result = simulate_compliance_intervention(sample_data, target_patients=targets)

    assert result['target_patients'] == targets


def test_simulate_compliance_intervention_interpretation(sample_data):
    """Test that interpretation string is provided."""
    result = simulate_compliance_intervention(sample_data, compliance_boost=15.0)

    assert 'interpretation' in result
    assert isinstance(result['interpretation'], str)
    assert '15.0' in result['interpretation'] or 'compliance' in result['interpretation'].lower()


def test_run_dosage_sensitivity_analysis_returns_dataframe(sample_data):
    """Test that sensitivity analysis returns a DataFrame."""
    result = run_dosage_sensitivity_analysis(sample_data)

    assert isinstance(result, pd.DataFrame)
    assert 'dosage_mg' in result.columns


def test_run_dosage_sensitivity_analysis_includes_metrics(sample_data):
    """Test that result includes required metrics."""
    result = run_dosage_sensitivity_analysis(sample_data)

    assert 'mean_projected_outcome' in result.columns
    assert 'std_projected_outcome' in result.columns
    assert 'mean_outcome_change' in result.columns
    assert 'pct_improved' in result.columns


def test_run_dosage_sensitivity_analysis_custom_dosages(sample_data):
    """Test with custom dosage levels."""
    dosages = [50, 75, 100, 125]
    result = run_dosage_sensitivity_analysis(sample_data, dosage_levels=dosages)

    assert len(result) == len(dosages)
    assert all(result['dosage_mg'].isin(dosages))


def test_run_dosage_sensitivity_analysis_default_dosages(sample_data):
    """Test with default dosage levels."""
    result = run_dosage_sensitivity_analysis(sample_data)

    default_dosages = [25, 50, 75, 100, 125, 150]
    assert len(result) == len(default_dosages)


def test_run_dosage_sensitivity_analysis_improvement_percentages(sample_data):
    """Test that improvement percentages are valid."""
    result = run_dosage_sensitivity_analysis(sample_data)

    assert all(0 <= pct <= 100 for pct in result['pct_improved'])
    assert all(0 <= pct <= 100 for pct in result['pct_declined'])


def test_simulate_scenario_dosage_change(sample_data):
    """Test simulate_scenario with dosage_change type."""
    result = simulate_scenario(sample_data, scenario_type='dosage_change', new_dosage=100)

    assert isinstance(result, dict)
    assert 'scenario' in result
    assert result['scenario'] == 'dosage_change'
    assert 'data' in result
    assert 'summary' in result


def test_simulate_scenario_dosage_change_summary(sample_data):
    """Test summary in dosage change scenario."""
    result = simulate_scenario(sample_data, scenario_type='dosage_change', new_dosage=75)

    summary = result['summary']
    assert 'mean_outcome_change' in summary
    assert 'patients_improved' in summary
    assert 'patients_declined' in summary


def test_simulate_scenario_compliance_intervention(sample_data):
    """Test simulate_scenario with compliance_intervention type."""
    result = simulate_scenario(sample_data, scenario_type='compliance_intervention', compliance_boost=10.0)

    assert isinstance(result, dict)
    assert 'before' in result
    assert 'after' in result


def test_simulate_scenario_sensitivity_analysis(sample_data):
    """Test simulate_scenario with sensitivity_analysis type."""
    result = simulate_scenario(sample_data, scenario_type='sensitivity_analysis')

    assert isinstance(result, dict)
    assert 'scenario' in result
    assert result['scenario'] == 'sensitivity_analysis'
    assert 'data' in result
    assert 'optimal_dosage' in result


def test_simulate_scenario_sensitivity_optimal_dosage(sample_data):
    """Test that optimal dosage is identified."""
    result = simulate_scenario(sample_data, scenario_type='sensitivity_analysis')

    optimal = result['optimal_dosage']
    assert isinstance(optimal, (int, np.integer))
    assert optimal > 0


def test_simulate_scenario_invalid_type(sample_data):
    """Test error handling for invalid scenario type."""
    result = simulate_scenario(sample_data, scenario_type='invalid_scenario')

    assert isinstance(result, dict)
    assert 'error' in result


def test_simulate_scenario_with_kwargs(sample_data):
    """Test passing additional kwargs to scenario."""
    result = simulate_scenario(
        sample_data,
        scenario_type='dosage_change',
        new_dosage=125,
        compliance_change=5.0
    )

    assert result['scenario'] == 'dosage_change'
    assert 'parameters' in result


def test_simulate_dosage_change_empty_data():
    """Test behavior with empty data."""
    df = pd.DataFrame({
        'patient_id': [],
        'dosage_mg': [],
        'outcome_score': [],
        'trial_day': [],
        'compliance_pct': [],
        'adverse_event_flag': [],
        'doctor_notes': [],
        'cohort': [],
        'visit_date': []
    })
    result = simulate_dosage_change(df, new_dosage=75)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_simulate_compliance_intervention_no_low_compliance():
    """Test intervention when no patients need intervention."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'compliance_pct': [95.0, 98.0, 96.0],
        'outcome_score': [85.0, 88.0, 87.0],
        'trial_day': [5, 5, 5],
        'dosage_mg': [100, 100, 100],
        'adverse_event_flag': [0, 0, 0],
        'doctor_notes': ['OK'] * 3,
        'cohort': ['A', 'B', 'A'],
        'visit_date': pd.to_datetime(['2024-01-05'] * 3)
    })
    result = simulate_compliance_intervention(df)

    assert 'message' in result or len(result['target_patients']) == 0
