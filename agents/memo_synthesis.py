import os
import json
import anthropic
from langsmith import traceable
from models.schemas import AnalystState
from utils.prompts import MEMO_SYNTHESIS_PROMPT

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _dcf_summary(dcf: dict) -> str:
    if not dcf:
        return "DCF model unavailable."
    lines = [
        f"Intrinsic Value/Share: ${dcf.get('intrinsic_value_per_share', 'N/A')}",
        f"Current Price: ${dcf.get('current_price', 'N/A')}",
        f"Implied Upside: {dcf.get('upside_pct', 'N/A')}%",
        f"WACC: {dcf.get('wacc', 0) * 100:.1f}%",
        f"FCF Growth Rate Used: {dcf.get('growth_rate_used', 0) * 100:.1f}%",
        f"Enterprise Value: ${dcf.get('enterprise_value_m', 'N/A')}M",
    ]
    return "\n".join(lines)


def _sentiment_summary(sentiment: dict) -> str:
    if not sentiment:
        return "Sentiment analysis unavailable."
    return (
        f"Dominant tone: {sentiment.get('dominant', 'N/A')} "
        f"(net score: {sentiment.get('net_score', 0):.3f})\n"
        f"{sentiment.get('narrative', '')}"
    )


@traceable(name="memo_synthesis_agent")
def run_memo_synthesis(state: AnalystState) -> AnalystState:
    """Synthesize all agent outputs into a final investment memo."""
    financials = state.get("parsed_financials", {})
    dcf = state.get("dcf_model", {})
    sentiment = state.get("sentiment_results", {})
    moat = state.get("moat_analysis", "Moat analysis unavailable.")

    fin_summary = (
        f"Revenue: ${financials.get('revenue', ['N/A'])[0]}M | "
        f"Net Income: ${financials.get('net_income', ['N/A'])[0]}M | "
        f"OCF: ${financials.get('operating_cash_flow', ['N/A'])[0]}M\n"
        f"Business: {financials.get('business_description', 'N/A')}"
    )

    prompt = MEMO_SYNTHESIS_PROMPT.format(
        company_name=state.get("company_name", state["ticker"]),
        ticker=state["ticker"],
        dcf_summary=_dcf_summary(dcf),
        sentiment_summary=_sentiment_summary(sentiment),
        moat_analysis=moat,
        financials_summary=fin_summary,
    )

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: treat full response as memo text
        result = {
            "recommendation": "HOLD",
            "confidence_score": 0.5,
            "memo": response.content[0].text.strip(),
            "key_catalysts": [],
            "key_risks": financials.get("key_risks", []),
        }
    except Exception as e:
        return {**state, "errors": state["errors"] + [f"memo_synthesis: {e}"]}

    return {
        **state,
        "investment_memo": result.get("memo", ""),
        "recommendation": result.get("recommendation", "HOLD"),
        "confidence_score": float(result.get("confidence_score", 0.5)),
    }
