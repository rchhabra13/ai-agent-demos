"""
FHIR R4 Patient Bundle parser.

Extracts a structured PatientProfile from a FHIR Bundle that may contain
Patient, Condition, MedicationRequest, Observation, and AllergyIntolerance
resources.  Designed to handle real-world messy FHIR — gracefully skips
resources it cannot parse rather than raising.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Any

import structlog

from clinical_trial_matchmaker.models.patient import (
    LabValue,
    Medication,
    PatientCondition,
    PatientProfile,
)

logger = structlog.get_logger(__name__)

# LOINC codes for common labs we specifically care about
_IMPORTANT_LOINC = {
    "718-7": "Hemoglobin",
    "2823-3": "Potassium",
    "2160-0": "Creatinine",
    "1742-6": "ALT",
    "1920-8": "AST",
    "6768-6": "Alkaline Phosphatase",
    "33914-3": "eGFR",
    "2532-0": "LDH",
    "35741-8": "Platelet count",
    "26515-7": "Platelet count",
    "6690-2": "WBC",
    "26464-8": "WBC",
    "10334-1": "ECOG Performance Status",
}


class FhirParser:
    """
    Converts a raw FHIR R4 Bundle (as a dict or JSON string) into a
    clean PatientProfile suitable for trial matching.
    """

    def parse(self, fhir_input: str | dict[str, Any]) -> PatientProfile:
        """
        Parse a FHIR Bundle and return a PatientProfile.

        Args:
            fhir_input: A FHIR R4 Bundle as a JSON string or already-parsed dict.

        Returns:
            PatientProfile with all extractable fields populated.

        Raises:
            ValueError: If the input is not a valid FHIR Bundle.
        """
        bundle = self._load(fhir_input)
        resources = self._extract_resources(bundle)

        patient_resource = self._find_first(resources, "Patient")
        if not patient_resource:
            raise ValueError("FHIR Bundle contains no Patient resource")

        profile = self._parse_patient(patient_resource)
        profile.conditions = self._parse_conditions(resources)
        profile.medications = self._parse_medications(resources)
        profile.lab_values, profile.ecog_performance_status = self._parse_observations(resources)
        profile.allergies = self._parse_allergies(resources)

        logger.info(
            "fhir_parsed",
            patient_id=profile.patient_id,
            conditions=len(profile.conditions),
            medications=len(profile.medications),
            labs=len(profile.lab_values),
        )
        return profile

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _load(fhir_input: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(fhir_input, str):
            try:
                data: dict[str, Any] = json.loads(fhir_input)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in FHIR input: {exc}") from exc
        else:
            data = fhir_input
        if data.get("resourceType") not in ("Bundle", "Patient"):
            raise ValueError(
                f"Expected resourceType 'Bundle' or 'Patient', got '{data.get('resourceType')}'"
            )
        return data

    @staticmethod
    def _extract_resources(bundle: dict[str, Any]) -> list[dict[str, Any]]:
        """Pull all resource objects out of a Bundle or return the resource itself."""
        if bundle.get("resourceType") == "Patient":
            return [bundle]
        entries: list[Any] = bundle.get("entry", [])
        return [e["resource"] for e in entries if "resource" in e]

    @staticmethod
    def _find_first(
        resources: list[dict[str, Any]], resource_type: str
    ) -> dict[str, Any] | None:
        return next((r for r in resources if r.get("resourceType") == resource_type), None)

    @staticmethod
    def _find_all(
        resources: list[dict[str, Any]], resource_type: str
    ) -> list[dict[str, Any]]:
        return [r for r in resources if r.get("resourceType") == resource_type]

    def _parse_patient(self, patient: dict[str, Any]) -> PatientProfile:
        patient_id = patient.get("id", "unknown")

        # Name
        given_name: str | None = None
        names = patient.get("name", [])
        if names:
            first_name_entry = names[0]
            given = first_name_entry.get("given", [])
            given_name = given[0] if given else first_name_entry.get("text")

        # Birth date
        birth_date: date | None = None
        if raw_bd := patient.get("birthDate"):
            try:
                birth_date = date.fromisoformat(raw_bd)
            except ValueError:
                logger.warning("unparseable_birth_date", value=raw_bd)

        # Gender
        raw_gender = patient.get("gender", "unknown").lower()
        gender_map = {"male": "male", "female": "female", "other": "other"}
        gender = gender_map.get(raw_gender, "unknown")

        # Address
        zip_code: str | None = None
        state: str | None = None
        country: str = "United States"
        addresses = patient.get("address", [])
        if addresses:
            addr = addresses[0]
            zip_code = addr.get("postalCode")
            state = addr.get("state")
            country = addr.get("country", "United States")

        return PatientProfile(
            patient_id=patient_id,
            given_name=given_name,
            birth_date=birth_date,
            gender=gender,  # type: ignore[arg-type]
            zip_code=zip_code,
            state=state,
            country=country,
        )

    def _parse_conditions(self, resources: list[dict[str, Any]]) -> list[PatientCondition]:
        conditions: list[PatientCondition] = []
        for cond in self._find_all(resources, "Condition"):
            try:
                conditions.append(self._parse_single_condition(cond))
            except Exception as exc:  # noqa: BLE001
                logger.warning("condition_parse_error", error=str(exc))
        return conditions

    @staticmethod
    def _parse_single_condition(cond: dict[str, Any]) -> PatientCondition:
        # Clinical status
        cs_coding = (
            cond.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "active")
        )
        clinical_status_map = {
            "active": "active", "recurrence": "recurrence", "relapse": "relapse",
            "inactive": "inactive", "remission": "remission", "resolved": "resolved",
        }
        clinical_status = clinical_status_map.get(cs_coding, "active")

        # Verification status
        vs_coding = (
            cond.get("verificationStatus", {}).get("coding", [{}])[0].get("code", "confirmed")
        )
        verification_map = {
            "confirmed": "confirmed", "provisional": "provisional",
            "differential": "differential", "refuted": "refuted", "unknown": "unknown",
        }
        verification_status = verification_map.get(vs_coding, "confirmed")

        # Condition name + codes
        code_obj = cond.get("code", {})
        coding_list = code_obj.get("coding", [])
        name = code_obj.get("text") or (coding_list[0].get("display") if coding_list else "Unknown condition")

        icd10_code: str | None = None
        snomed_code: str | None = None
        for coding in coding_list:
            system = coding.get("system", "")
            if "icd" in system.lower():
                icd10_code = coding.get("code")
            elif "snomed" in system.lower():
                snomed_code = coding.get("code")

        # Onset date
        onset_date: date | None = None
        if onset_str := cond.get("onsetDateTime") or cond.get("onsetPeriod", {}).get("start"):
            try:
                onset_date = datetime.fromisoformat(onset_str.replace("Z", "+00:00")).date()
            except ValueError:
                pass

        # Stage
        stage: str | None = None
        stage_list = cond.get("stage", [])
        if stage_list:
            stage_summary = stage_list[0].get("summary", {})
            stage = stage_summary.get("text") or (
                stage_summary.get("coding", [{}])[0].get("display")
            )

        return PatientCondition(
            name=name,
            icd10_code=icd10_code,
            snomed_code=snomed_code,
            clinical_status=clinical_status,  # type: ignore[arg-type]
            verification_status=verification_status,  # type: ignore[arg-type]
            onset_date=onset_date,
            stage=stage,
        )

    def _parse_medications(self, resources: list[dict[str, Any]]) -> list[Medication]:
        meds: list[Medication] = []
        for med_req in self._find_all(resources, "MedicationRequest"):
            try:
                meds.append(self._parse_single_medication(med_req))
            except Exception as exc:  # noqa: BLE001
                logger.warning("medication_parse_error", error=str(exc))
        return meds

    @staticmethod
    def _parse_single_medication(med_req: dict[str, Any]) -> Medication:
        status_raw = med_req.get("status", "active")
        status_map = {"active": "active", "stopped": "stopped", "on-hold": "on-hold", "completed": "completed"}
        status = status_map.get(status_raw, "active")

        # Medication name
        med_code = med_req.get("medicationCodeableConcept", {})
        coding_list = med_code.get("coding", [])
        name = (
            med_code.get("text")
            or (coding_list[0].get("display") if coding_list else None)
            or med_req.get("medicationReference", {}).get("display", "Unknown")
        )

        rxnorm: str | None = None
        for coding in coding_list:
            if "rxnorm" in coding.get("system", "").lower():
                rxnorm = coding.get("code")
                break

        # Dosage
        dosage_instructions = med_req.get("dosageInstruction", [])
        dosage: str | None = None
        if dosage_instructions:
            dosage = dosage_instructions[0].get("text")

        # Reason
        reason: str | None = None
        reasons = med_req.get("reasonCode", [])
        if reasons:
            reason = reasons[0].get("text") or (
                reasons[0].get("coding", [{}])[0].get("display")
            )

        return Medication(
            name=name,
            rxnorm_code=rxnorm,
            status=status,  # type: ignore[arg-type]
            dosage=dosage,
            reason=reason,
        )

    def _parse_observations(
        self, resources: list[dict[str, Any]]
    ) -> tuple[list[LabValue], int | None]:
        labs: list[LabValue] = []
        ecog: int | None = None

        for obs in self._find_all(resources, "Observation"):
            try:
                result = self._parse_single_observation(obs)
                if result is None:
                    continue
                if result[0] == "__ecog__":
                    ecog = int(result[1])
                else:
                    labs.append(result)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                logger.warning("observation_parse_error", error=str(exc))

        return labs, ecog

    def _parse_single_observation(
        self, obs: dict[str, Any]
    ) -> LabValue | tuple[str, Any] | None:
        code_obj = obs.get("code", {})
        coding_list = code_obj.get("coding", [])
        display = code_obj.get("text") or (coding_list[0].get("display") if coding_list else None)
        loinc_code: str | None = None

        for coding in coding_list:
            if "loinc" in coding.get("system", "").lower():
                loinc_code = coding.get("code")
                break

        # ECOG performance status
        if loinc_code == "10334-1" or (display and "ecog" in display.lower()):
            val = obs.get("valueInteger") or obs.get("valueQuantity", {}).get("value")
            if val is not None:
                return ("__ecog__", int(val))

        # Skip non-lab observations
        if not obs.get("valueQuantity"):
            return None

        # Only include labs we recognize or those matching important LOINC codes
        if loinc_code and loinc_code not in _IMPORTANT_LOINC and display is None:
            return None

        vq = obs["valueQuantity"]
        value: float | None = vq.get("value")
        if value is None:
            return None

        unit = vq.get("unit") or vq.get("code", "")
        name = (
            (_IMPORTANT_LOINC.get(loinc_code) if loinc_code else None)
            or display
            or "Lab Value"
        )

        # Reference range
        ref_range: str | None = None
        rr_list = obs.get("referenceRange", [])
        if rr_list:
            low = rr_list[0].get("low", {}).get("value")
            high = rr_list[0].get("high", {}).get("value")
            if low is not None and high is not None:
                ref_range = f"{low}-{high}"

        # Interpretation
        is_abnormal = False
        interp_list = obs.get("interpretation", [])
        if interp_list:
            interp_code = interp_list[0].get("coding", [{}])[0].get("code", "N")
            is_abnormal = interp_code not in ("N", "normal")

        # Effective date
        obs_date: date | None = None
        if eff_str := obs.get("effectiveDateTime"):
            try:
                obs_date = datetime.fromisoformat(eff_str.replace("Z", "+00:00")).date()
            except ValueError:
                pass

        return LabValue(
            name=name,
            loinc_code=loinc_code,
            value=float(value),
            unit=unit,
            reference_range=ref_range,
            date_recorded=obs_date,
            is_abnormal=is_abnormal,
        )

    def _parse_allergies(self, resources: list[dict[str, Any]]) -> list[str]:
        allergies: list[str] = []
        for allergy in self._find_all(resources, "AllergyIntolerance"):
            try:
                code_obj = allergy.get("code", {})
                name = code_obj.get("text") or (
                    code_obj.get("coding", [{}])[0].get("display")
                )
                if name:
                    allergies.append(name)
            except Exception as exc:  # noqa: BLE001
                logger.warning("allergy_parse_error", error=str(exc))
        return allergies

    @staticmethod
    def _extract_text_value(obj: dict[str, Any]) -> str | None:
        """Safely pull a display/text value from a FHIR CodeableConcept."""
        if text := obj.get("text"):
            return text
        coding = obj.get("coding", [])
        if coding:
            return coding[0].get("display")
        return None
