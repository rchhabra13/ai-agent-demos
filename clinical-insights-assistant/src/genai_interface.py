"""
GenAI Interface Module
======================
Provides LLM-powered summarization and analysis capabilities.
Uses mock/template-based responses for self-contained operation.
Can be swapped with real OpenAI/Azure calls by changing the backend.
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime


class MockLLM:
    """
    Mock LLM that generates template-based responses mimicking
    a real language model for clinical trial analysis.
    """

    def __init__(self, model_name: str = "mock-gpt-4"):
        self.model_name = model_name
        self.call_count = 0

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a mock response based on prompt analysis."""
        self.call_count += 1
        prompt_lower = prompt.lower()

        if 'summarize' in prompt_lower and 'doctor' in prompt_lower:
            return self._doctor_notes_summary(prompt)
        elif 'regulatory' in prompt_lower or 'fda' in prompt_lower:
            return self._regulatory_summary(prompt)
        elif 'adverse' in prompt_lower:
            return self._adverse_event_summary(prompt)
        elif 'cohort' in prompt_lower or 'comparison' in prompt_lower:
            return self._cohort_summary(prompt)
        elif 'scenario' in prompt_lower or 'dosage' in prompt_lower:
            return self._scenario_summary(prompt)
        elif 'recommend' in prompt_lower or 'next step' in prompt_lower:
            return self._recommendation_summary(prompt)
        else:
            return self._general_summary(prompt)

    def _doctor_notes_summary(self, prompt: str) -> str:
        return (
            "## Doctor Notes Summary\n\n"
            "**Key Themes Identified:**\n"
            "1. **Patient Stability**: The majority of clinical notes indicate stable patient conditions "
            "with no significant complaints, suggesting the treatment regimen is generally well-tolerated.\n"
            "2. **Mild Side Effects**: A notable subset of patients reported mild headaches and fatigue, "
            "which are consistent with the known side effect profile of the study drug.\n"
            "3. **Positive Response Indicators**: Several notes document symptom improvement, "
            "particularly among patients with high compliance rates.\n\n"
            "**Adverse Events:**\n"
            "- Approximately 10% of visit records flagged adverse reactions\n"
            "- Most common: headache, fatigue, nausea\n"
            "- Severe reactions requiring dosage adjustment were rare (<5%)\n\n"
            "**Anomalies Detected:**\n"
            "- Some patients with high compliance still showed declining outcome scores, "
            "suggesting potential drug resistance or unmeasured confounders\n"
            "- Compliance tracking gaps noted for a small subset of patients\n"
        )

    def _regulatory_summary(self, prompt: str) -> str:
        date_str = datetime.now().strftime('%B %d, %Y')
        return (
            f"## Regulatory Summary Report\n"
            f"**Prepared:** {date_str}\n"
            f"**Study Phase:** Phase III Clinical Trial\n\n"
            "**EXECUTIVE SUMMARY**\n\n"
            "This clinical trial evaluated the efficacy and safety of the study drug across "
            "two patient cohorts (A and B) with a total enrollment of 200 patients over a "
            "30-day observation period. The primary endpoint was the composite outcome score "
            "measured on a standardized 0-100 scale.\n\n"
            "**EFFICACY FINDINGS**\n\n"
            "The study drug demonstrated a statistically significant improvement in outcome "
            "scores among compliant patients (compliance > 80%). Mean outcome scores were "
            "consistently higher in Cohort A compared to Cohort B, with a moderate effect size. "
            "Dose-response analysis indicated optimal efficacy at the 75mg dosage level, with "
            "diminishing returns observed at higher doses.\n\n"
            "**SAFETY PROFILE**\n\n"
            "The overall adverse event rate was approximately 10%, consistent with pre-clinical "
            "projections. The most frequently reported adverse events included headache (15%), "
            "fatigue (12%), and nausea (5%). No serious adverse events (SAEs) requiring trial "
            "discontinuation were reported. Adverse events were generally mild to moderate in "
            "severity and self-limiting. The safety profile supports the favorable benefit-risk "
            "ratio of the study drug at the recommended dosage.\n"
        )

    def _adverse_event_summary(self, prompt: str) -> str:
        return (
            "## Adverse Event Analysis Summary\n\n"
            "**Overview:** Adverse events were detected in approximately 10% of all recorded "
            "patient visits across both cohorts.\n\n"
            "**Distribution by Severity:**\n"
            "- Low severity: 60% of adverse events (mild symptoms, self-resolving)\n"
            "- Medium severity: 30% (required monitoring or minor intervention)\n"
            "- High severity: 10% (required dosage adjustment or treatment modification)\n\n"
            "**Correlation Analysis:**\n"
            "- Adverse events were inversely correlated with compliance (r = -0.23)\n"
            "- Higher dosage levels showed marginally increased adverse event rates\n"
            "- No significant difference in adverse event rates between cohorts\n\n"
            "**Recommendation:** Continue monitoring patients with recurring adverse events "
            "and consider dosage reduction for patients experiencing high-severity events.\n"
        )

    def _cohort_summary(self, prompt: str) -> str:
        return (
            "## Cohort Comparison Summary\n\n"
            "**Study Design:** Two-arm parallel group comparison (Cohort A vs. Cohort B)\n\n"
            "**Key Findings:**\n"
            "- Cohort A demonstrated moderately higher mean outcome scores compared to Cohort B\n"
            "- The difference was statistically significant (p < 0.05) with a small-to-medium "
            "effect size\n"
            "- Compliance patterns were similar between cohorts, ruling out compliance as a "
            "confounding factor\n"
            "- Adverse event rates did not differ significantly between groups\n\n"
            "**Interpretation:** The observed difference in outcomes between cohorts may be "
            "attributable to the treatment protocol variations. Further subgroup analysis is "
            "recommended to identify patient characteristics driving the differential response.\n"
        )

    def _scenario_summary(self, prompt: str) -> str:
        return (
            "## Scenario Simulation Summary\n\n"
            "**Simulation Results:**\n"
            "The dosage adjustment simulation projects the following outcomes:\n\n"
            "- Increasing dosage from 50mg to 75mg: Projected +5.0 point improvement in mean "
            "outcome scores with a minimal increase in adverse event probability\n"
            "- Increasing dosage from 75mg to 100mg: Projected +2.5 point improvement with "
            "moderate increase in adverse event probability\n"
            "- Compliance intervention (+10%): Projected +3.0 point improvement in outcomes "
            "for targeted low-compliance patients\n\n"
            "**Risk Assessment:** The benefit-risk profile is most favorable at the 75mg dosage "
            "level. Dosages above 100mg show diminishing returns with increased adverse event "
            "risk.\n"
        )

    def _recommendation_summary(self, prompt: str) -> str:
        return (
            "## Recommended Next Steps\n\n"
            "Based on the comprehensive analysis of the clinical trial data, the following "
            "actions are recommended:\n\n"
            "1. **Dosage Optimization:** Consider standardizing the dosage at 75mg for patients "
            "currently on 50mg, given the projected outcome improvement.\n"
            "2. **Compliance Monitoring:** Implement enhanced compliance tracking for the 15% of "
            "patients showing declining adherence over the trial period.\n"
            "3. **Adverse Event Protocol:** Establish a rapid-response protocol for the subset "
            "of patients experiencing recurring adverse events.\n"
            "4. **Subgroup Analysis:** Conduct detailed analysis on patients showing unexpected "
            "outcome declines despite high compliance.\n"
            "5. **Regulatory Preparation:** Begin compiling the Phase III clinical study report "
            "with the generated regulatory summaries as a foundation.\n"
        )

    def _general_summary(self, prompt: str) -> str:
        return (
            "## Analysis Summary\n\n"
            "The clinical trial data has been analyzed across multiple dimensions including "
            "patient outcomes, compliance patterns, adverse events, and cohort comparisons. "
            "Key insights include generally favorable treatment outcomes with an overall mean "
            "score above the efficacy threshold, manageable adverse event rates, and "
            "statistically significant differences between cohorts. Detailed findings are "
            "available in the individual analysis modules.\n"
        )


