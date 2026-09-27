"""
Streamlit UI for Clinical Insights Assistant
=============================================
Interactive web interface for analyzing clinical trial data.
Run with: streamlit run src/ui/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_loader import load_data, validate_data, get_patient_summary, generate_synthetic_data
from src.issue_detection import run_all_detections, detect_non_compliance, detect_adverse_events
from src.cohort_analysis import run_full_cohort_analysis, compute_cohort_stats
from src.scenario_simulation import (
    simulate_dosage_change, simulate_compliance_intervention,
    run_dosage_sensitivity_analysis
)
from src.genai_interface import (
    summarize_doctor_notes, generate_regulatory_summary,
    generate_recommendations, generate_cohort_narrative
)
from src.agent.agent_core import ClinicalInsightsAgent


# Page config
st.set_page_config(
    page_title="Clinical Insights Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_or_generate_data():
    """Load data, generating if necessary."""
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'clinical_trial_data.csv')
    if os.path.exists(data_path):
        return load_data(data_path)
    else:
        df = generate_synthetic_data(output_path=data_path)
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        return df


def main():
    # Sidebar navigation
    st.sidebar.title("🏥 Clinical Insights Assistant")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate to:",
        [
            "📊 Dashboard",
            "🔍 Issue Detection",
            "📈 Cohort Comparison",
            "🧪 Scenario Simulation",
            "🤖 GenAI Summaries",
            "🧠 Agentic AI",
            "👤 Patient Lookup"
        ]
    )

    # Load data
    df = load_or_generate_data()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Dataset:** {len(df):,} records")
    st.sidebar.markdown(f"**Patients:** {df['patient_id'].nunique()}")
    st.sidebar.markdown(f"**Cohorts:** {', '.join(sorted(df['cohort'].unique()))}")

    # Route to page
    if page == "📊 Dashboard":
        render_dashboard(df)
    elif page == "🔍 Issue Detection":
        render_issue_detection(df)
    elif page == "📈 Cohort Comparison":
        render_cohort_comparison(df)
    elif page == "🧪 Scenario Simulation":
        render_scenario_simulation(df)
    elif page == "🤖 GenAI Summaries":
        render_genai_summaries(df)
    elif page == "🧠 Agentic AI":
        render_agentic_ai(df)
    elif page == "👤 Patient Lookup":
        render_patient_lookup(df)


def render_dashboard(df):
    """Main dashboard with KPIs and overview charts."""
    st.title("📊 Clinical Trial Dashboard")

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients", df['patient_id'].nunique())
    with col2:
        st.metric("Mean Outcome", f"{df['outcome_score'].mean():.1f}")
    with col3:
        st.metric("Adverse Event Rate", f"{df['adverse_event_flag'].mean():.1%}")
    with col4:
        st.metric("Mean Compliance", f"{df['compliance_pct'].mean():.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x='outcome_score', nbins=50, color='cohort',
                          title='Outcome Score Distribution by Cohort',
                          barmode='overlay', opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        trends = df.groupby(['trial_day', 'cohort'])['outcome_score'].mean().reset_index()
        fig = px.line(trends, x='trial_day', y='outcome_score', color='cohort',
                     title='Mean Outcome Score Over Time')
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(df, x='dosage_mg', y='outcome_score', color='cohort',
                    title='Outcome by Dosage and Cohort')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        notes_freq = df['doctor_notes'].value_counts().reset_index()
        notes_freq.columns = ['note', 'count']
        fig = px.bar(notes_freq, x='count', y='note', orientation='h',
                    title='Doctor Notes Frequency')
        st.plotly_chart(fig, use_container_width=True)


def render_issue_detection(df):
    """Issue detection page."""
    st.title("🔍 Issue Detection")

    col1, col2 = st.columns(2)
    with col1:
        compliance_threshold = st.slider("Compliance Threshold (%)", 50, 95, 75)
    with col2:
        z_threshold = st.slider("Anomaly Z-Score Threshold", 1.0, 4.0, 2.0, 0.1)

    if st.button("Run Detection", type="primary"):
        with st.spinner("Running issue detection..."):
            results = run_all_detections(df, compliance_threshold, z_threshold)

        # Summary metrics
        st.markdown("### Detection Summary")
        cols = st.columns(5)
        labels = ['Non-Compliance', 'Adverse Events', 'Outcome Anomalies', 'Dosage Issues', 'Declining Patients']
        keys = ['non_compliance', 'adverse_events', 'outcome_anomalies', 'dosage_anomalies', 'declining_patients']
        for col, label, key in zip(cols, labels, keys):
            with col:
                st.metric(label, results[key]['count'],
                         delta=f"{results[key]['patients_affected']} patients")

        st.markdown("---")

        # Non-compliance details
        st.subheader("Non-Compliance Details")
        nc = results['non_compliance']['data']
        if len(nc) > 0:
            fig = px.histogram(nc, x='compliance_pct', color='severity',
                             title='Non-Compliant Records by Severity')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(nc[['patient_id', 'trial_day', 'compliance_pct', 'outcome_score', 'severity']].head(20))
        else:
            st.info("No non-compliance issues detected.")

        # Adverse events
        st.subheader("Adverse Events")
        ae = results['adverse_events']['data']
        if len(ae) > 0:
            fig = px.scatter(ae, x='trial_day', y='outcome_score', color='severity',
                           hover_data=['patient_id', 'doctor_notes'],
                           title='Adverse Events: Outcome Score vs Trial Day')
            st.plotly_chart(fig, use_container_width=True)


def render_cohort_comparison(df):
    """Cohort comparison page."""
    st.title("📈 Cohort Comparison")

    if st.button("Run Cohort Analysis", type="primary"):
        with st.spinner("Running analysis..."):
            results = run_full_cohort_analysis(df)

        # Stats table
        st.subheader("Cohort Statistics")
        st.dataframe(results['cohort_stats'])

        # Outcome comparison
        st.subheader("Outcome Score Comparison")
        oc = results['outcome_comparison']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Mean Cohort {oc['cohort_a']}", f"{oc['mean_a']:.2f}")
        with col2:
            st.metric(f"Mean Cohort {oc['cohort_b']}", f"{oc['mean_b']:.2f}")
        with col3:
            st.metric("P-Value", f"{oc['p_value']:.6f}")

        st.info(oc['interpretation'])

        # Visualizations
        col1, col2 = st.columns(2)
        with col1:
            fig = px.violin(df, x='cohort', y='outcome_score', color='cohort',
                          title='Outcome Distribution by Cohort', box=True)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            trends = results['trends']
            fig = px.line(trends, x='trial_day', y='mean_outcome', color='cohort',
                        title='Mean Outcome Trend by Cohort')
            st.plotly_chart(fig, use_container_width=True)

        # Adverse event comparison
        st.subheader("Adverse Event Rate Comparison")
        aec = results['adverse_event_comparison']
        st.write(f"Rate Cohort A: {aec['rate_a']:.2%} | Rate Cohort B: {aec['rate_b']:.2%}")
        st.write(f"Chi-squared: {aec['chi2_statistic']:.4f} | P-value: {aec['p_value']:.6f}")

        # GenAI narrative
        st.subheader("AI-Generated Cohort Narrative")
        narrative = generate_cohort_narrative(results)
        st.markdown(narrative)


def render_scenario_simulation(df):
    """Scenario simulation page."""
    st.title("🧪 Scenario Simulation")

    tab1, tab2, tab3 = st.tabs(["Dosage Change", "Compliance Intervention", "Sensitivity Analysis"])

    with tab1:
        st.subheader("Dosage Change Simulation")
        col1, col2 = st.columns(2)
        with col1:
            new_dosage = st.selectbox("New Dosage (mg)", [25, 50, 75, 100, 125, 150])
        with col2:
            patient = st.text_input("Patient ID (leave empty for all)", "")

        if st.button("Simulate Dosage Change", type="primary"):
            with st.spinner("Simulating..."):
                pid = patient if patient else None
                sim = simulate_dosage_change(df, patient_id=pid, new_dosage=new_dosage)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Outcome Change", f"{sim['outcome_change'].mean():.2f}")
            with col2:
                st.metric("Patients Improved", f"{(sim['outcome_change'] > 0).sum()}")
            with col3:
                st.metric("Patients Declined", f"{(sim['outcome_change'] < 0).sum()}")

            fig = px.histogram(sim, x='outcome_change', nbins=50,
                             title=f'Outcome Change Distribution ({new_dosage}mg)')
            fig.add_vline(x=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Compliance Intervention")
        boost = st.slider("Compliance Boost (%)", 1.0, 25.0, 10.0, 0.5)

        if st.button("Simulate Intervention", type="primary"):
            with st.spinner("Simulating..."):
                result = simulate_compliance_intervention(df, compliance_boost=boost)

            st.write(result['interpretation'])

            if result['before']:
                fig = go.Figure(data=[
                    go.Bar(name='Before', x=['Compliance', 'Outcome'],
                           y=[result['before']['mean_compliance'], result['before']['mean_outcome']]),
                    go.Bar(name='After', x=['Compliance', 'Outcome'],
                           y=[result['after']['mean_compliance'], result['after']['mean_outcome']])
                ])
                fig.update_layout(barmode='group', title='Before vs After Intervention')
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Dosage Sensitivity Analysis")
        if st.button("Run Sensitivity Analysis", type="primary"):
            with st.spinner("Running..."):
                sensitivity = run_dosage_sensitivity_analysis(df)

            st.dataframe(sensitivity)

            fig = px.line(sensitivity, x='dosage_mg', y='mean_projected_outcome',
                        title='Dosage vs Projected Outcome',
                        markers=True)
            st.plotly_chart(fig, use_container_width=True)


def render_genai_summaries(df):
    """GenAI summaries page."""
    st.title("🤖 GenAI Summaries")

    summary_type = st.selectbox("Select Summary Type", [
        "Doctor Notes Summary",
        "Regulatory Summary (FDA-Style)",
        "Recommended Next Steps"
    ])

    if st.button("Generate Summary", type="primary"):
        with st.spinner("Generating summary..."):
            if summary_type == "Doctor Notes Summary":
                result = summarize_doctor_notes(df)
            elif summary_type == "Regulatory Summary (FDA-Style)":
                result = generate_regulatory_summary(df)
            else:
                detection = run_all_detections(df)
                context = {'total_issues': detection['summary']['total_issues_found']}
                result = generate_recommendations(context)

        st.markdown(result)
        st.download_button(
            label="Download Summary",
            data=result,
            file_name=f"{summary_type.lower().replace(' ', '_')}.md",
            mime="text/markdown"
        )


def render_agentic_ai(df):
    """Agentic AI page."""
    st.title("🧠 Agentic AI Loop")
    st.markdown("The agent autonomously explores data, runs analyses, and recommends actions.")

    if st.button("Run Autonomous Analysis", type="primary"):
        with st.spinner("Agent is thinking and analyzing..."):
            agent = ClinicalInsightsAgent(df, verbose=False)
            report = agent.run()

        st.success(f"Agent completed {report['summary']['num_reasoning_steps']} reasoning steps!")

        # Show reasoning trace
        st.subheader("Reasoning Trace")
        for step in report['reasoning_trace']:
            with st.expander(f"Step {step['step']}: {step['action']}"):
                st.write(f"**Thought:** {step['thought']}")
                st.write(f"**Action:** {step['action']}")
                st.write(f"**Observation:** {step['observation']}")

        # Results
        st.subheader("Analysis Results")
        st.write(f"Results stored: {report['summary']['result_keys']}")

    st.markdown("---")
    st.subheader("Ask the Agent")
    question = st.text_input("Ask a question about the trial data:")
    if question:
        with st.spinner("Agent is thinking..."):
            agent = ClinicalInsightsAgent(df, verbose=False)
            answer = agent.ask(question)
        st.markdown(answer)


def render_patient_lookup(df):
    """Patient lookup page."""
    st.title("👤 Patient Lookup")

    patient_ids = sorted(df['patient_id'].unique())
    selected = st.selectbox("Select Patient", patient_ids)

    if selected:
        summary = get_patient_summary(df, selected)
        patient_df = df[df['patient_id'] == selected]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cohort", summary['cohort'])
        with col2:
            st.metric("Avg Compliance", f"{summary['avg_compliance']}%")
        with col3:
            st.metric("Avg Outcome", f"{summary['avg_outcome']}")
        with col4:
            st.metric("Adverse Events", summary['total_adverse_events'])

        # Outcome trend
        fig = px.line(patient_df, x='trial_day', y='outcome_score',
                     title=f'Outcome Score Over Time - {selected}',
                     markers=True)
        fig.add_hline(y=patient_df['outcome_score'].mean(), line_dash="dash",
                     annotation_text="Mean")
        st.plotly_chart(fig, use_container_width=True)

        # Compliance trend
        fig = px.line(patient_df, x='trial_day', y='compliance_pct',
                     title=f'Compliance Over Time - {selected}',
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Visit log
        st.subheader("Visit Log")
        st.dataframe(patient_df[['trial_day', 'dosage_mg', 'compliance_pct',
                                  'adverse_event_flag', 'doctor_notes', 'outcome_score']])


if __name__ == "__main__":
    main()
