import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.schemas import AnalysisRequest, AnalysisResponse, HealthResponse
from graph.workflow import run_analysis
from data.neo4j_client import Neo4jClient

app = FastAPI(
    title="Hedge Fund Analyst Agent",
    description="LLM-powered autonomous equity analysis: 10-K ingestion → DCF → Sentiment → Moat → Investment Memo",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health():
    neo4j_ok = False
    try:
        client = Neo4jClient()
        neo4j_ok = client.ping()
        client.close()
    except Exception:
        pass
    return {"status": "ok", "neo4j_connected": neo4j_ok}


@app.post("/analyze/{ticker}", response_model=AnalysisResponse)
def analyze(ticker: str, body: AnalysisRequest = None):
    """
    Run the full multi-agent analysis pipeline for a given ticker.

    Pipeline: SEC EDGAR fetch → Filing Parser → DCF Valuation →
              FinBERT Sentiment → Moat Assessment → Memo Synthesis → Neo4j store
    """
    transcript = None
    if body and body.include_transcript and body.transcript_text:
        transcript = body.transcript_text

    try:
        result = run_analysis(ticker=ticker, transcript_text=transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not result.get("investment_memo"):
        errors = result.get("errors", [])
        raise HTTPException(
            status_code=422,
            detail=f"Analysis incomplete. Errors: {errors}",
        )

    dcf = result.get("dcf_model") or {}
    sentiment = result.get("sentiment_results") or {}
    moat_raw = result.get("moat_analysis") or ""

    # Extract moat overall rating if JSON
    moat_score = None
    try:
        import json
        moat_data = json.loads(moat_raw)
        moat_score = moat_data.get("overall_moat_rating")
    except Exception:
        pass

    return AnalysisResponse(
        ticker=result["ticker"],
        company_name=result.get("company_name", ticker),
        recommendation=result.get("recommendation", "HOLD"),
        confidence_score=result.get("confidence_score", 0.5),
        investment_memo=result["investment_memo"],
        dcf_intrinsic_value=dcf.get("intrinsic_value_per_share"),
        dcf_current_price=dcf.get("current_price"),
        dcf_upside_pct=dcf.get("upside_pct"),
        sentiment_score=sentiment.get("net_score"),
        moat_score=moat_score,
        generated_at=datetime.utcnow(),
    )


@app.get("/history/{ticker}")
def get_history(ticker: str):
    """Retrieve prior analysis history for a ticker from Neo4j."""
    try:
        client = Neo4jClient()
        history = client.get_company_history(ticker.upper())
        client.close()
        return {"ticker": ticker.upper(), "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
