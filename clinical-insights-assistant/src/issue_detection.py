"""
Issue Detection Module
======================
Detects non-compliance, adverse events, and anomalies in clinical trial data
using rule-based and statistical methods.
"""

import pandas as pd
import numpy as np
from typing import Optional


def detect_non_compliance(
    df: pd.DataFrame,
    threshold: float = 75.0
) -> pd.DataFrame:
    """
    Detect patients with compliance below threshold.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data.
    threshold : float
        Compliance percentage below which a patient is flagged.

    Returns
    -------
    pd.DataFrame
        DataFrame of non-compliant records with flag column.
    """
    flagged = df[df['compliance_pct'] < threshold].copy()
    flagged['issue_type'] = 'non_compliance'
    flagged['severity'] = flagged['compliance_pct'].apply(
        lambda x: 'high' if x < 60 else ('medium' if x < 70 else 'low')
    )
    return flagged


def detect_adverse_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract all records with adverse events and categorize severity.

    Returns
    -------
    pd.DataFrame
        Records with adverse_event_flag == 1, with additional context.
    """
    adverse = df[df['adverse_event_flag'] == 1].copy()
    adverse['issue_type'] = 'adverse_event'

    # Severity based on outcome score impact
    adverse['severity'] = adverse['outcome_score'].apply(
        lambda x: 'high' if x < 55 else ('medium' if x < 70 else 'low')
    )
    return adverse


def detect_outcome_anomalies(
    df: pd.DataFrame,
    z_threshold: float = 2.0
) -> pd.DataFrame:
    """
    Detect anomalous outcome scores using z-score method.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data.
    z_threshold : float
        Z-score threshold for flagging anomalies.

    Returns
    -------
    pd.DataFrame
        Records with anomalous outcome scores.
    """
    mean_score = df['outcome_score'].mean()
    std_score = df['outcome_score'].std()

    if std_score == 0:
        return pd.DataFrame(columns=df.columns.tolist() + ['z_score', 'issue_type', 'severity'])

    df_copy = df.copy()
    df_copy['z_score'] = (df_copy['outcome_score'] - mean_score) / std_score
    anomalies = df_copy[df_copy['z_score'].abs() > z_threshold].copy()
    anomalies['issue_type'] = 'outcome_anomaly'
    anomalies['severity'] = anomalies['z_score'].abs().apply(
        lambda z: 'high' if z > 3.0 else ('medium' if z > 2.5 else 'low')
    )
    return anomalies


def detect_dosage_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect unusual dosage patterns per patient (e.g., frequent changes).
    """
    results = []
    for pid, group in df.groupby('patient_id'):
        dosage_changes = (group.sort_values('trial_day')['dosage_mg'].diff() != 0).sum()
        if dosage_changes > len(group) * 0.5:
            for _, row in group.iterrows():
                rec = row.to_dict()
                rec['issue_type'] = 'dosage_instability'
                rec['severity'] = 'medium'
                rec['dosage_change_rate'] = round(dosage_changes / len(group), 2)
                results.append(rec)

    if not results:
        return pd.DataFrame()
    return pd.DataFrame(results)


def detect_declining_patients(
    df: pd.DataFrame,
    window: int = 7,
    decline_threshold: float = -5.0
) -> pd.DataFrame:
    """
    Detect patients whose outcome scores are declining over a rolling window.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data.
    window : int
        Rolling window size in days.
    decline_threshold : float
        Threshold for score change to be considered a decline.

    Returns
    -------
    pd.DataFrame
        Patient-level summary of declining trends.
    """
    results = []
    for pid, group in df.groupby('patient_id'):
        group = group.sort_values('trial_day')
        rolling_mean = group['outcome_score'].rolling(window=window, min_periods=3).mean()
        if len(rolling_mean.dropna()) >= 2:
            trend = rolling_mean.iloc[-1] - rolling_mean.dropna().iloc[0]
            if trend < decline_threshold:
                results.append({
                    'patient_id': pid,
                    'cohort': group['cohort'].iloc[0],
                    'score_trend': round(trend, 2),
                    'latest_score': round(group['outcome_score'].iloc[-1], 2),
                    'avg_compliance': round(group['compliance_pct'].mean(), 1),
                    'adverse_event_count': int(group['adverse_event_flag'].sum()),
                    'issue_type': 'declining_outcome',
                    'severity': 'high' if trend < -10 else 'medium'
                })

    if not results:
        return pd.DataFrame()
    return pd.DataFrame(results)


def run_all_detections(
    df: pd.DataFrame,
    compliance_threshold: float = 75.0,
    z_threshold: float = 2.0
) -> dict:
    """
    Run all detection analyses and return a comprehensive report.

    Returns
    -------
    dict
        Dictionary with keys for each detection type and summary statistics.
    """
    non_compliance = detect_non_compliance(df, compliance_threshold)
    adverse_events = detect_adverse_events(df)
    outcome_anomalies = detect_outcome_anomalies(df, z_threshold)
    dosage_anomalies = detect_dosage_anomalies(df)
    declining = detect_declining_patients(df)

    return {
        'non_compliance': {
            'data': non_compliance,
            'count': len(non_compliance),
            'patients_affected': non_compliance['patient_id'].nunique() if len(non_compliance) > 0 else 0
        },
        'adverse_events': {
            'data': adverse_events,
            'count': len(adverse_events),
            'patients_affected': adverse_events['patient_id'].nunique() if len(adverse_events) > 0 else 0
        },
        'outcome_anomalies': {
            'data': outcome_anomalies,
            'count': len(outcome_anomalies),
            'patients_affected': outcome_anomalies['patient_id'].nunique() if len(outcome_anomalies) > 0 else 0
        },
        'dosage_anomalies': {
            'data': dosage_anomalies,
            'count': len(dosage_anomalies),
            'patients_affected': dosage_anomalies['patient_id'].nunique() if len(dosage_anomalies) > 0 else 0
        },
        'declining_patients': {
            'data': declining,
            'count': len(declining),
            'patients_affected': declining['patient_id'].nunique() if len(declining) > 0 else 0
        },
        'summary': {
            'total_records_analyzed': len(df),
            'total_patients': df['patient_id'].nunique(),
            'total_issues_found': (
                len(non_compliance) + len(adverse_events) +
                len(outcome_anomalies) + len(dosage_anomalies) + len(declining)
            )
        }
    }
