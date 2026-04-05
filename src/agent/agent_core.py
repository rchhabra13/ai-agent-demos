"""
Agent Core Module
=================
Implements the agentic AI loop using a ReAct-style (Reason + Act) pattern.
The agent autonomously explores data, runs analyses, and recommends next steps.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
from typing import Optional, Callable
from src.agent.memory import SessionMemory
from src.issue_detection import run_all_detections
from src.cohort_analysis import run_full_cohort_analysis
from src.scenario_simulation import simulate_scenario
from src.genai_interface import (
    summarize_doctor_notes,
    generate_regulatory_summary,
    generate_recommendations,
    generate_cohort_narrative,
    summarize_scenario_results,
    get_llm
)


class ClinicalInsightsAgent:
    """
    An autonomous agent that reasons about clinical trial data,
    selects appropriate tools, and generates insights.

    Uses a ReAct-style loop:
    1. THINK: Reason about what to do next
    2. ACT: Execute a tool/analysis
    3. OBSERVE: Record the result
    4. REPEAT until the task is complete
    """

    AVAILABLE_TOOLS = {
        'detect_issues': 'Run issue detection (non-compliance, adverse events, anomalies)',
        'compare_cohorts': 'Compare outcomes between patient cohorts',
        'simulate_dosage': 'Simulate dosage change scenarios',
        'simulate_compliance': 'Simulate compliance intervention',
        'sensitivity_analysis': 'Run dosage sensitivity analysis',
        'summarize_notes': 'Summarize doctor notes using GenAI',
        'regulatory_summary': 'Generate FDA-style regulatory summary',
        'recommend_actions': 'Generate recommended next steps',
        'patient_lookup': 'Look up a specific patient\'s data',
    }

    def __init__(self, df: pd.DataFrame, verbose: bool = True):
        """
        Initialize the agent with clinical trial data.

        Parameters
        ----------
        df : pd.DataFrame
            Clinical trial dataset.
        verbose : bool
            Whether to print reasoning steps.
        """
        self.df = df
        self.memory = SessionMemory()
        self.verbose = verbose
        self.max_steps = 10
        self.llm = get_llm()

    def _log(self, message: str):
        """Log a message if verbose mode is on."""
        if self.verbose:
            print(message)

    def _think(self, task: str, step: int) -> tuple:
        """
        Reasoning step: decide what tool to use next.

        Returns (thought, tool_name, tool_params)
        """
        completed = self.memory.analysis.results.keys()

        # Planning logic based on task and completed analyses
        if 'detect_issues' not in completed:
            thought = "I should start by detecting issues in the data to understand the landscape."
            return thought, 'detect_issues', {}

        if 'compare_cohorts' not in completed:
            thought = "Now I should compare cohorts to understand differential outcomes."
            return thought, 'compare_cohorts', {}

        if 'summarize_notes' not in completed:
            thought = "Let me summarize the doctor notes to extract qualitative insights."
            return thought, 'summarize_notes', {}

        if 'sensitivity_analysis' not in completed:
            thought = "I should run a dosage sensitivity analysis to explore optimal dosing."
            return thought, 'sensitivity_analysis', {}

        if 'regulatory_summary' not in completed:
            thought = "Now I have enough data to generate a regulatory summary."
            return thought, 'regulatory_summary', {}

        if 'recommendations' not in completed:
            thought = "Finally, let me generate actionable recommendations based on all findings."
            return thought, 'recommend_actions', {}

        return "All primary analyses are complete.", 'done', {}

    def _act(self, tool_name: str, params: dict) -> str:
        """Execute a tool and return the observation."""
        try:
            if tool_name == 'detect_issues':
                result = run_all_detections(self.df)
                summary = result['summary']
                self.memory.analysis.store_result('detect_issues', result)
                return (
                    f"Issue detection complete. Analyzed {summary['total_records_analyzed']} records "
                    f"across {summary['total_patients']} patients. "
                    f"Found {summary['total_issues_found']} total issues."
                )

            elif tool_name == 'compare_cohorts':
                result = run_full_cohort_analysis(self.df)
                self.memory.analysis.store_result('compare_cohorts', result)
                outcome = result['outcome_comparison']
                return (
                    f"Cohort comparison complete. "
                    f"Mean outcome A: {outcome['mean_a']}, B: {outcome['mean_b']}. "
                    f"P-value: {outcome['p_value']}. {outcome['interpretation']}"
                )

            elif tool_name == 'summarize_notes':
                result = summarize_doctor_notes(self.df)
                self.memory.analysis.store_result('summarize_notes', result)
                return f"Doctor notes summarized. Key themes extracted."

            elif tool_name == 'simulate_dosage':
                new_dosage = params.get('new_dosage', 75)
                result = simulate_scenario(
                    self.df, 'dosage_change', new_dosage=new_dosage
                )
                self.memory.analysis.store_result(f'simulate_dosage_{new_dosage}', result)
                return (
                    f"Dosage simulation complete for {new_dosage}mg. "
                    f"Mean change: {result['summary']['mean_outcome_change']} points."
                )

            elif tool_name == 'simulate_compliance':
                boost = params.get('compliance_boost', 10.0)
                result = simulate_scenario(
                    self.df, 'compliance_intervention', compliance_boost=boost
                )
                self.memory.analysis.store_result('simulate_compliance', result)
                return f"Compliance intervention simulated. {result.get('interpretation', '')}"

            elif tool_name == 'sensitivity_analysis':
                result = simulate_scenario(self.df, 'sensitivity_analysis')
                self.memory.analysis.store_result('sensitivity_analysis', result)
                return (
                    f"Sensitivity analysis complete. "
                    f"Optimal dosage: {result['optimal_dosage']}mg."
                )

            elif tool_name == 'regulatory_summary':
                detection = self.memory.analysis.get_result('detect_issues')
                cohort = self.memory.analysis.get_result('compare_cohorts')
                result = generate_regulatory_summary(self.df, cohort, detection)
                self.memory.analysis.store_result('regulatory_summary', result)
                return "Regulatory summary generated."

            elif tool_name == 'recommend_actions':
                context = self.memory.analysis.get_summary()
                result = generate_recommendations(context)
                self.memory.analysis.store_result('recommendations', result)
                return "Recommendations generated based on all analyses."

            elif tool_name == 'patient_lookup':
                patient_id = params.get('patient_id', 'P001')
                from src.data_loader import get_patient_summary
                result = get_patient_summary(self.df, patient_id)
                self.memory.analysis.store_result(f'patient_{patient_id}', result)
                return f"Patient {patient_id} data retrieved: {result}"

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def run(self, task: str = "Perform a comprehensive analysis of the clinical trial data.") -> dict:
        """
        Execute the agent loop.

        Parameters
        ----------
        task : str
            The task/query for the agent to address.

        Returns
        -------
        dict
            Complete results from the agent's analysis.
        """
        self._log(f"\n{'='*60}")
        self._log(f"AGENT TASK: {task}")
        self._log(f"{'='*60}\n")

        self.memory.conversation.add_message('user', task)

        for step in range(1, self.max_steps + 1):
            # THINK
            thought, tool_name, params = self._think(task, step)

            if tool_name == 'done':
                self._log(f"\nStep {step} - THINK: {thought}")
                self._log("Agent loop complete.\n")
                break

            self._log(f"\nStep {step} - THINK: {thought}")
            self._log(f"Step {step} - ACT: {tool_name}({params})")

            # ACT
            observation = self._act(tool_name, params)

            self._log(f"Step {step} - OBSERVE: {observation}")

            # Record reasoning
            self.memory.analysis.add_reasoning_step(thought, tool_name, observation)

        # Compile final report
        report = self._compile_report()
        self.memory.conversation.add_message('agent', 'Analysis complete. Report generated.')

        return report

    def _compile_report(self) -> dict:
        """Compile all analysis results into a final report."""
        return {
            'session_id': self.memory.session_id,
            'reasoning_trace': self.memory.analysis.get_reasoning_trace(),
            'results': {
                key: val['value']
                for key, val in self.memory.analysis.results.items()
            },
            'summary': self.memory.analysis.get_summary()
        }

    def ask(self, question: str) -> str:
        """
        Ask the agent a specific question about the data.

        Parameters
        ----------
        question : str
            Natural language question.

        Returns
        -------
        str
            Agent's response.
        """
        self.memory.conversation.add_message('user', question)

        # Route to appropriate tool based on question
        q_lower = question.lower()

        if 'patient' in q_lower and any(f'p{i:03d}' in q_lower for i in range(1, 201)):
            # Extract patient ID
            import re
            match = re.search(r'p\d{3}', q_lower)
            if match:
                pid = match.group().upper()
                obs = self._act('patient_lookup', {'patient_id': pid})
                response = f"Here's what I found about patient {pid}:\n{obs}"
        elif 'adverse' in q_lower or 'side effect' in q_lower:
            if not self.memory.analysis.has_result('detect_issues'):
                self._act('detect_issues', {})
            result = self.memory.analysis.get_result('detect_issues')
            ae_count = result['adverse_events']['count']
            ae_patients = result['adverse_events']['patients_affected']
            response = (
                f"Adverse event analysis: {ae_count} adverse events detected "
                f"affecting {ae_patients} patients."
            )
        elif 'cohort' in q_lower or 'compare' in q_lower:
            if not self.memory.analysis.has_result('compare_cohorts'):
                self._act('compare_cohorts', {})
            result = self.memory.analysis.get_result('compare_cohorts')
            response = generate_cohort_narrative(result)
        elif 'dosage' in q_lower or 'dose' in q_lower:
            obs = self._act('sensitivity_analysis', {})
            response = f"Dosage analysis results: {obs}"
        elif 'regulatory' in q_lower or 'fda' in q_lower:
            obs = self._act('regulatory_summary', {})
            result = self.memory.analysis.get_result('regulatory_summary')
            response = result if isinstance(result, str) else str(result)
        else:
            response = self.llm.generate(question)

        self.memory.conversation.add_message('agent', response)
        return response
