"""MCP tool handlers for the Clinical Trial Matchmaker."""

from clinical_trial_matchmaker.tools.enrollment_summary import register_enrollment_summary
from clinical_trial_matchmaker.tools.match_trials import register_match_trials
from clinical_trial_matchmaker.tools.trial_details import register_trial_details

__all__ = [
    "register_enrollment_summary",
    "register_match_trials",
    "register_trial_details",
]
