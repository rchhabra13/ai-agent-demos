"""
LLM-powered eligibility reasoning service.

Uses Anthropic's Claude to:
1. Extract a structured PatientProfile from raw FHIR JSON.
2. Score patient eligibility against a list of candidate trials.
3. Generate patient-facing enrollment summaries.

All prompts are designed to elicit structured JSON output that is then
validated against Pydantic models.
"""

from __future__ import annotations

import json
from typing import Any

import structlog
from anthropic import AsyncAnthropic
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from clinical_trial_matchmaker.config import Settings
from clinical_trial_matchmaker.models.patient import PatientProfile
from clinical_trial_matchmaker.models.trial import EligibilityAssessment

logger = structlog.get_logger(__name__)

_SYSTEM_PROMPT = """\
You are a board-certified clinical research coordinator and oncology specialist \
with 15 years of experience matching patients to clinical trials. \
You reason carefully, cite specific eligibility criteria text when making assessments, \
and always flag uncertainty rather than guessing. \
You output only valid JSON — no markdown fences, no prose outside the JSON structure.\
"""


class LLMReasoner:
    """
    Wraps Anthropic's Claude API to perform healthcare-specific reasoning tasks.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    # ── Public API ──────────────────────────────────────────────────────────

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        stop=stop_after_attempt(2),
        before_sleep=before_sleep_log(logger, "warning"),  # type: ignore[arg-type]
        reraise=True,
    )
    async def score_eligibility(
        self,
        patient_profile: PatientProfile,
        trial_contexts: list[str],
    ) -> list[EligibilityAssessment]:
        """
        Score a list of trials for patient eligibility.

        Args:
            patient_profile: Structured patient data.
            trial_contexts:   List of formatted trial strings (from ClinicalTrialsClient).

        Returns:
            List of EligibilityAssessment objects, sorted by score descending.
        """
        if not trial_contexts:
            return []

        patient_summary = patient_profile.to_matching_summary()
        trials_block = "\n\n---\n\n".join(trial_contexts)

        prompt = f"""\
You will assess the eligibility of a patient for each of the following clinical trials.

## PATIENT CLINICAL PROFILE
{patient_summary}

## CANDIDATE TRIALS
{trials_block}

## YOUR TASK
For EACH trial above, produce a JSON object with these exact fields:
- "nct_id": string (the NCT ID, e.g. "NCT04513847")
- "trial_title": string (brief title of the trial)
- "eligibility_score": integer 0-100
  (80-100 = likely eligible, 50-79 = possible with more info, 0-49 = unlikely)
- "likely_eligible": boolean (true if score >= 65)
- "key_matches": array of strings — specific inclusion criteria the patient appears to satisfy
- "key_concerns": array of strings — specific exclusion criteria or risk factors that may disqualify
- "missing_information": array of strings — data points needed to fully assess (e.g. "HER2 status not documented")
- "recommendation": string — one concise sentence for the clinician
- "phase": string or null
- "status": string (RECRUITING, etc.)
- "sponsor": string or null
- "brief_summary": string (≤ 150 chars) or null

Return a JSON ARRAY of these objects, sorted by eligibility_score descending.
Do not include any text outside the JSON array.\
"""

        logger.info(
            "llm_scoring_trials",
            patient_id=patient_profile.patient_id,
            trial_count=len(trial_contexts),
            model=self._settings.llm_model,
        )

        response = await self._client.messages.create(
            model=self._settings.llm_model,
            max_tokens=self._settings.llm_max_tokens,
            temperature=self._settings.llm_temperature,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.content[0].text.strip()
        assessments = self._parse_assessments(raw_text)

        logger.info(
            "llm_scoring_complete",
            patient_id=patient_profile.patient_id,
            assessments=len(assessments),
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        return sorted(assessments, key=lambda a: a.eligibility_score, reverse=True)

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        stop=stop_after_attempt(2),
        before_sleep=before_sleep_log(logger, "warning"),  # type: ignore[arg-type]
        reraise=True,
    )
    async def generate_patient_summary(
        self,
        patient_name: str,
        nct_id: str,
        trial_title: str,
        eligibility_reasoning: str,
        trial_description: str = "",
    ) -> str:
        """
        Generate a compassionate, plain-English patient-facing summary
        explaining why this trial is being discussed.

        Returns a plain text string (not JSON).
        """
        prompt = f"""\
Write a compassionate patient-facing summary (8th-grade reading level, 150-200 words) \
explaining why their care team is discussing a clinical trial with them.

Patient name: {patient_name}
Trial: {trial_title} ({nct_id})
Why it may apply: {eligibility_reasoning}
Trial description: {trial_description[:400] if trial_description else "Not provided"}

Guidelines:
- Use warm, reassuring language
- Briefly explain what the trial is studying (1-2 sentences)
- Explain why the patient's doctor thinks it may be relevant (reference the eligibility reasoning)
- Mention that participation is always voluntary
- Encourage the patient to ask questions
- Do NOT make promises about outcomes, cures, or efficacy
- Do NOT include legal disclaimers

Return only the summary text, no headers or metadata.\
"""

        response = await self._client.messages.create(
            model=self._settings.llm_model,
            max_tokens=600,
            temperature=0.3,
            system="You are a compassionate patient educator who explains complex medical topics simply.",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        stop=stop_after_attempt(2),
        before_sleep=before_sleep_log(logger, "warning"),  # type: ignore[arg-type]
        reraise=True,
    )
    async def generate_clinician_commentary(
        self,
        patient_profile: PatientProfile,
        trial_detail_text: str,
    ) -> str:
        """
        Generate clinician-facing commentary on a specific trial for this patient:
        key fit reasons, next steps, questions to ask the trial site.

        Returns a plain text string.
        """
        prompt = f"""\
You are a clinical research coordinator preparing a brief for a physician.

## PATIENT PROFILE
{patient_profile.to_matching_summary()}

## TRIAL DETAILS
{trial_detail_text[:2000]}

Provide a structured clinical commentary with these sections:
1. **Potential Fit** — 2-3 bullets on why this trial matches the patient
2. **Potential Concerns** — 2-3 bullets on eligibility risks or unknowns
3. **Recommended Next Steps** — concrete actions (e.g., check specific lab, contact trial coordinator)
4. **Questions for Trial Site** — 2-3 specific questions the physician should ask

Keep each section concise. Use clinical language appropriate for a physician.\
"""

        response = await self._client.messages.create(
            model=self._settings.llm_model,
            max_tokens=800,
            temperature=0.2,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_assessments(raw: str) -> list[EligibilityAssessment]:
        """
        Parse the LLM JSON response into validated EligibilityAssessment objects.
        Handles minor formatting issues gracefully.
        """
        # Strip any accidental markdown fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        try:
            raw_list: list[dict[str, Any]] = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("llm_json_parse_error", error=str(exc), raw=raw[:300])
            return []

        assessments: list[EligibilityAssessment] = []
        for item in raw_list:
            try:
                assessments.append(EligibilityAssessment.model_validate(item))
            except Exception as exc:  # noqa: BLE001
                logger.warning("assessment_validation_error", error=str(exc), item=item)

        return assessments
