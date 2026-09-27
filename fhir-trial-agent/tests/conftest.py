"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from clinical_trial_matchmaker.config import Settings
from clinical_trial_matchmaker.models.patient import PatientProfile, PatientCondition, Medication, LabValue
from clinical_trial_matchmaker.models.trial import EligibilityAssessment, TrialDetail, TrialStatus

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_fhir_bundle_str() -> str:
    return (FIXTURES_DIR / "sample_patient.json").read_text()


@pytest.fixture()
def sample_fhir_bundle(sample_fhir_bundle_str: str) -> dict:
    return json.loads(sample_fhir_bundle_str)


@pytest.fixture()
def test_settings() -> Settings:
    return Settings(
        anthropic_api_key="sk-ant-test-key",
        llm_model="claude-haiku-4-5-20251001",
        environment="development",
        log_level="DEBUG",
    )


@pytest.fixture()
def sample_patient_profile() -> PatientProfile:
    from datetime import date
    return PatientProfile(
        patient_id="patient-001",
        given_name="Maria",
        birth_date=date(1968, 4, 15),
        gender="female",
        zip_code="44106",
        state="OH",
        country="United States",
        conditions=[
            PatientCondition(
                name="Non-small cell lung cancer",
                icd10_code="C34.10",
                clinical_status="active",
                stage="Stage IIIA",
            )
        ],
        medications=[
            Medication(name="Pembrolizumab", status="active", dosage="200mg IV every 3 weeks")
        ],
        lab_values=[
            LabValue(name="Hemoglobin", loinc_code="718-7", value=10.8, unit="g/dL", is_abnormal=True)
        ],
        ecog_performance_status=1,
    )


@pytest.fixture()
def sample_trial_detail() -> TrialDetail:
    return TrialDetail(
        nct_id="NCT04513847",
        title="A Study of Pembrolizumab in Combination With Chemotherapy in NSCLC",
        status=TrialStatus.RECRUITING,
        phases=["PHASE3"],
        sponsor="Merck Sharp & Dohme LLC",
        brief_summary="This trial evaluates pembrolizumab plus chemotherapy in stage III NSCLC.",
        eligibility_criteria_raw=(
            "Inclusion Criteria:\n"
            "- Stage IIIA non-small cell lung cancer\n"
            "- ECOG performance status 0-1\n"
            "- Age >= 18 years\n\n"
            "Exclusion Criteria:\n"
            "- Prior anti-PD-1 therapy\n"
            "- Active autoimmune disease"
        ),
        minimum_age="18 Years",
        sex="ALL",
    )


@pytest.fixture()
def sample_eligibility_assessment() -> EligibilityAssessment:
    return EligibilityAssessment(
        nct_id="NCT04513847",
        trial_title="A Study of Pembrolizumab in Combination With Chemotherapy in NSCLC",
        eligibility_score=82,
        likely_eligible=True,
        key_matches=["Stage IIIA NSCLC", "ECOG 1", "Age 56"],
        key_concerns=["Already on pembrolizumab monotherapy — check if combination permitted"],
        missing_information=["PD-L1 expression status not documented"],
        recommendation="Strong candidate — confirm PD-L1 status and prior pembrolizumab dose history.",
        phase="PHASE3",
        status="RECRUITING",
        sponsor="Merck",
    )


@pytest.fixture()
def mock_ctgov_studies() -> list[dict]:
    """Minimal ClinicalTrials.gov API v2 study response."""
    return [
        {
            "protocolSection": {
                "identificationModule": {
                    "nctId": "NCT04513847",
                    "briefTitle": "Pembrolizumab + Chemotherapy in Stage III NSCLC",
                },
                "statusModule": {"overallStatus": "RECRUITING"},
                "designModule": {"phases": ["PHASE3"], "studyType": "INTERVENTIONAL"},
                "eligibilityModule": {
                    "eligibilityCriteria": "Inclusion:\n- Stage III NSCLC\n- ECOG 0-1\nExclusion:\n- Prior PD-1 therapy",
                    "minimumAge": "18 Years",
                    "maximumAge": "N/A",
                    "sex": "ALL",
                },
                "descriptionModule": {"briefSummary": "Phase 3 trial of pembro + chemo in NSCLC."},
                "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Merck"}},
            }
        }
    ]
