from langsmith import traceable
from models.schemas import AnalystState
from typing import Optional

RISK_FREE_RATE = 0.045       # 10-yr Treasury yield approximation
EQUITY_RISK_PREMIUM = 0.055  # Damodaran US ERP
PROJECTION_YEARS = 5
TERMINAL_GROWTH_RATE = 0.03


def _wacc(beta: float, debt_usd_m: float, equity_usd_m: float, tax_rate: float = 0.21) -> float:
    cost_of_equity = RISK_FREE_RATE + beta * EQUITY_RISK_PREMIUM
    if debt_usd_m + equity_usd_m == 0:
        return cost_of_equity
    # Assume pre-tax cost of debt ≈ risk-free + 200bps spread
    cost_of_debt = RISK_FREE_RATE + 0.02
    weight_equity = equity_usd_m / (debt_usd_m + equity_usd_m)
    weight_debt = debt_usd_m / (debt_usd_m + equity_usd_m)
    return weight_equity * cost_of_equity + weight_debt * cost_of_debt * (1 - tax_rate)


def _safe_list_first(lst, default=None) -> Optional[float]:
    if isinstance(lst, list) and lst:
        try:
            return float(lst[0])
        except (TypeError, ValueError):
            pass
    return default


@traceable(name="dcf_valuation_agent")
def run_dcf_valuation(state: AnalystState) -> AnalystState:
    """Build a 5-year DCF model from parsed financials and market data."""
    financials = state.get("parsed_financials")
    price_data = state.get("price_data")

    if not financials or not price_data:
        return {**state, "errors": state["errors"] + ["dcf_valuation: missing financials or price data"]}

    ocf = _safe_list_first(financials.get("operating_cash_flow"))
    capex = _safe_list_first(financials.get("capex"))
    shares = (
        financials.get("shares_outstanding")
        or (price_data.get("shares_outstanding", 0) / 1e6)
        or 1
    )
    shares = float(shares)

    if ocf is None or capex is None or shares <= 0:
        return {**state, "errors": state["errors"] + ["dcf_valuation: insufficient data for DCF"]}

    base_fcf = ocf - capex  # free cash flow in USD millions

    # Growth rate: use guidance if available, else historical OCF CAGR, else 8%
    guidance = financials.get("revenue_growth_guidance")
    ocf_hist = financials.get("operating_cash_flow", [])
    if guidance is not None:
        try:
            growth_rate = float(guidance)
        except (TypeError, ValueError):
            growth_rate = 0.08
    elif isinstance(ocf_hist, list) and len(ocf_hist) >= 3:
        try:
            oldest = float(ocf_hist[-1])
            newest = float(ocf_hist[0])
            n = len(ocf_hist) - 1
            growth_rate = (newest / oldest) ** (1 / n) - 1 if oldest > 0 else 0.08
        except (TypeError, ValueError, ZeroDivisionError):
            growth_rate = 0.08
    else:
        growth_rate = 0.08

    # Cap growth assumptions
    growth_rate = max(min(growth_rate, 0.35), -0.10)

    debt = float(financials.get("total_debt") or 0)
    cash = float(financials.get("cash_and_equivalents") or 0)
    market_cap_m = (price_data.get("market_cap") or 0) / 1e6
    beta = float(price_data.get("beta") or 1.0)

    wacc = _wacc(beta, debt, market_cap_m)
    wacc = max(wacc, 0.06)  # floor at 6%

    # Project FCF for N years
    projected_fcfs = []
    fcf = base_fcf
    for _ in range(PROJECTION_YEARS):
        fcf *= (1 + growth_rate)
        projected_fcfs.append(fcf)

    # Terminal value (Gordon growth)
    terminal_value = projected_fcfs[-1] * (1 + TERMINAL_GROWTH_RATE) / (wacc - TERMINAL_GROWTH_RATE)

    # PV of projected FCFs
    pv_fcfs = sum(
        cf / (1 + wacc) ** (i + 1)
        for i, cf in enumerate(projected_fcfs)
    )
    pv_terminal = terminal_value / (1 + wacc) ** PROJECTION_YEARS

    enterprise_value = pv_fcfs + pv_terminal
    equity_value = enterprise_value - debt + cash
    intrinsic_value_per_share = equity_value / shares if shares > 0 else None

    current_price = price_data.get("current_price")
    upside_pct = None
    if intrinsic_value_per_share and current_price and current_price > 0:
        upside_pct = (intrinsic_value_per_share - current_price) / current_price * 100

    dcf_model = {
        "base_fcf_m": round(base_fcf, 1),
        "growth_rate_used": round(growth_rate, 4),
        "wacc": round(wacc, 4),
        "terminal_growth_rate": TERMINAL_GROWTH_RATE,
        "projected_fcfs_m": [round(f, 1) for f in projected_fcfs],
        "pv_fcfs_m": round(pv_fcfs, 1),
        "pv_terminal_m": round(pv_terminal, 1),
        "enterprise_value_m": round(enterprise_value, 1),
        "equity_value_m": round(equity_value, 1),
        "intrinsic_value_per_share": round(intrinsic_value_per_share, 2) if intrinsic_value_per_share else None,
        "current_price": current_price,
        "upside_pct": round(upside_pct, 1) if upside_pct is not None else None,
    }

    return {**state, "dcf_model": dcf_model}
