"""Tests for the FHIR R4 patient bundle parser."""

from __future__ import annotations

import json
from datetime import date

import pytest

from clinical_trial_matchmaker.services.fhir_parser import FhirParser


class TestFhirParser:
    parser = FhirParser()

    def test_parse_full_bundle(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)

        assert profile.patient_id == "patient-001"
        assert profile.given_name == "Maria"
        assert profile.birth_date == date(1968, 4, 15)
        assert profile.gender == "female"
        assert profile.zip_code == "44106"
        assert profile.state == "OH"

    def test_age_computed(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)
        assert profile.age is not None
        assert 50 < profile.age < 70  # Born 1968

    def test_conditions_parsed(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)

        assert len(profile.conditions) == 2
        nsclc = next(c for c in profile.conditions if "lung" in c.name.lower())
        assert nsclc.clinical_status == "active"
        assert nsclc.icd10_code == "C34.10"
        assert nsclc.stage == "Stage IIIA"

    def test_active_condition_names(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)
        active = profile.active_condition_names
        assert "Non-small cell lung cancer" in active
        # Diabetes is inactive — should not appear
        assert not any("diabetes" in c.lower() for c in active)

    def test_medications_parsed(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)

        assert len(profile.medications) == 1
        pembro = profile.medications[0]
        assert pembro.name == "Pembrolizumab"
        assert pembro.status == "active"
        assert "200mg" in (pembro.dosage or "")

    def test_lab_values_parsed(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)

        hgb = next((lv for lv in profile.lab_values if lv.loinc_code == "718-7"), None)
        assert hgb is not None
        assert hgb.value == 10.8
        assert hgb.unit == "g/dL"
        assert hgb.is_abnormal is True

    def test_ecog_parsed(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)
        assert profile.ecog_performance_status == 1

    def test_accepts_dict_input(self, sample_fhir_bundle: dict) -> None:
        profile = self.parser.parse(sample_fhir_bundle)
        assert profile.patient_id == "patient-001"

    def test_rejects_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            self.parser.parse("not json at all {{{")

    def test_rejects_wrong_resource_type(self) -> None:
        with pytest.raises(ValueError, match="resourceType"):
            self.parser.parse(json.dumps({"resourceType": "Observation", "id": "obs-1"}))

    def test_rejects_bundle_without_patient(self) -> None:
        bundle = {"resourceType": "Bundle", "type": "searchset", "entry": []}
        with pytest.raises(ValueError, match="no Patient resource"):
            self.parser.parse(bundle)

    def test_to_matching_summary(self, sample_fhir_bundle_str: str) -> None:
        profile = self.parser.parse(sample_fhir_bundle_str)
        summary = profile.to_matching_summary()

        assert "female" in summary
        assert "Non-small cell lung cancer" in summary
        assert "Pembrolizumab" in summary
        assert "Hemoglobin" in summary
        assert "ECOG" in summary

    def test_minimal_patient_bundle(self) -> None:
        """Parser should succeed with just a Patient resource."""
        minimal = {
            "resourceType": "Patient",
            "id": "min-001",
            "gender": "male",
            "birthDate": "1980-01-01",
        }
        profile = self.parser.parse(minimal)
        assert profile.patient_id == "min-001"
        assert profile.gender == "male"
        assert profile.conditions == []
        assert profile.medications == []
