import os
import json
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple

EDGAR_BASE = "https://data.sec.gov"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
HEADERS = {"User-Agent": os.environ.get("SEC_USER_AGENT", "HedgeFundAnalyst contact@example.com")}

_ticker_cik_cache: dict = {}


def _get_ticker_cik_map() -> dict:
    if _ticker_cik_cache:
        return _ticker_cik_cache
    resp = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    for entry in data.values():
        ticker = entry["ticker"].upper()
        cik = str(entry["cik_str"]).zfill(10)
        _ticker_cik_cache[ticker] = (cik, entry["title"])
    return _ticker_cik_cache


def get_cik_and_name(ticker: str) -> Tuple[str, str]:
    mapping = _get_ticker_cik_map()
    ticker = ticker.upper()
    if ticker not in mapping:
        raise ValueError(f"Ticker {ticker} not found in EDGAR")
    return mapping[ticker]  # (cik, company_name)


def get_latest_10k_text(cik: str, max_chars: int = 120_000) -> Optional[str]:
    """Fetch most recent 10-K text from EDGAR, truncated to max_chars."""
    url = f"{EDGAR_BASE}/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    submissions = resp.json()

    filings = submissions.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    accessions = filings.get("accessionNumber", [])
    primary_docs = filings.get("primaryDocument", [])

    # Find first 10-K
    for form, accession, doc in zip(forms, accessions, primary_docs):
        if form == "10-K":
            accession_clean = accession.replace("-", "")
            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}"
                f"/{accession_clean}/{doc}"
            )
            time.sleep(0.1)  # EDGAR rate limit courtesy
            filing_resp = requests.get(filing_url, headers=HEADERS, timeout=60)
            filing_resp.raise_for_status()

            soup = BeautifulSoup(filing_resp.text, "lxml")
            # Remove script/style noise
            for tag in soup(["script", "style", "ix:header", "ix:hidden"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            # Collapse whitespace
            import re
            text = re.sub(r"\s+", " ", text)
            return text[:max_chars]

    return None
