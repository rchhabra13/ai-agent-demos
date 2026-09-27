"""Clinical trial data models."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class TrialStatus(StrEnum):
    RECRUITING = "RECRUITING"
    NOT_YET_RECRUITING = "NOT_YET_RECRUITING"
    ACTIVE_NOT_RECRUITING = "ACTIVE_NOT_RECRUITING"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    WITHDRAWN = "WITHDRAWN"
    ENROLLING_BY_INVITATION = "ENROLLING_BY_INVITATION"
    UNKNOWN = "UNKNOWN"


class TrialPhase(StrEnum):
    PHASE_1 = "PHASE1"
    PHASE_2 = "PHASE2"
    PHASE_3 = "PHASE3"
    PHASE_4 = "PHASE4"
    EARLY_PHASE_1 = "EARLY_PHASE1"
    NA = "NA"


class TrialContact(BaseModel):
    """Contact person for a clinical trial."""

    name: str | None = None
    role: str | None = None
    phone: str | None = None
    email: str | None = None


class TrialLocation(BaseModel):
    """A geographic site participating in a trial."""

    facility: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zip_code: str | None = None
    status: str | None = None
    contact: TrialContact | None = None


class EligibilityAssessment(BaseModel):
    """
    LLM-generated eligibility assessment for one patient against one trial.
    All fields are populated by the LLM reasoning step.
    """

    nct_id: str = Field(description="ClinicalTrials.gov identifier, e.g. NCT04513847")
    trial_title: str

    # Scoring
    eligibility_score: int = Field(
        ge=0,
        le=100,
        description="0-100 likelihood of eligibility. 80+ = likely eligible, 50-79 = possible, <50 = unlikely",
    )
    likely_eligible: bool

    # Reasoning
    key_matches: list[str] = Field(
        description="Specific inclusion criteria the patient appears to meet",
        default_factory=list,
    )
    key_concerns: list[str] = Field(
        description="Specific exclusion criteria or red flags that may disqualify the patient",
        default_factory=list,
    )
    missing_information: list[str] = Field(
        description="Data points needed to fully assess eligibility",
        default_factory=list,
    )
    recommendation: str = Field(
        description="One-sentence clinical recommendation for the clinician"
    )

    # Metadata
    phase: str | None = None
    status: str | None = None
    sponsor: str | None = None
    brief_summary: str | None = None


class TrialMatchResponse(BaseModel):
    """Full response for the find_matching_trials tool."""

    patient_id: str
    query_conditions: list[str]
    total_trials_searched: int
    matches: list[EligibilityAssessment]
    reasoning_model: str
    disclaimer: str = (
        "This output is for informational purposes only and does not constitute medical advice. "
        "Clinical eligibility must be confirmed by the trial site. "
        "Always verify current enrollment status directly with the trial team."
    )


class TrialDetail(BaseModel):
    """Full detail for a single clinical trial from ClinicalTrials.gov."""

    nct_id: str
    title: str
    official_title: str | None = None
    status: TrialStatus = TrialStatus.UNKNOWN
    phases: list[str] = Field(default_factory=list)
    study_type: str | None = None
    sponsor: str | None = None
    brief_summary: str | None = None
    detailed_description: str | None = None

    # Eligibility
    eligibility_criteria_raw: str | None = Field(
        default=None,
        description="Raw eligibility text from ClinicalTrials.gov (inclusion + exclusion)"
    )
    minimum_age: str | None = None
    maximum_age: str | None = None
    sex: str | None = None
    healthy_volunteers: bool | None = None

    # Dates
    start_date: str | None = None
    primary_completion_date: str | None = None
    estimated_enrollment: int | None = None

    # Interventions
    interventions: list[dict[str, Any]] = Field(default_factory=list)

    # Outcomes
    primary_outcomes: list[dict[str, Any]] = Field(default_factory=list)
    secondary_outcomes: list[dict[str, Any]] = Field(default_factory=list)

    # Contacts & locations
    central_contacts: list[TrialContact] = Field(default_factory=list)
    locations: list[TrialLocation] = Field(default_factory=list)

    # URL
    ctgov_url: str = Field(default="")

    def model_post_init(self, __context: Any) -> None:
        if self.nct_id and not self.ctgov_url:
            self.ctgov_url = f"https://clinicaltrials.gov/study/{self.nct_id}"
