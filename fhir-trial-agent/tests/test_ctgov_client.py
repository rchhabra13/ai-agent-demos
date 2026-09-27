"""Tests for the ClinicalTrials.gov API client."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import respx

from clinical_trial_matchmaker.services.ctgov_client import ClinicalTrialsClient


class TestClinicalTrialsClient:

    @respx.mock
    async def test_search_trials_success(
        self, test_settings, mock_ctgov_studies: list[dict]
    ) -> None:
        respx.get("https://clinicaltrials.gov/api/v2/studies").mock(
            return_value=httpx.Response(200, json={"studies": mock_ctgov_studies})
        )

        async with ClinicalTrialsClient(test_settings) as client:
            results = await client.search_trials(
                conditions=["Non-small cell lung cancer"],
                max_results=10,
            )

        assert len(results) == 1
        nct_id = ClinicalTrialsClient.extract_nct_id(results[0])
        assert nct_id == "NCT04513847"

    @respx.mock
    async def test_search_trials_empty_conditions(self, test_settings) -> None:
        async with ClinicalTrialsClient(test_settings) as client:
            results = await client.search_trials(conditions=[])
        assert results == []

    @respx.mock
    async def test_search_trials_returns_empty_on_no_results(self, test_settings) -> None:
        respx.get("https://clinicaltrials.gov/api/v2/studies").mock(
            return_value=httpx.Response(200, json={"studies": []})
        )
        async with ClinicalTrialsClient(test_settings) as client:
            results = await client.search_trials(conditions=["Rare Condition XYZ"])
        assert results == []

    @respx.mock
    async def test_get_trial_success(self, test_settings) -> None:
        nct_id = "NCT04513847"
        mock_study = {
            "protocolSection": {
                "identificationModule": {"nctId": nct_id, "briefTitle": "Test Trial"},
                "statusModule": {"overallStatus": "RECRUITING"},
                "designModule": {"phases": ["PHASE3"], "studyType": "INTERVENTIONAL"},
                "eligibilityModule": {
                    "eligibilityCriteria": "Inclusion:\n- NSCLC\nExclusion:\n- Prior therapy",
                    "minimumAge": "18 Years",
                    "sex": "ALL",
                },
                "descriptionModule": {"briefSummary": "A test trial."},
                "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Test Sponsor"}},
                "contactsLocationsModule": {"centralContacts": [], "locations": []},
                "armsInterventionsModule": {"interventions": []},
                "outcomesModule": {"primaryOutcomes": [], "secondaryOutcomes": []},
            }
        }
        respx.get(f"https://clinicaltrials.gov/api/v2/studies/{nct_id}").mock(
            return_value=httpx.Response(200, json=mock_study)
        )

        async with ClinicalTrialsClient(test_settings) as client:
            detail = await client.get_trial(nct_id)

        assert detail is not None
        assert detail.nct_id == nct_id
        assert detail.title == "Test Trial"
        assert detail.ctgov_url == f"https://clinicaltrials.gov/study/{nct_id}"

    @respx.mock
    async def test_get_trial_not_found(self, test_settings) -> None:
        respx.get("https://clinicaltrials.gov/api/v2/studies/NCT99999999").mock(
            return_value=httpx.Response(404)
        )

        async with ClinicalTrialsClient(test_settings) as client:
            result = await client.get_trial("NCT99999999")

        assert result is None

    def test_study_to_llm_context(self, mock_ctgov_studies: list[dict]) -> None:
        study = mock_ctgov_studies[0]
        client = ClinicalTrialsClient.__new__(ClinicalTrialsClient)
        context = ClinicalTrialsClient.study_to_llm_context(study)

        assert "NCT04513847" in context
        assert "NSCLC" in context
        assert "Merck" in context
        assert "PHASE3" in context

    def test_nct_id_extraction(self, mock_ctgov_studies: list[dict]) -> None:
        nct_id = ClinicalTrialsClient.extract_nct_id(mock_ctgov_studies[0])
        assert nct_id == "NCT04513847"

    def test_nct_id_extraction_malformed(self) -> None:
        result = ClinicalTrialsClient.extract_nct_id({})
        assert result is None
