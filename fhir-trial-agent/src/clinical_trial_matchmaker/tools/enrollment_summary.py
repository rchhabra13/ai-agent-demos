"""
MCP Tool: draft_enrollment_summary

Generates a plain-English, patient-facing summary explaining a clinical trial
and why their doctor is discussing it with them. Designed for shared
decision-making conversations.
"""

from __future__ import annotations

import json

import structlog
from mcp.server.fastmcp import FastMCP

from clinical_trial_matchmaker.config import Settings
from clinical_trial_matchmaker.services.ctgov_client import ClinicalTrialsClient
from clinical_trial_matchmaker.services.llm_reasoner import LLMReasoner

logger = structlog.get_logger(__name__)


def register_enrollment_summary(mcp: FastMCP, settings: Settings) -> None:
    """Register the draft_enrollment_summary tool on the MCP server."""

    reasoner = LLMReasoner(settings)

    @mcp.tool()
    async def draft_enrollment_summary(
        nct_id: str,
        patient_name: str,
        eligibility_reasoning: str,
        patient_language: str = "English",
    ) -> str:
        """
        Draft a compassionate patient-facing summary about a clinical trial.

        Creates a plain-English (8th-grade reading level) document explaining
        why a patient's care team is discussing a specific clinical trial with them.
        Designed for use in shared decision-making conversations between clinicians
        and patients or their families.

        Args:
            nct_id:                 ClinicalTrials.gov identifier (e.g. "NCT04513847").
            patient_name:           Patient's first name for personalization.
            eligibility_reasoning:  Why this trial is relevant — can be copied from
                                    the "recommendation" field of find_matching_trials.
            patient_language:       Language for the summary (default: "English").
                                    Supported: English, Spanish, French, Mandarin,
                                    Portuguese, Arabic, Hindi.

        Returns:
            JSON string with:
            - "patient_summary": Plain-English patient-facing text
            - "nct_id": The trial identifier
            - "trial_title": Full trial title
            - "ctgov_url": Direct link to trial information
            - "disclaimer": Required medical disclaimer
        """
        nct_id = nct_id.strip().upper()
        logger.info(
            "draft_enrollment_summary_called",
            nct_id=nct_id,
            patient_language=patient_language,
        )

        # Fetch trial title and description for context
        trial_title = nct_id  # Fallback
        trial_description = ""
        try:
            async with ClinicalTrialsClient(settings) as ctgov:
                trial = await ctgov.get_trial(nct_id)
                if trial:
                    trial_title = trial.title
                    trial_description = trial.brief_summary or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("trial_fetch_for_summary_failed", nct_id=nct_id, error=str(exc))

        # Generate the patient summary
        summary = await reasoner.generate_patient_summary(
            patient_name=patient_name,
            nct_id=nct_id,
            trial_title=trial_title,
            eligibility_reasoning=eligibility_reasoning,
            trial_description=trial_description,
        )

        # Translate if requested
        if patient_language.lower() != "english":
            summary = await _translate(reasoner, summary, patient_language)

        return json.dumps(
            {
                "patient_summary": summary,
                "nct_id": nct_id,
                "trial_title": trial_title,
                "ctgov_url": f"https://clinicaltrials.gov/study/{nct_id}",
                "language": patient_language,
                "disclaimer": (
                    "This summary was prepared to support a conversation with your care team. "
                    "Participating in a clinical trial is always your choice. "
                    "Please discuss any questions with your doctor before making a decision."
                ),
            },
            indent=2,
        )


async def _translate(reasoner: LLMReasoner, text: str, language: str) -> str:
    """Translate patient summary to the requested language."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=reasoner._settings.anthropic_api_key)
    resp = await client.messages.create(
        model=reasoner._settings.llm_model,
        max_tokens=800,
        temperature=0.1,
        messages=[{
            "role": "user",
            "content": (
                f"Translate the following patient summary to {language}. "
                "Preserve the warm, compassionate tone. Return only the translated text.\n\n"
                f"{text}"
            ),
        }],
    )
    return resp.content[0].text.strip()
