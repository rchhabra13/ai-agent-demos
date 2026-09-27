import os
import json
import anthropic
from langsmith import traceable
from models.schemas import AnalystState
from utils.prompts import FILING_PARSER_PROMPT

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


@traceable(name="filing_parser_agent")
def run_filing_parser(state: AnalystState) -> AnalystState:
    """Extract structured financials from raw 10-K text using Claude."""
    filing_text = state.get("filing_text")
    if not filing_text:
        return {**state, "errors": state["errors"] + ["filing_parser: no filing text"]}

    prompt = FILING_PARSER_PROMPT.format(filing_text=filing_text[:100_000])

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return {**state, "errors": state["errors"] + [f"filing_parser: JSON parse error — {e}"]}
    except Exception as e:
        return {**state, "errors": state["errors"] + [f"filing_parser: {e}"]}

    return {**state, "parsed_financials": parsed}
