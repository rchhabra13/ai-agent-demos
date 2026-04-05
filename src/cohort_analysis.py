"""
Cohort Analysis Module
======================
Compare trial outcomes between patient cohorts using statistical methods.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Tuple


def compute_cohort_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute descriptive statistics per cohort.

    Returns
    -------
    pd.DataFrame
        Summary statistics for each cohort.
    """
    cohort_stats = df.groupby('cohort').agg(
        num_patients=('patient_id', 'nunique'),
        num_records=('patient_id', 'count'),
        mean_outcome=('outcome_score', 'mean'),
        std_outcome=('outcome_score', 'std'),
        median_outcome=('outcome_score', 'median'),
        mean_compliance=('compliance_pct', 'mean'),
        adverse_event_rate=('adverse_event_flag', 'mean'),
        mean_dosage=('dosage_mg', 'mean'),
    ).round(3)

    cohort_stats['ci_95_lower'] = cohort_stats['mean_outcome'] - 1.96 * (
        cohort_stats['std_outcome'] / np.sqrt(cohort_stats['num_records'])
    )
    cohort_stats['ci_95_upper'] = cohort_stats['mean_outcome'] + 1.96 * (
        cohort_stats['std_outcome'] / np.sqrt(cohort_stats['num_records'])
    )

    return cohort_stats.round(3)


def compare_cohorts_ttest(
    df: pd.DataFrame,
    metric: str = 'outcome_score'
) -> dict:
    """
    Perform independent t-test comparing two cohorts on a given metric.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data.
    metric : str
        Column name to compare.

    Returns
    -------
    dict
        Test results including t-statistic, p-value, effect size.
    """
    cohorts = sorted(df['cohort'].unique())
    if len(cohorts) != 2:
        return {'error': f'Expected 2 cohorts, found {len(cohorts)}'}

    group_a = df[df['cohort'] == cohorts[0]][metric].dropna()
    group_b = df[df['cohort'] == cohorts[1]][metric].dropna()

    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)

    # Cohen's d effect size
    pooled_std = np.sqrt(
        ((len(group_a) - 1) * group_a.std()**2 + (len(group_b) - 1) * group_b.std()**2)
        / (len(group_a) + len(group_b) - 2)
    )
    cohens_d = (group_a.mean() - group_b.mean()) / pooled_std if pooled_std > 0 else 0

    return {
        'metric': metric,
        'cohort_a': cohorts[0],
        'cohort_b': cohorts[1],
        'mean_a': round(group_a.mean(), 3),
        'mean_b': round(group_b.mean(), 3),
        'std_a': round(group_a.std(), 3),
        'std_b': round(group_b.std(), 3),
        'n_a': len(group_a),
        'n_b': len(group_b),
        't_statistic': round(t_stat, 4),
        'p_value': round(p_value, 6),
        'cohens_d': round(cohens_d, 4),
        'significant_at_05': p_value < 0.05,
        'significant_at_01': p_value < 0.01,
        'interpretation': _interpret_ttest(p_value, cohens_d, cohorts[0], cohorts[1])
    }


def _interpret_ttest(p_value: float, cohens_d: float, name_a: str, name_b: str) -> str:
    """Generate human-readable interpretation of t-test results."""
    if p_value >= 0.05:
        sig_text = "no statistically significant difference"
    elif p_value >= 0.01:
        sig_text = "a statistically significant difference (p < 0.05)"
    else:
        sig_text = "a highly significant difference (p < 0.01)"

    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        effect_text = "negligible"
    elif abs_d < 0.5:
        effect_text = "small"
    elif abs_d < 0.8:
        effect_text = "medium"
    else:
        effect_text = "large"

    better = name_a if cohens_d > 0 else name_b
    return (
        f"There is {sig_text} between cohorts {name_a} and {name_b}. "
        f"The effect size is {effect_text} (Cohen's d = {cohens_d:.3f}). "
        f"Cohort {better} shows higher mean scores."
    )


def compare_adverse_event_rates(df: pd.DataFrame) -> dict:
    """
    Compare adverse event rates between cohorts using chi-squared test.
    """
    cohorts = sorted(df['cohort'].unique())
    if len(cohorts) != 2:
        return {'error': f'Expected 2 cohorts, found {len(cohorts)}'}

    contingency = pd.crosstab(df['cohort'], df['adverse_event_flag'])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    rates = df.groupby('cohort')['adverse_event_flag'].mean()

    return {
        'test': 'chi-squared',
        'cohort_a': cohorts[0],
        'cohort_b': cohorts[1],
        'rate_a': round(rates[cohorts[0]], 4),
        'rate_b': round(rates[cohorts[1]], 4),
        'chi2_statistic': round(chi2, 4),
        'p_value': round(p_value, 6),
        'degrees_of_freedom': dof,
        'significant_at_05': p_value < 0.05
    }


def compare_compliance_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare compliance trends over trial days between cohorts.

    Returns a DataFrame with mean compliance per trial day per cohort.
    """
    trends = df.groupby(['cohort', 'trial_day']).agg(
        mean_compliance=('compliance_pct', 'mean'),
        mean_outcome=('outcome_score', 'mean'),
        adverse_rate=('adverse_event_flag', 'mean')
    ).reset_index().round(3)
    return trends


def run_full_cohort_analysis(df: pd.DataFrame) -> dict:
    """
    Run a comprehensive cohort comparison analysis.

    Returns
    -------
    dict
        Complete analysis results.
    """
    return {
        'cohort_stats': compute_cohort_stats(df),
        'outcome_comparison': compare_cohorts_ttest(df, 'outcome_score'),
        'compliance_comparison': compare_cohorts_ttest(df, 'compliance_pct'),
        'adverse_event_comparison': compare_adverse_event_rates(df),
        'trends': compare_compliance_trends(df)
    }
