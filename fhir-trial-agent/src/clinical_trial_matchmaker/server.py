"""
Clinical Trial Matchmaker — MCP Server entry point.

Registers three tools on a FastMCP server:
  1. find_matching_trials   — ranks trials by patient eligibility
  2. get_trial_details      — full trial info + clinician commentary
  3. draft_enrollment_summary — patient-facing summary for shared decisions
"""

from __future__ import annotations

import structlog
from mcp.server.fastmcp import FastMCP

from clinical_trial_matchmaker.config import get_settings
from clinical_trial_matchmaker.tools import (
    register_enrollment_summary,
    register_match_trials,
    register_trial_details,
)

logger = structlog.get_logger(__name__)


def create_server() -> FastMCP:
    """
    Construct and configure the MCP server instance.
    Called at import time so the server is usable in tests
    without triggering stdio transport.
    """
    settings = get_settings()

    # Configure structured logging
    import logging
    import structlog

    logging.basicConfig(level=settings.log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
    )

    mcp = FastMCP(
        name="clinical-trial-matchmaker",
        instructions=(
            "This MCP server helps clinicians find relevant clinical trials for their patients. "
            "Given a FHIR R4 Patient bundle, it queries ClinicalTrials.gov for recruiting trials "
            "and uses AI reasoning to score patient eligibility. "
            "\n\n"
            "Available tools:\n"
            "- find_matching_trials: Main tool. Pass a FHIR bundle to get ranked trials.\n"
            "- get_trial_details: Get full protocol info for a specific NCT ID.\n"
            "- draft_enrollment_summary: Generate a patient-friendly trial summary.\n"
            "\n"
            "SHARP context (sharp_patient_id, sharp_fhir_base_url, sharp_fhir_token) "
            "is automatically propagated by the Prompt Opinion platform."
        ),
    )

    # Register all tools
    register_match_trials(mcp, settings)
    register_trial_details(mcp, settings)
    register_enrollment_summary(mcp, settings)

    logger.info(
        "server_initialized",
        model=settings.llm_model,
        environment=settings.environment,
        tools=["find_matching_trials", "get_trial_details", "draft_enrollment_summary"],
    )

    return mcp


# Module-level server instance (required by FastMCP stdio transport)
mcp = create_server()


def main() -> None:
    """CLI entry point — runs the server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
