import yfinance as yf
from typing import Dict, Any


def get_market_data(ticker: str) -> Dict[str, Any]:
    """Fetch price, beta, market cap, and shares outstanding via yfinance."""
    stock = yf.Ticker(ticker)
    info = stock.info

    hist = stock.history(period="1y")
    current_price = float(hist["Close"].iloc[-1]) if not hist.empty else None

    return {
        "current_price": current_price,
        "market_cap": info.get("marketCap"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "beta": info.get("beta", 1.0),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "long_name": info.get("longName", ticker),
    }