# Module-level LLM instance
_llm = MockLLM()


def get_llm() -> MockLLM:
    """Get the current LLM instance."""
    return _llm


def summarize_doctor_notes(df: pd.DataFrame) -> str:
    """
    Summarize doctor notes from the dataset using GenAI.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data containing 'doctor_notes' column.

    Returns
    -------
    str
        LLM-generated summary of doctor notes.
    """
    notes = df['doctor_notes'].value_counts()
    notes_context = "\n".join([f"- '{note}': {count} occurrences" for note, count in notes.items()])

    prompt = (
        f"Summarize the following doctor notes from a clinical trial with "
        f"{df['patient_id'].nunique()} patients over {df['trial_day'].max()} days.\n\n"
        f"Note frequency:\n{notes_context}\n\n"
        f"Total adverse events: {df['adverse_event_flag'].sum()}\n"
        f"Average outcome score: {df['outcome_score'].mean():.2f}\n\n"
        f"Please summarize key themes, adverse events, and anomalies."
    )
    return _llm.generate(prompt)


def generate_regulatory_summary(
    df: pd.DataFrame,
    cohort_results: Optional[dict] = None,
    detection_results: Optional[dict] = None
) -> str:
    """
    Generate a regulatory-ready summary aligned with FDA expectations.

    Parameters
    ----------
    df : pd.DataFrame
        Clinical trial data.
    cohort_results : dict, optional
        Results from cohort analysis.
    detection_results : dict, optional
        Results from issue detection.

    Returns
    -------
    str
        FDA-style regulatory summary.
    """
    prompt = (
        f"Generate an FDA-style regulatory summary for a clinical trial.\n"
        f"Patients: {df['patient_id'].nunique()}\n"
        f"Cohorts: {df['cohort'].nunique()}\n"
        f"Duration: {df['trial_day'].max()} days\n"
        f"Mean outcome: {df['outcome_score'].mean():.2f}\n"
        f"Adverse event rate: {df['adverse_event_flag'].mean():.2%}\n"
    )
    return _llm.generate(prompt)


def summarize_scenario_results(scenario_results: dict) -> str:
    """Generate a natural language summary of scenario simulation results."""
    prompt = (
        f"Summarize the following scenario simulation results:\n"
        f"Scenario type: {scenario_results.get('scenario', 'unknown')}\n"
        f"Parameters: {scenario_results.get('parameters', {})}\n"
    )
    return _llm.generate(prompt)


def generate_cohort_narrative(cohort_results: dict) -> str:
    """Generate a narrative comparison of cohort results."""
    prompt = (
        f"Generate a narrative comparison of clinical trial cohorts.\n"
        f"Results: {cohort_results.get('outcome_comparison', {})}\n"
    )
    return _llm.generate(prompt)


def generate_recommendations(analysis_context: dict) -> str:
    """Generate recommended next steps based on analysis results."""
    prompt = (
        f"Based on the analysis results, recommend next steps.\n"
        f"Context: {analysis_context}\n"
    )
    return _llm.generate(prompt)
