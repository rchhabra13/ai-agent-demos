"""
CLI Interface for Clinical Insights Assistant
==============================================
Command-line alternative to the Streamlit UI.
Usage: python src/ui/cli.py [command]
"""

import argparse
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_loader import load_data, validate_data, generate_synthetic_data
from src.issue_detection import run_all_detections
from src.cohort_analysis import run_full_cohort_analysis
from src.scenario_simulation import simulate_scenario
from src.genai_interface import (
    summarize_doctor_notes, generate_regulatory_summary,
    generate_recommendations
)
from src.agent.agent_core import ClinicalInsightsAgent


def load_dataset(data_path):
    """Load or generate dataset."""
    if os.path.exists(data_path):
        return load_data(data_path)
    print("Dataset not found. Generating synthetic data...")
    return generate_synthetic_data(output_path=data_path)


def cmd_validate(df):
    """Validate dataset."""
    result = validate_data(df)
    print("\n=== DATA VALIDATION ===")
    for k, v in result.items():
        print(f"  {k}: {v}")


def cmd_detect(df, args):
    """Run issue detection."""
    results = run_all_detections(df, args.compliance_threshold, args.z_threshold)
    print("\n=== ISSUE DETECTION REPORT ===")
    print(f"Total records: {results['summary']['total_records_analyzed']}")
    print(f"Total patients: {results['summary']['total_patients']}")
    print(f"Total issues: {results['summary']['total_issues_found']}")
    for key in ['non_compliance', 'adverse_events', 'outcome_anomalies',
                'dosage_anomalies', 'declining_patients']:
        r = results[key]
        print(f"\n  {key}:")
        print(f"    Issues: {r['count']}")
        print(f"    Patients affected: {r['patients_affected']}")


def cmd_cohort(df):
    """Run cohort comparison."""
    results = run_full_cohort_analysis(df)
    print("\n=== COHORT COMPARISON ===")
    print(results['cohort_stats'].to_string())
    print(f"\nOutcome comparison:")
    oc = results['outcome_comparison']
    print(f"  {oc['interpretation']}")


def cmd_simulate(df, args):
    """Run scenario simulation."""
    result = simulate_scenario(df, args.scenario_type,
                              new_dosage=args.dosage,
                              compliance_boost=args.compliance_boost)
    print(f"\n=== SCENARIO: {args.scenario_type} ===")
    if isinstance(result, dict):
        for k, v in result.items():
            if k != 'data':
                print(f"  {k}: {v}")


def cmd_summarize(df, args):
    """Generate GenAI summaries."""
    if args.summary_type == 'notes':
        print(summarize_doctor_notes(df))
    elif args.summary_type == 'regulatory':
        print(generate_regulatory_summary(df))
    elif args.summary_type == 'recommendations':
        print(generate_recommendations({'source': 'cli'}))


def cmd_agent(df):
    """Run the autonomous agent."""
    agent = ClinicalInsightsAgent(df, verbose=True)
    report = agent.run()
    print(f"\nAgent completed {report['summary']['num_reasoning_steps']} steps.")
    print(f"Results: {report['summary']['result_keys']}")


def main():
    parser = argparse.ArgumentParser(description="Clinical Insights Assistant CLI")
    parser.add_argument('--data', default='data/clinical_trial_data.csv',
                       help='Path to CSV data file')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    subparsers.add_parser('validate', help='Validate dataset')

    detect_parser = subparsers.add_parser('detect', help='Run issue detection')
    detect_parser.add_argument('--compliance-threshold', type=float, default=75.0)
    detect_parser.add_argument('--z-threshold', type=float, default=2.0)

    subparsers.add_parser('cohort', help='Run cohort comparison')

    sim_parser = subparsers.add_parser('simulate', help='Run scenario simulation')
    sim_parser.add_argument('--scenario-type', default='sensitivity_analysis',
                           choices=['dosage_change', 'compliance_intervention', 'sensitivity_analysis'])
    sim_parser.add_argument('--dosage', type=int, default=75)
    sim_parser.add_argument('--compliance-boost', type=float, default=10.0)

    sum_parser = subparsers.add_parser('summarize', help='Generate GenAI summary')
    sum_parser.add_argument('--summary-type', default='notes',
                           choices=['notes', 'regulatory', 'recommendations'])

    subparsers.add_parser('agent', help='Run autonomous agent')

    args = parser.parse_args()

    df = load_dataset(args.data)

    if args.command == 'validate':
        cmd_validate(df)
    elif args.command == 'detect':
        cmd_detect(df, args)
    elif args.command == 'cohort':
        cmd_cohort(df)
    elif args.command == 'simulate':
        cmd_simulate(df, args)
    elif args.command == 'summarize':
        cmd_summarize(df, args)
    elif args.command == 'agent':
        cmd_agent(df)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
