import os
from langgraph.graph import StateGraph, START, END
from langsmith import traceable

from models.schemas import AnalystState
from data.edgar import get_cik_and_name, get_latest_10k_text
from data.market import get_market_data
from data.neo4j_client import Neo4jClient
from agents.filing_parser import run_filing_parser
from agents.dcf_valuation import run_dcf_valuation
from agents.sentiment import run_sentiment
from agents.moat_assessment import run_moat_assessment
from agents.memo_synthesis import run_memo_synthesis


# ── Node functions ──────────────────────────────────────────────────────────

def node_fetch_data(state: AnalystState) -> AnalystState:
    """Fetch 10-K filing text + market data in parallel conceptually, sequentially here."""
    ticker = state["ticker"]
    errors = list(state.get("errors", []))

    # EDGAR
    try:
        cik, company_name = get_cik_and_name(ticker)
        filing_text = get_latest_10k_text(cik)
    except Exception as e:
        errors.append(f"fetch_data/edgar: {e}")
        cik, company_name, filing_text = "", ticker, None

    # Market data
    try:
        price_data = get_market_data(ticker)
        if not company_name or company_name == ticker:
            company_name = price_data.get("long_name", ticker)
    except Exception as e:
        errors.append(f"fetch_data/market: {e}")
        price_data = None

    return {
        **state,
        "cik": cik,
        "company_name": company_name,
        "filing_text": filing_text,
        "price_data": price_data,
        "errors": errors,
    }


def node_parse_filing(state: AnalystState) -> AnalystState:
    return run_filing_parser(state)


def node_dcf(state: AnalystState) -> AnalystState:
    return run_dcf_valuation(state)


def node_sentiment(state: AnalystState) -> AnalystState:
    return run_sentiment(state)


def node_moat(state: AnalystState) -> AnalystState:
    return run_moat_assessment(state)


def node_memo(state: AnalystState) -> AnalystState:
    return run_memo_synthesis(state)


def node_store_neo4j(state: AnalystState) -> AnalystState:
    """Persist company data, metrics, and analysis result to Neo4j."""
    neo4j_uri = os.environ.get("NEO4J_URI")
    if not neo4j_uri:
        return state  # skip gracefully if Neo4j not configured

    try:
        client = Neo4jClient()
        price_data = state.get("price_data") or {}
        financials = state.get("parsed_financials") or {}

        client.upsert_company(
            ticker=state["ticker"],
            name=state.get("company_name", state["ticker"]),
            sector=price_data.get("sector"),
            industry=price_data.get("industry"),
        )
        if financials:
            fy = financials.get("fiscal_year_end", "unknown")
            client.store_metrics(state["ticker"], financials, period=fy)

        if state.get("recommendation"):
            client.store_analysis(
                ticker=state["ticker"],
                recommendation=state["recommendation"],
                confidence=state.get("confidence_score", 0.5),
                memo_snippet=state.get("investment_memo", "")[:500],
            )
        client.close()
    except Exception as e:
        return {**state, "errors": state["errors"] + [f"neo4j: {e}"]}

    return state


# ── Guard: skip nodes if we already have fatal errors in required upstream data ──

def _has_filing(state: AnalystState) -> str:
    return "parse" if state.get("filing_text") else "skip_parse"


# ── Build graph ─────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    workflow = StateGraph(AnalystState)

    workflow.add_node("fetch_data", node_fetch_data)
    workflow.add_node("parse_filing", node_parse_filing)
    workflow.add_node("run_dcf", node_dcf)
    workflow.add_node("run_sentiment", node_sentiment)
    workflow.add_node("assess_moat", node_moat)
    workflow.add_node("synthesize_memo", node_memo)
    workflow.add_node("store_neo4j", node_store_neo4j)

    workflow.add_edge(START, "fetch_data")
    workflow.add_edge("fetch_data", "parse_filing")
    workflow.add_edge("parse_filing", "run_dcf")
    workflow.add_edge("run_dcf", "run_sentiment")
    workflow.add_edge("run_sentiment", "assess_moat")
    workflow.add_edge("assess_moat", "synthesize_memo")
    workflow.add_edge("synthesize_memo", "store_neo4j")
    workflow.add_edge("store_neo4j", END)

    return workflow.compile()


@traceable(name="hedge_fund_analyst_pipeline")
def run_analysis(ticker: str, transcript_text: str = None) -> AnalystState:
    graph = build_graph()
    initial_state: AnalystState = {
        "ticker": ticker.upper(),
        "company_name": "",
        "cik": "",
        "filing_text": None,
        "transcript_text": transcript_text,
        "price_data": None,
        "parsed_financials": None,
        "dcf_model": None,
        "sentiment_results": None,
        "moat_analysis": None,
        "investment_memo": None,
        "recommendation": None,
        "confidence_score": None,
        "errors": [],
    }
    return graph.invoke(initial_state)
