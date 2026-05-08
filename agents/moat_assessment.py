import os
import json
import anthropic
from langsmith import traceable
from models.schemas import AnalystState
from utils.prompts import MOAT_ASSESSMENT_PROMPT

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _build_financials_summary(financials: dict) -> str:
    rev = financials.get("revenue", [])
    ni = financials.get("net_income", [])
    ocf = financials.get("operating_cash_flow", [])
    lines = []
    if rev:
        lines.append(f"Revenue (most recent): ${rev[0]}M")
        if len(rev) >= 2 and rev[1] and rev[1] != 0:
            growth = (rev[0] - rev[1]) / abs(rev[1]) * 100
            lines.append(f"Revenue YoY growth: {growth:.1f}%")
    if ni:
        lines.append(f"Net Income: ${ni[0]}M")
    if ocf:
        lines.append(f"Operating Cash Flow: ${ocf[0]}M")
    lines.append(f"Total Debt: ${financials.get('total_debt', 'N/A')}M")
    lines.append(f"Cash: ${financials.get('cash_and_equivalents', 'N/A')}M")
    return "\n".join(lines)


@traceable(name="moat_assessment_agent")
def run_moat_assessment(state: AnalystState) -> AnalystState:
    """Claude-powered competitive moat assessment."""
    financials = state.get("parsed_financials")
    if not financials:
        return {**state, "errors": state["errors"] + ["moat_assessment: no financials"]}

    fin_summary = _build_financials_summary(financials)
    prompt = MOAT_ASSESSMENT_PROMPT.format(
        company_name=state.get("company_name", state["ticker"]),
        ticker=state["ticker"],
        financials_summary=fin_summary,
        business_description=financials.get("business_description", "N/A"),
        key_risks=", ".join(financials.get("key_risks", [])),
    )

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        moat_data = json.loads(raw)
        moat_text = json.dumps(moat_data, indent=2)
    except json.JSONDecodeError:
        moat_text = response.content[0].text.strip()
    except Exception as e:
        return {**state, "errors": state["errors"] + [f"moat_assessment: {e}"]}

    return {**state, "moat_analysis": moat_text}
