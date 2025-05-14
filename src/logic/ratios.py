# src/logic/ratios.py

import logging
from src.fetch.sec import get_fundamentals
from src.fetch.fundamentals_api import get_profile_data


logger = logging.getLogger(__name__)

def calculate_pe_ratio(ticker):
    profile = get_profile_data(ticker)
    fundamentals = get_fundamentals(ticker)

    try:
        price = profile.get("price")
        market_cap = profile.get("mktCap")
        if not (price and market_cap and fundamentals):
            return "(no data)"

        net_income = fundamentals.get("netIncome")
        if not net_income:
            return "(no data)"

        shares_outstanding = market_cap / price
        eps = net_income / shares_outstanding
        pe = price / eps

        logger.debug(f"{ticker} P/E formula: P/E = Price / (Net Income / (Market Cap / Price))")
        logger.debug(f"{ticker} P/E values: P/E = {price:.2f} / ({net_income:.2f} / ({market_cap:.2f} / {price:.2f})) = {pe:.2f}")

        return f"{pe:.1f}"
    except Exception:
        return "(no data)"

def calculate_eps(ticker):
    profile = get_profile_data(ticker)
    fundamentals = get_fundamentals(ticker)

    try:
        price = profile.get("price")
        market_cap = profile.get("mktCap")
        if not (price and market_cap and fundamentals):
            return "(no data)"

        net_income = fundamentals.get("netIncome")
        if not net_income:
            return "(no data)"

        shares_outstanding = market_cap / price
        eps = net_income / shares_outstanding

        logger.debug(f"{ticker} EPS formula: EPS = Net Income / (Market Cap / Price)")
        logger.debug(f"{ticker} EPS values: EPS = {net_income:.2f} / ({market_cap:.2f} / {price:.2f}) = {eps:.2f}")

        return f"{eps:.2f}"
    except Exception:
        return "(no data)"

