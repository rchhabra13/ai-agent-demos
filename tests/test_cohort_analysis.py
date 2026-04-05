import pytest
import pandas as pd
import numpy as np
from src.cohort_analysis import (
    compute_cohort_stats,
    compare_cohorts_ttest,
    compare_adverse_event_rates,
    compare_compliance_trends,
    run_full_cohort_analysis
)


@pytest.fixture
def sample_data():
    """Create sample clinical trial data with two cohorts."""
    data = {
        'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008'],
        'trial_day': [1, 1, 1, 1, 5, 5, 5, 5],
        'dosage_mg': [50, 50, 75, 75, 50, 50, 75, 75],
        'compliance_pct': [95.0, 92.0, 88.0, 85.0, 90.0, 88.0, 85.0, 82.0],
        'adverse_event_flag': [0, 0, 0, 1, 0, 1, 1, 1],
        'doctor_notes': ['OK', 'OK', 'OK', 'Issue', 'OK', 'Issue', 'Issue', 'Issue'],
        'outcome_score': [85.0, 82.0, 78.0, 70.0, 88.0, 75.0, 72.0, 65.0],
        'cohort': ['A', 'A', 'B', 'B', 'A', 'A', 'B', 'B'],
        'visit_date': pd.to_datetime([
            '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01',
            '2024-01-05', '2024-01-05', '2024-01-05', '2024-01-05'
        ])
    }
    return pd.DataFrame(data)


