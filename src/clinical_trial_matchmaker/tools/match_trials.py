"""
MCP Tool: find_matching_trials

Given a FHIR patient bundle (or SHARP context), fetches recruiting trials
from ClinicalTrials.gov and uses LLM reasoning to rank them by eligibility.
"""

from __future__ import annotations

import json

import structlog
from mcp.server.fastmcp import FastMCP

from clinical_trial_matchmaker.config import Settings
from clinical_trial_matchmaker.models.trial import TrialMatchResponse
from clinical_trial_matchmaker.services.ctgov_client import ClinicalTrialsClient
from clinical_trial_matchmaker.services.fhir_parser import FhirParser
from clinical_trial_matchmaker.services.llm_reasoner import LLMReasoner

logger = structlog.get_logger(__name__)


def register_match_trials(mcp: FastMCP, settings: Settings) -> None:
    """Register the find_matching_trials tool on the MCP server."""

    fhir_parser = FhirParser()
    reasoner = LLMReasoner(settings)

    @mcp.tool()
    async def find_matching_trials(
        fhir_patient_bundle: str,
        max_results: int = 10,
        location_country: str = "United States",
        sharp_patient_id: str | None = None,
        sharp_fhir_base_url: str | None = None,
        sharp_fhir_token: str | None = None,
    ) -> str:
        """
        Find and rank clinical trials matching a patient's profile.

        Reads a FHIR R4 Patient Bundle, extracts the patient's conditions,
        medications, demographics, and lab values, then queries ClinicalTrials.gov
        for recruiting trials and uses AI reasoning to score patient eligibility
        for each trial.

        Args:
            fhir_patient_bundle:  A FHIR R4 Bundle (JSON string) containing Patient,
                                  Condition, MedicationRequest, and Observation resources.
                                  When running on the Prompt Opinion platform this is
                                  automatically populated via SHARP context.
            max_results:          Maximum number of ranked trials to return (1-20).
            location_country:     Country filter for trial sites (default: "United States").
            sharp_patient_id:     SHARP context: patient ID in the EHR system.
            sharp_fhir_base_url:  SHARP context: base URL of the FHIR server.
            sharp_fhir_token:     SHARP context: bearer token for FHIR access.

        Returns:
            JSON string containing a TrialMatchResponse with ranked trials,
            eligibility scores (0-100), key matches, key concerns, and
            clinician recommendations. Includes a mandatory medical disclaimer.
        """
        logger.info(
            "find_matching_trials_called",
            sharp_patient_id=sharp_patient_id,
            max_results=max_results,
        )

        # 1. If SHARP context is present, optionally fetch live FHIR bundle
        #    (In production Prompt Opinion injects the bundle automatically)
        if sharp_fhir_base_url and sharp_patient_id and sharp_fhir_token:
            try:
                import httpx
                async with httpx.AsyncClient(
                    headers={"Authorization": f"Bearer {sharp_fhir_token}"},
                    timeout=settings.fhir_timeout_seconds,
                ) as http:
                    resp = await http.get(
                        f"{sharp_fhir_base_url.rstrip('/')}/Patient/{sharp_patient_id}/$everything",
                        params={"_count": "100"},
                    )
                    resp.raise_for_status()
                    fhir_patient_bundle = resp.text
                    logger.info("fhir_bundle_fetched_via_sharp", patient_id=sharp_patient_id)
            except Exception as exc:  # noqa: BLE001
                logger.warning("sharp_fhir_fetch_failed", error=str(exc))
                # Fall through to use the bundle passed directly

        # 2. Parse FHIR bundle into structured profile
        try:
            patient_profile = fhir_parser.parse(fhir_patient_bundle)
        except ValueError as exc:
            return json.dumps({"error": f"Invalid FHIR bundle: {exc}"})

        if not patient_profile.active_condition_names:
            return json.dumps({
                "error": "No active conditions found in FHIR bundle. Cannot perform trial matching.",
                "hint": "Ensure the bundle includes Condition resources with active clinicalStatus.",
            })

        # 3. Search ClinicalTrials.gov
        async with ClinicalTrialsClient(settings) as ctgov:
            studies = await ctgov.search_trials(
                conditions=patient_profile.active_condition_names,
                location=location_country,
                max_results=min(max_results * 2, 40),  # Fetch extra; LLM will filter
            )

        if not studies:
            return json.dumps({
                "patient_id": patient_profile.patient_id,
                "message": "No currently recruiting trials found for the patient's conditions.",
                "conditions_searched": patient_profile.active_condition_names,
            })

        # 4. Format studies as LLM context strings
        ctgov_tmp = ClinicalTrialsClient(settings)  # Stateless for parsing only
        trial_contexts = [
            ctgov_tmp.study_to_llm_context(s)
            for s in studies[:20]
        ]

        # 5. LLM eligibility scoring
        assessments = await reasoner.score_eligibility(
            patient_profile=patient_profile,
            trial_contexts=trial_contexts,
        )

        # 6. Limit to requested number of results
        top_assessments = assessments[:max_results]

        # 7. Build and return response
        response = TrialMatchResponse(
            patient_id=patient_profile.patient_id,
            query_conditions=patient_profile.active_condition_names,
            total_trials_searched=len(studies),
            matches=top_assessments,
            reasoning_model=settings.llm_model,
        )

        logger.info(
            "find_matching_trials_complete",
            patient_id=patient_profile.patient_id,
            trials_found=len(studies),
            matches_returned=len(top_assessments),
        )

        return response.model_dump_json(indent=2)
