import os
import json
import anthropic
from langsmith import traceable
from transformers import pipeline
from models.schemas import AnalystState
from utils.prompts import SENTIMENT_SUMMARY_PROMPT

_finbert = None
_client = None

CHUNK_SIZE = 512  # tokens approx (characters / 4)
CHUNK_CHARS = CHUNK_SIZE * 4


def _get_finbert():
    global _finbert
    if _finbert is None:
        _finbert = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            truncation=True,
            max_length=512,
        )
    return _finbert


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _chunk_text(text: str, chunk_chars: int = CHUNK_CHARS) -> list[str]:
    words = text.split()
    chunks, current = [], []
    current_len = 0
    for word in words:
        current_len += len(word) + 1
        current.append(word)
        if current_len >= chunk_chars:
            chunks.append(" ".join(current))
            current, current_len = [], 0
    if current:
        chunks.append(" ".join(current))
    return chunks


def _aggregate_sentiment(results: list[dict]) -> dict:
    scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for r in results:
        label = r["label"].lower()
        if label in scores:
            scores[label] += r["score"]
            counts[label] += 1

    total = sum(counts.values())
    if total == 0:
        return {"positive": 0, "negative": 0, "neutral": 1, "net_score": 0.0, "dominant": "neutral"}

    avg = {k: scores[k] / max(counts[k], 1) * (counts[k] / total) for k in scores}
    net_score = avg["positive"] - avg["negative"]
    dominant = max(avg, key=avg.get)
    return {**avg, "net_score": round(net_score, 4), "dominant": dominant, "chunk_count": total}


@traceable(name="sentiment_agent")
def run_sentiment(state: AnalystState) -> AnalystState:
    """FinBERT sentiment analysis on transcript or MD&A section."""
    text = state.get("transcript_text") or state.get("filing_text", "")
    if not text:
        return {**state, "errors": state["errors"] + ["sentiment: no text available"]}

    # Use first 50k chars (MD&A section is typically in this range)
    text = text[:50_000]
    chunks = _chunk_text(text)[:40]  # cap at 40 chunks

    finbert = _get_finbert()
    raw_results = [finbert(chunk)[0] for chunk in chunks]
    aggregated = _aggregate_sentiment(raw_results)

    # Claude summarizes the sentiment pattern
    summary_prompt = SENTIMENT_SUMMARY_PROMPT.format(
        company_name=state.get("company_name", state["ticker"]),
        ticker=state["ticker"],
        sentiment_data=json.dumps(aggregated, indent=2),
    )
    try:
        response = _get_client().messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": summary_prompt}],
        )
        narrative = response.content[0].text.strip()
    except Exception as e:
        narrative = f"Sentiment summary unavailable: {e}"

    return {
        **state,
        "sentiment_results": {
            **aggregated,
            "narrative": narrative,
        },
    }