def test_compute_cohort_stats_returns_dataframe(sample_data):
    """Test that compute_cohort_stats returns a DataFrame."""
    result = compute_cohort_stats(sample_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2  # Two cohorts


def test_compute_cohort_stats_includes_required_columns(sample_data):
    """Test that result includes required statistical columns."""
    result = compute_cohort_stats(sample_data)

    required_cols = ['num_patients', 'num_records', 'mean_outcome', 'std_outcome',
                     'median_outcome', 'mean_compliance', 'adverse_event_rate', 'mean_dosage']
    for col in required_cols:
        assert col in result.columns


def test_compute_cohort_stats_includes_confidence_intervals(sample_data):
    """Test that result includes 95% confidence intervals."""
    result = compute_cohort_stats(sample_data)

    assert 'ci_95_lower' in result.columns
    assert 'ci_95_upper' in result.columns


def test_compute_cohort_stats_correct_values(sample_data):
    """Test that statistics are computed correctly."""
    result = compute_cohort_stats(sample_data)

    cohort_a = sample_data[sample_data['cohort'] == 'A']
    assert result.loc['A', 'num_patients'] == cohort_a['patient_id'].nunique()
    assert result.loc['A', 'mean_outcome'] == round(cohort_a['outcome_score'].mean(), 3)


def test_compute_cohort_stats_single_cohort():
    """Test with single cohort data."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'cohort': ['A', 'A', 'A'],
        'outcome_score': [85.0, 82.0, 88.0],
        'compliance_pct': [95.0, 92.0, 90.0],
        'adverse_event_flag': [0, 0, 0],
        'dosage_mg': [50, 75, 100],
        'trial_day': [1, 1, 1],
        'doctor_notes': ['OK'] * 3,
        'visit_date': pd.to_datetime(['2024-01-01'] * 3)
    })
    result = compute_cohort_stats(df)

    assert len(result) == 1
    assert result.index[0] == 'A'


def test_compare_cohorts_ttest_returns_dict(sample_data):
    """Test that compare_cohorts_ttest returns a dictionary."""
    result = compare_cohorts_ttest(sample_data, metric='outcome_score')

    assert isinstance(result, dict)
    assert 'metric' in result
    assert 'p_value' in result


def test_compare_cohorts_ttest_includes_statistics(sample_data):
    """Test that t-test results include required statistics."""
    result = compare_cohorts_ttest(sample_data, metric='outcome_score')

    assert 'mean_a' in result
    assert 'mean_b' in result
    assert 't_statistic' in result
    assert 'cohens_d' in result
    assert 'significant_at_05' in result


def test_compare_cohorts_ttest_on_compliance(sample_data):
    """Test t-test on compliance metric."""
    result = compare_cohorts_ttest(sample_data, metric='compliance_pct')

    assert result['metric'] == 'compliance_pct'
    assert isinstance(result['p_value'], (float, np.floating))


def test_compare_cohorts_ttest_interpretation(sample_data):
    """Test that interpretation is included."""
    result = compare_cohorts_ttest(sample_data, metric='outcome_score')

    assert 'interpretation' in result
    assert isinstance(result['interpretation'], str)
    assert len(result['interpretation']) > 0


def test_compare_cohorts_ttest_single_cohort_error():
    """Test error handling when only one cohort present."""
    df = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'cohort': ['A', 'A', 'A'],
        'outcome_score': [85.0, 82.0, 88.0],
        'compliance_pct': [95.0, 92.0, 90.0],
        'adverse_event_flag': [0, 0, 0],
        'dosage_mg': [50, 75, 100],
        'trial_day': [1, 1, 1],
        'doctor_notes': ['OK'] * 3,
        'visit_date': pd.to_datetime(['2024-01-01'] * 3)
    })
    result = compare_cohorts_ttest(df, metric='outcome_score')

    assert 'error' in result


def test_compare_adverse_event_rates_returns_dict(sample_data):
    """Test that adverse event comparison returns a dictionary."""
    result = compare_adverse_event_rates(sample_data)

    assert isinstance(result, dict)
    assert 'test' in result
    assert result['test'] == 'chi-squared'


def test_compare_adverse_event_rates_includes_rates(sample_data):
    """Test that rates are included in result."""
    result = compare_adverse_event_rates(sample_data)

    assert 'rate_a' in result
    assert 'rate_b' in result
    assert 'chi2_statistic' in result
    assert 'p_value' in result


def test_compare_adverse_event_rates_valid_values(sample_data):
    """Test that rates are valid proportions."""
    result = compare_adverse_event_rates(sample_data)

    assert 0 <= result['rate_a'] <= 1
    assert 0 <= result['rate_b'] <= 1


def test_compare_adverse_event_rates_significance(sample_data):
    """Test that significance flag is included."""
    result = compare_adverse_event_rates(sample_data)

    assert 'significant_at_05' in result
    assert isinstance(result['significant_at_05'], (bool, np.bool_))


def test_compare_compliance_trends_returns_dataframe(sample_data):
    """Test that compliance trends returns a DataFrame."""
    result = compare_compliance_trends(sample_data)

    assert isinstance(result, pd.DataFrame)
    assert 'cohort' in result.columns
    assert 'trial_day' in result.columns


def test_compare_compliance_trends_includes_metrics(sample_data):
    """Test that trends include required metrics."""
    result = compare_compliance_trends(sample_data)

    assert 'mean_compliance' in result.columns
    assert 'mean_outcome' in result.columns
    assert 'adverse_rate' in result.columns


def test_compare_compliance_trends_organized_by_cohort(sample_data):
    """Test that trends are organized by cohort."""
    result = compare_compliance_trends(sample_data)

    cohorts = result['cohort'].unique()
    assert set(cohorts) == {'A', 'B'}


def test_compare_compliance_trends_ordered_by_day(sample_data):
    """Test that results are ordered by trial day."""
    result = compare_compliance_trends(sample_data)

    for cohort in result['cohort'].unique():
        cohort_data = result[result['cohort'] == cohort]
        days = cohort_data['trial_day'].values
        assert all(days[i] <= days[i+1] for i in range(len(days)-1))


def test_run_full_cohort_analysis_returns_dict(sample_data):
    """Test that full analysis returns a dictionary."""
    result = run_full_cohort_analysis(sample_data)

    assert isinstance(result, dict)
    assert 'cohort_stats' in result
    assert 'outcome_comparison' in result
    assert 'compliance_comparison' in result
    assert 'adverse_event_comparison' in result
    assert 'trends' in result


def test_run_full_cohort_analysis_cohort_stats_is_dataframe(sample_data):
    """Test that cohort stats is a DataFrame."""
    result = run_full_cohort_analysis(sample_data)

    assert isinstance(result['cohort_stats'], pd.DataFrame)


def test_run_full_cohort_analysis_comparisons_are_dicts(sample_data):
    """Test that comparisons are dictionaries."""
    result = run_full_cohort_analysis(sample_data)

    assert isinstance(result['outcome_comparison'], dict)
    assert isinstance(result['compliance_comparison'], dict)
    assert isinstance(result['adverse_event_comparison'], dict)


def test_run_full_cohort_analysis_trends_is_dataframe(sample_data):
    """Test that trends is a DataFrame."""
    result = run_full_cohort_analysis(sample_data)

    assert isinstance(result['trends'], pd.DataFrame)


def test_run_full_cohort_analysis_comprehensive():
    """Test full analysis with realistic data."""
    df = pd.DataFrame({
        'patient_id': [f'P{i:03d}' for i in range(1, 21)],
        'cohort': ['A'] * 10 + ['B'] * 10,
        'outcome_score': np.concatenate([
            np.random.normal(80, 5, 10),
            np.random.normal(75, 5, 10)
        ]),
        'compliance_pct': np.concatenate([
            np.random.normal(90, 5, 10),
            np.random.normal(85, 5, 10)
        ]),
        'adverse_event_flag': np.concatenate([
            np.random.choice([0, 1], 10, p=[0.8, 0.2]),
            np.random.choice([0, 1], 10, p=[0.7, 0.3])
        ]),
        'dosage_mg': np.repeat([50, 75], 10),
        'trial_day': [1] * 20,
        'doctor_notes': ['OK'] * 20,
        'visit_date': pd.to_datetime(['2024-01-01'] * 20)
    })

    result = run_full_cohort_analysis(df)

    assert isinstance(result, dict)
    assert len(result['cohort_stats']) == 2
    assert 'p_value' in result['outcome_comparison']
