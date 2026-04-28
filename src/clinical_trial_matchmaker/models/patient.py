"""FHIR-derived patient profile models."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class LabValue(BaseModel):
    """A single laboratory observation."""

    name: str = Field(description="Human-readable lab test name, e.g. 'Hemoglobin'")
    loinc_code: str | None = Field(default=None, description="LOINC code if available")
    value: float = Field(description="Numeric result value")
    unit: str = Field(description="Unit of measure, e.g. 'g/dL'")
    reference_range: str | None = Field(default=None, description="Normal range string, e.g. '13.5-17.5'")
    date_recorded: date | None = Field(default=None)
    is_abnormal: bool = Field(default=False)


class Medication(BaseModel):
    """An active or recent medication."""

    name: str = Field(description="Medication name (generic preferred)")
    rxnorm_code: str | None = Field(default=None)
    status: Literal["active", "stopped", "on-hold", "completed"] = Field(default="active")
    dosage: str | None = Field(default=None, description="Dosage string, e.g. '500mg twice daily'")
    reason: str | None = Field(default=None, description="Indication for the medication")


class PatientCondition(BaseModel):
    """A clinical condition / diagnosis."""

    name: str = Field(description="Condition display name, e.g. 'Non-small cell lung cancer'")
    icd10_code: str | None = Field(default=None)
    snomed_code: str | None = Field(default=None)
    clinical_status: Literal["active", "recurrence", "relapse", "inactive", "remission", "resolved"] = (
        Field(default="active")
    )
    verification_status: Literal["confirmed", "provisional", "differential", "refuted", "unknown"] = (
        Field(default="confirmed")
    )
    onset_date: date | None = Field(default=None)
    stage: str | None = Field(default=None, description="Disease stage if documented, e.g. 'Stage III'")


class PatientProfile(BaseModel):
    """
    Structured patient profile extracted from a FHIR R4 Patient bundle.
    Contains only the clinical attributes relevant for trial matching.
    """

    # Identity (de-identified for matching purposes)
    patient_id: str = Field(description="FHIR Patient resource ID")
    given_name: str | None = Field(default=None, description="First name for display only")
    birth_date: date | None = Field(default=None)
    gender: Literal["male", "female", "other", "unknown"] = Field(default="unknown")

    # Location
    zip_code: str | None = Field(default=None, description="For geographic trial proximity filtering")
    state: str | None = Field(default=None)
    country: str = Field(default="United States")

    # Clinical data
    conditions: list[PatientCondition] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    lab_values: list[LabValue] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list, description="Known allergy names")

    # Functional status
    ecog_performance_status: int | None = Field(
        default=None,
        ge=0,
        le=4,
        description="ECOG performance status 0-4",
    )
    karnofsky_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Karnofsky performance score 0-100",
    )

    # Clinical history flags (extracted by LLM from notes)
    prior_cancer_treatment: bool | None = Field(default=None)
    prior_radiation: bool | None = Field(default=None)
    prior_surgery: bool | None = Field(default=None)
    pregnant_or_breastfeeding: bool | None = Field(default=None)
    organ_transplant_history: bool | None = Field(default=None)
    autoimmune_disease: bool | None = Field(default=None)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def age(self) -> int | None:
        """Derive current age from birth date."""
        if self.birth_date is None:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_condition_names(self) -> list[str]:
        """Return names of all active/current conditions."""
        return [
            c.name
            for c in self.conditions
            if c.clinical_status in ("active", "recurrence", "relapse")
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_medication_names(self) -> list[str]:
        """Return names of all active medications."""
        return [m.name for m in self.medications if m.status == "active"]

    def to_matching_summary(self) -> str:
        """
        Produce a plain-text clinical summary for use as LLM context.
        Omits PII — uses age bucket rather than exact birth date.
        """
        lines: list[str] = [
            f"Age: {self.age or 'unknown'}",
            f"Gender: {self.gender}",
        ]
        if self.ecog_performance_status is not None:
            lines.append(f"ECOG Performance Status: {self.ecog_performance_status}")
        if self.conditions:
            active = [c for c in self.conditions if c.clinical_status in ("active", "recurrence", "relapse")]
            inactive = [c for c in self.conditions if c not in active]
            if active:
                condition_strs = []
                for c in active:
                    s = c.name
                    if c.stage:
                        s += f" ({c.stage})"
                    condition_strs.append(s)
                lines.append(f"Active conditions: {', '.join(condition_strs)}")
            if inactive:
                lines.append(f"History of: {', '.join(c.name for c in inactive)}")
        if self.medications:
            active_meds = [m for m in self.medications if m.status == "active"]
            if active_meds:
                lines.append(f"Current medications: {', '.join(m.name for m in active_meds)}")
        if self.lab_values:
            abnormal = [lv for lv in self.lab_values if lv.is_abnormal]
            notable = abnormal or self.lab_values[:5]
            lab_strs = [f"{lv.name} {lv.value} {lv.unit}" for lv in notable]
            lines.append(f"Key labs: {', '.join(lab_strs)}")
        if self.allergies:
            lines.append(f"Allergies: {', '.join(self.allergies)}")
        flags = []
        if self.prior_cancer_treatment:
            flags.append("prior cancer treatment")
        if self.prior_radiation:
            flags.append("prior radiation")
        if self.prior_surgery:
            flags.append("prior surgery")
        if self.organ_transplant_history:
            flags.append("organ transplant history")
        if self.autoimmune_disease:
            flags.append("autoimmune disease")
        if self.pregnant_or_breastfeeding:
            flags.append("pregnant or breastfeeding")
        if flags:
            lines.append(f"Clinical history: {', '.join(flags)}")
        if self.zip_code:
            lines.append(f"Location: {self.zip_code}, {self.state or ''} {self.country}".strip())
        return "\n".join(lines)
