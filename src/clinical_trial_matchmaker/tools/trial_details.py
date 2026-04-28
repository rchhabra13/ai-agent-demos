"""
MCP Tool: get_trial_details

Fetches full details for a specific trial by NCT ID and optionally
generates clinician-facing commentary for a specific patient.
"""

from __future__ import annotations

import json

import structlog
from mcp.server.fastmcp import FastMCP

from clinical_trial_matchmaker.config import Settings
from clinical_trial_matchmaker.services.ctgov_client import ClinicalTrialsClient
from clinical_trial_matchmaker.services.fhir_parser import FhirParser
from clinical_trial_matchmaker.services.llm_reasoner import LLMReasoner

logger = structlog.get_logger(__name__)


def register_trial_details(mcp: FastMCP, settings: Settings) -> None:
    """Register the get_trial_details tool on the MCP server."""

    fhir_parser = FhirParser()
    reasoner = LLMReasoner(settings)

    @mcp.tool()
    async def get_trial_details(
        nct_id: str,
        fhir_patient_bundle: str | None = None,
        include_clinician_commentary: bool = True,
    ) -> str:
        """
        Retrieve complete information about a specific clinical trial.

        Fetches full protocol details from ClinicalTrials.gov including eligibility
        criteria, intervention details, outcome measures, participating sites, and
        contact information. Optionally generates AI-powered clinician commentary
        explaining how the trial fits a specific patient.

        Args:
            nct_id:                        ClinicalTrials.gov identifier (e.g. "NCT04513847").
            fhir_patient_bundle:           Optional FHIR R4 Patient Bundle (JSON string).
                                           When provided, generates patient-specific
                                           clinician commentary.
            include_clinician_commentary:  Whether to generate AI commentary when a
                                           patient bundle is provided (default: True).

        Returns:
            JSON string with full trial details. When a patient bundle is provided,
            includes an additional "clinician_commentary" field with AI-generated
            assessment of fit, concerns, next steps, and questions for the trial site.
        """
        nct_id = nct_id.strip().upper()
        logger.info("get_trial_details_called", nct_id=nct_id)

        async with ClinicalTrialsClient(settings) as ctgov:
            trial = await ctgov.get_trial(nct_id)

        if trial is None:
            return json.dumps({
                "error": f"Trial {nct_id} not found on ClinicalTrials.gov.",
                "hint": "Verify the NCT ID is correct and the trial exists.",
            })

        result = trial.model_dump()

        # Add clinician commentary if patient context is available
        if fhir_patient_bundle and include_clinician_commentary:
            try:
                patient_profile = fhir_parser.parse(fhir_patient_bundle)
                trial_text = (
                    f"NCT ID: {trial.nct_id}\n"
                    f"Title: {trial.title}\n"
                    f"Status: {trial.status}\n"
                    f"Phase: {', '.join(trial.phases)}\n"
                    f"Sponsor: {trial.sponsor}\n"
                    f"Summary: {trial.brief_summary or 'N/A'}\n\n"
                    f"Eligibility Criteria:\n{trial.eligibility_criteria_raw or 'N/A'}\n\n"
                    f"Interventions: {json.dumps(trial.interventions[:3])}\n"
                    f"Primary Outcomes: {json.dumps(trial.primary_outcomes[:2])}"
                )
                commentary = await reasoner.generate_clinician_commentary(
                    patient_profile=patient_profile,
                    trial_detail_text=trial_text,
                )
                result["clinician_commentary"] = commentary
                result["patient_id"] = patient_profile.patient_id
                logger.info(
                    "clinician_commentary_generated",
                    nct_id=nct_id,
                    patient_id=patient_profile.patient_id,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("commentary_generation_failed", nct_id=nct_id, error=str(exc))
                result["clinician_commentary_error"] = str(exc)

        # Always include the direct URL
        result["ctgov_url"] = f"https://clinicaltrials.gov/study/{nct_id}"

        return json.dumps(result, indent=2, default=str)
