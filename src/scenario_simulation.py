"""
Scenario Simulation Module
==========================
Simulate clinical what-if scenarios such as dosage adjustments
and predict their impact on patient outcomes.
"""

import pandas as pd
import numpy as np
from typing import Optional


def simulate_dosage_change(
    df: pd.DataFrame,
    patient_id: Optional[str] = None,
    new_dosage: int = 75,
    compliance_change: float = 0.0
) -> pd.DataFrame:
    """
    Simulate the impact of a dosage change on outcome scores.

    Uses a linear model derived from the data relationships:
    outcome ~ base + dosage_effect + compliance_effect - adverse_penalty

    Parameters
    ----------
    df : pd.DataFrame
        Original clinical trial data.
    patient_id : str, optional
        If provided, simulate only for this patient. Otherwise, all patients.
    new_dosage : int
        New dosage in mg (50, 75, or 100).
    compliance_change : float
        Percentage change in compliance (e.g., +5.0 means 5% increase).

    Returns
    -------
    pd.DataFrame
        Simulated outcomes with original and projected scores.
    """
    if patient_id:
        sim_df = df[df['patient_id'] == patient_id].copy()
    else:
        sim_df = df.copy()

    if sim_df.empty:
        return pd.DataFrame()

    sim_df['original_dosage'] = sim_df['dosage_mg']
    sim_df['original_outcome'] = sim_df['outcome_score']
    sim_df['original_compliance'] = sim_df['compliance_pct']

    # Calculate dosage effect coefficient from the data
    dosage_effect = 0.2  # per mg increase from baseline 50
    compliance_effect = 0.3  # per percentage point

    # Apply dosage change
    dosage_delta = new_dosage - sim_df['dosage_mg']
    compliance_delta = compliance_change

    sim_df['new_dosage'] = new_dosage
    sim_df['new_compliance'] = np.clip(
        sim_df['compliance_pct'] + compliance_delta, 50, 100
    )

    # Project new outcome
    outcome_change = (
        dosage_delta * dosage_effect
        + compliance_delta * compliance_effect
    )
    sim_df['projected_outcome'] = np.clip(
        sim_df['outcome_score'] + outcome_change + np.random.normal(0, 2, len(sim_df)),
        40, 100
    ).round(2)

    sim_df['outcome_change'] = (
        sim_df['projected_outcome'] - sim_df['original_outcome']
    ).round(2)

    return sim_df


def simulate_compliance_intervention(
    df: pd.DataFrame,
    target_patients: Optional[list] = None,
    compliance_boost: float = 10.0
) -> dict:
    """
    Simulate the effect of a compliance intervention program.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data.
    target_patients : list, optional
        List of patient IDs to target. If None, targets low-compliance patients.
    compliance_boost : float
        Expected compliance improvement in percentage points.

    Returns
    -------
    dict
        Before/after comparison metrics.
    """
    if target_patients is None:
        # Target patients with compliance below 80%
        patient_avg = df.groupby('patient_id')['compliance_pct'].mean()
        target_patients = patient_avg[patient_avg < 80].index.tolist()

    if not target_patients:
        return {
            'message': 'No patients meet the criteria for intervention.',
            'target_patients': [],
            'before': {},
            'after': {}
        }

    targeted_df = df[df['patient_id'].isin(target_patients)].copy()

    before_metrics = {
        'num_patients': len(target_patients),
        'mean_compliance': round(targeted_df['compliance_pct'].mean(), 2),
        'mean_outcome': round(targeted_df['outcome_score'].mean(), 2),
        'adverse_event_rate': round(targeted_df['adverse_event_flag'].mean(), 4)
    }

    # Simulate boosted compliance
    new_compliance = np.clip(targeted_df['compliance_pct'] + compliance_boost, 50, 100)
    compliance_delta = new_compliance - targeted_df['compliance_pct']
    projected_outcome = np.clip(
        targeted_df['outcome_score'] + compliance_delta * 0.3,
        40, 100
    )

    after_metrics = {
        'num_patients': len(target_patients),
        'mean_compliance': round(new_compliance.mean(), 2),
        'mean_outcome': round(projected_outcome.mean(), 2),
        'projected_improvement': round(projected_outcome.mean() - targeted_df['outcome_score'].mean(), 2)
    }

    return {
        'target_patients': target_patients,
        'compliance_boost': compliance_boost,
        'before': before_metrics,
        'after': after_metrics,
        'interpretation': (
            f"Intervening on {len(target_patients)} low-compliance patients with a "
            f"{compliance_boost}% compliance boost is projected to improve average "
            f"outcome scores by {after_metrics['projected_improvement']} points "
            f"(from {before_metrics['mean_outcome']} to {after_metrics['mean_outcome']})."
        )
    }


def run_dosage_sensitivity_analysis(
    df: pd.DataFrame,
    dosage_levels: list = None
) -> pd.DataFrame:
    """
    Run sensitivity analysis across multiple dosage levels.

    Returns
    -------
    pd.DataFrame
        Summary of projected outcomes at each dosage level.
    """
    if dosage_levels is None:
        dosage_levels = [25, 50, 75, 100, 125, 150]

    results = []
    for dosage in dosage_levels:
        sim = simulate_dosage_change(df, new_dosage=dosage)
        results.append({
            'dosage_mg': dosage,
            'mean_projected_outcome': round(sim['projected_outcome'].mean(), 2),
            'std_projected_outcome': round(sim['projected_outcome'].std(), 2),
            'mean_outcome_change': round(sim['outcome_change'].mean(), 2),
            'pct_improved': round((sim['outcome_change'] > 0).mean() * 100, 1),
            'pct_declined': round((sim['outcome_change'] < 0).mean() * 100, 1),
        })

    return pd.DataFrame(results)


def simulate_scenario(
    df: pd.DataFrame,
    scenario_type: str = 'dosage_change',
    **kwargs
) -> dict:
    """
    Unified scenario simulation interface.

    Parameters
    ----------
    scenario_type : str
        One of 'dosage_change', 'compliance_intervention', 'sensitivity_analysis'
    **kwargs
        Additional parameters for the specific scenario.

    Returns
    -------
    dict
        Simulation results.
    """
    if scenario_type == 'dosage_change':
        result = simulate_dosage_change(df, **kwargs)
        return {
            'scenario': 'dosage_change',
            'parameters': kwargs,
            'data': result,
            'summary': {
                'mean_outcome_change': round(result['outcome_change'].mean(), 2),
                'patients_improved': int((result['outcome_change'] > 0).sum()),
                'patients_declined': int((result['outcome_change'] < 0).sum()),
            }
        }
    elif scenario_type == 'compliance_intervention':
        return simulate_compliance_intervention(df, **kwargs)
    elif scenario_type == 'sensitivity_analysis':
        result = run_dosage_sensitivity_analysis(df, **kwargs)
        return {
            'scenario': 'sensitivity_analysis',
            'data': result,
            'optimal_dosage': int(result.loc[result['mean_projected_outcome'].idxmax(), 'dosage_mg'])
        }
    else:
        return {'error': f'Unknown scenario type: {scenario_type}'}
