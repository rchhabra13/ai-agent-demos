"""
Async client for the ClinicalTrials.gov API v2.

https://clinicaltrials.gov/data-api/api
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from clinical_trial_matchmaker.config import Settings
from clinical_trial_matchmaker.models.trial import (
    TrialContact,
    TrialDetail,
    TrialLocation,
    TrialStatus,
)

logger = structlog.get_logger(__name__)

# Fields to request for search results (keeps payload small)
_SEARCH_FIELDS = ",".join([
    "NCTId",
    "BriefTitle",
    "OfficialTitle",
    "OverallStatus",
    "Phase",
    "StudyType",
    "BriefSummary",
    "EligibilityCriteria",
    "MinimumAge",
    "MaximumAge",
    "Sex",
    "LeadSponsorName",
    "StartDate",
    "PrimaryCompletionDate",
    "EnrollmentCount",
])

# Fields for full trial detail
_DETAIL_FIELDS = ",".join([
    "NCTId",
    "BriefTitle",
    "OfficialTitle",
    "OverallStatus",
    "Phase",
    "StudyType",
    "BriefSummary",
    "DetailedDescription",
    "EligibilityCriteria",
    "MinimumAge",
    "MaximumAge",
    "Sex",
    "HealthyVolunteers",
    "LeadSponsorName",
    "StartDate",
    "PrimaryCompletionDate",
    "EnrollmentCount",
    "InterventionType",
    "InterventionName",
    "PrimaryOutcomeMeasure",
    "PrimaryOutcomeDescription",
    "SecondaryOutcomeMeasure",
    "CentralContactName",
    "CentralContactPhone",
    "CentralContactEMail",
    "LocationFacility",
    "LocationCity",
    "LocationState",
    "LocationCountry",
    "LocationZip",
    "LocationStatus",
])


class ClinicalTrialsClient:
    """
    Async HTTP client for ClinicalTrials.gov API v2.

    Uses httpx for async requests with automatic retries on transient errors.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "ClinicalTrialsClient":
        self._client = httpx.AsyncClient(
            base_url=self._settings.ctgov_base_url,
            headers={"User-Agent": self._settings.ctgov_user_agent},
            timeout=httpx.Timeout(self._settings.ctgov_timeout_seconds),
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Use ClinicalTrialsClient as an async context manager")
        return self._client

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, "warning"),  # type: ignore[arg-type]
        reraise=True,
    )
    async def search_trials(
        self,
        conditions: list[str],
        location: str = "United States",
        max_results: int = 20,
        status_filter: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for recruiting trials matching one or more conditions.

        Args:
            conditions: List of condition names to search for.
            location:   Country or city/state to filter by proximity.
            max_results: Maximum number of trials to return (capped at 100).
            status_filter: Override default RECRUITING filter.

        Returns:
            List of raw study dicts from the API.
        """
        if not conditions:
            return []

        status = status_filter or ["RECRUITING", "ENROLLING_BY_INVITATION"]
        query = " OR ".join(f'"{c}"' for c in conditions[:5])

        params: dict[str, Any] = {
            "query.cond": query,
            "filter.overallStatus": "|".join(status),
            "pageSize": min(max_results, 100),
            "fields": _SEARCH_FIELDS,
            "format": "json",
        }

        logger.info("ctgov_search", conditions=conditions, location=location)
        resp = await self._http.get("/studies", params=params)
        resp.raise_for_status()

        data = resp.json()
        studies: list[dict[str, Any]] = data.get("studies", [])
        logger.info("ctgov_search_results", count=len(studies))
        return studies

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, "warning"),  # type: ignore[arg-type]
        reraise=True,
    )
    async def get_trial(self, nct_id: str) -> TrialDetail | None:
        """
        Fetch full details for a single trial by NCT ID.

        Args:
            nct_id: The NCT identifier, e.g. "NCT04513847".

        Returns:
            TrialDetail if found, None if the trial does not exist.
        """
        nct_id = nct_id.strip().upper()
        logger.info("ctgov_get_trial", nct_id=nct_id)

        resp = await self._http.get(
            f"/studies/{nct_id}",
            params={"fields": _DETAIL_FIELDS, "format": "json"},
        )
        if resp.status_code == 404:
            logger.warning("ctgov_trial_not_found", nct_id=nct_id)
            return None
        resp.raise_for_status()

        data = resp.json()
        return self._parse_trial_detail(data)

    # ── Parsers ──────────────────────────────────────────────────────────────

    @staticmethod
    def extract_nct_id(study: dict[str, Any]) -> str | None:
        """Extract NCT ID from a search result study dict."""
        try:
            return (
                study.get("protocolSection", {})
                .get("identificationModule", {})
                .get("nctId")
            )
        except AttributeError:
            return None

    @staticmethod
    def extract_brief_summary(study: dict[str, Any]) -> str | None:
        try:
            return (
                study.get("protocolSection", {})
                .get("descriptionModule", {})
                .get("briefSummary")
            )
        except AttributeError:
            return None

    @staticmethod
    def extract_eligibility_text(study: dict[str, Any]) -> str | None:
        try:
            return (
                study.get("protocolSection", {})
                .get("eligibilityModule", {})
                .get("eligibilityCriteria")
            )
        except AttributeError:
            return None

    @classmethod
    def study_to_llm_context(cls, study: dict[str, Any], max_eligibility_chars: int = 1200) -> str:
        """
        Format a raw study dict into a compact string for LLM context.
        Truncates long eligibility text to stay within token budget.
        """
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        design_mod = proto.get("designModule", {})
        elig_mod = proto.get("eligibilityModule", {})
        desc_mod = proto.get("descriptionModule", {})
        sponsor_mod = proto.get("sponsorCollaboratorsModule", {})

        nct_id = ident.get("nctId", "UNKNOWN")
        title = ident.get("briefTitle", "Untitled")
        status = status_mod.get("overallStatus", "UNKNOWN")
        phases = design_mod.get("phases", ["N/A"])
        sponsor = sponsor_mod.get("leadSponsor", {}).get("name", "Unknown")
        summary = (desc_mod.get("briefSummary") or "")[:300]
        elig = (elig_mod.get("eligibilityCriteria") or "")[:max_eligibility_chars]
        min_age = elig_mod.get("minimumAge", "No minimum")
        max_age = elig_mod.get("maximumAge", "No maximum")
        sex = elig_mod.get("sex", "ALL")

        return (
            f"NCT ID: {nct_id}\n"
            f"Title: {title}\n"
            f"Status: {status} | Phase: {', '.join(phases)} | Sponsor: {sponsor}\n"
            f"Age: {min_age} - {max_age} | Sex: {sex}\n"
            f"Summary: {summary}\n"
            f"Eligibility Criteria:\n{elig}"
        )

    def _parse_trial_detail(self, data: dict[str, Any]) -> TrialDetail:
        proto = data.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        design_mod = proto.get("designModule", {})
        elig_mod = proto.get("eligibilityModule", {})
        desc_mod = proto.get("descriptionModule", {})
        sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
        contacts_mod = proto.get("contactsLocationsModule", {})
        interventions_mod = proto.get("armsInterventionsModule", {})
        outcomes_mod = proto.get("outcomesModule", {})

        nct_id = ident.get("nctId", "UNKNOWN")
        status_str = status_mod.get("overallStatus", "UNKNOWN")
        try:
            status = TrialStatus(status_str)
        except ValueError:
            status = TrialStatus.UNKNOWN

        # Contacts
        central_contacts = [
            TrialContact(
                name=c.get("name"),
                role=c.get("role"),
                phone=c.get("phone"),
                email=c.get("email"),
            )
            for c in contacts_mod.get("centralContacts", [])
        ]

        # Locations
        locations = [
            TrialLocation(
                facility=loc.get("facility"),
                city=loc.get("city"),
                state=loc.get("state"),
                country=loc.get("country"),
                zip_code=loc.get("zip"),
                status=loc.get("status"),
            )
            for loc in contacts_mod.get("locations", [])
        ]

        # Interventions
        interventions = [
            {"type": iv.get("type"), "name": iv.get("name"), "description": iv.get("description")}
            for iv in interventions_mod.get("interventions", [])
        ]

        # Outcomes
        primary_outcomes = [
            {"measure": o.get("measure"), "description": o.get("description"), "timeFrame": o.get("timeFrame")}
            for o in outcomes_mod.get("primaryOutcomes", [])
        ]
        secondary_outcomes = [
            {"measure": o.get("measure"), "description": o.get("description")}
            for o in outcomes_mod.get("secondaryOutcomes", [])
        ]

        return TrialDetail(
            nct_id=nct_id,
            title=ident.get("briefTitle", ""),
            official_title=ident.get("officialTitle"),
            status=status,
            phases=design_mod.get("phases", []),
            study_type=design_mod.get("studyType"),
            sponsor=sponsor_mod.get("leadSponsor", {}).get("name"),
            brief_summary=desc_mod.get("briefSummary"),
            detailed_description=desc_mod.get("detailedDescription"),
            eligibility_criteria_raw=elig_mod.get("eligibilityCriteria"),
            minimum_age=elig_mod.get("minimumAge"),
            maximum_age=elig_mod.get("maximumAge"),
            sex=elig_mod.get("sex"),
            healthy_volunteers=elig_mod.get("healthyVolunteers") == "Yes",
            start_date=status_mod.get("startDateStruct", {}).get("date"),
            primary_completion_date=status_mod.get("primaryCompletionDateStruct", {}).get("date"),
            estimated_enrollment=design_mod.get("enrollmentInfo", {}).get("count"),
            interventions=interventions,
            primary_outcomes=primary_outcomes,
            secondary_outcomes=secondary_outcomes,
            central_contacts=central_contacts,
            locations=locations,
        )
