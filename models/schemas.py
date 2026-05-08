from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel
from datetime import datetime


class AnalystState(TypedDict):
    ticker: str
    company_name: str
    cik: str
    # Raw fetched data
    filing_text: Optional[str]
    transcript_text: Optional[str]
    price_data: Optional[Dict[str, Any]]
    # Agent outputs
    parsed_financials: Optional[Dict[str, Any]]
    dcf_model: Optional[Dict[str, Any]]
    sentiment_results: Optional[Dict[str, Any]]
    moat_analysis: Optional[str]
    # Final synthesis
    investment_memo: Optional[str]
    recommendation: Optional[str]   # BUY / HOLD / SELL
    confidence_score: Optional[float]
    errors: List[str]


class AnalysisRequest(BaseModel):
    ticker: str
    include_transcript: bool = False
    transcript_text: Optional[str] = None  # user-provided earnings call text


class AnalysisResponse(BaseModel):
    ticker: str
    company_name: str
    recommendation: str
    confidence_score: float
    investment_memo: str
    dcf_intrinsic_value: Optional[float] = None
    dcf_current_price: Optional[float] = None
    dcf_upside_pct: Optional[float] = None
    sentiment_score: Optional[float] = None
    moat_score: Optional[str] = None
    generated_at: datetime


class HealthResponse(BaseModel):
    status: str
    neo4j_connected: bool
