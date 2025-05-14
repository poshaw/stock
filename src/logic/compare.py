# src/logic/compare.py

from tabulate import tabulate
from src.db import database
from src.fetch import fundamentals_api
from src.logic.ratios import calculate_pe_ratio
from src.fetch.sec import get_fundamentals, get_sec_value_series
from src.logic.growth import calculate_cagr

def compare_stocks(tickers):
    conn = database.get_connection()
    price_data = {}
    market_cap_data = {}
    pe_ratio_data = {}
    fcf_data = {}
    fcf_cagr_data = {}
    eps_cagr_data = {}

    for ticker in tickers:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, close FROM daily_prices
            WHERE ticker = ?
            ORDER BY date DESC LIMIT 1
        """, (ticker,))
        row = cursor.fetchone()
        price_data[ticker] = row[1] if row else "(no data)"
        market_cap_data[ticker] = fundamentals_api.get_market_cap(ticker)
        pe_ratio_data[ticker] = calculate_pe_ratio(ticker)

        fundamentals = get_fundamentals(ticker)
        fcf = fundamentals.get("fcf")
        fcf_data[ticker] = f"{fcf / 1_000_000_000:.1f}B" if isinstance(fcf, (int, float)) else "(no data)"

        fcf_series = get_sec_value_series(ticker, "NetCashProvidedByUsedInOperatingActivities")
        fcf_last_5 = fcf_series[:5] if len(fcf_series) >= 5 else fcf_series
        fcf_cagr = calculate_cagr(fcf_last_5)
        fcf_cagr_data[ticker] = f"{fcf_cagr:.1%}" if fcf_cagr is not None else "(no data)"

        eps_series = get_sec_value_series(ticker, "EarningsPerShareBasic")
        eps_last_5 = eps_series[:5] if len(eps_series) >= 5 else eps_series
        eps_cagr = calculate_cagr(eps_last_5)
        eps_cagr_data[ticker] = f"{eps_cagr:.1%}" if eps_cagr is not None else "(no data)"

    conn.close()

    headers = ["Metric"] + tickers
    rows = [
        ["Price per share"] + [price_data[t] for t in tickers],
        ["Market cap"] + [market_cap_data[t] for t in tickers],
        ["P/E ratio"] + [pe_ratio_data[t] for t in tickers],
        ["Free cash flow"] + [fcf_data[t] for t in tickers],
        ["FCF 5y CAGR"] + [fcf_cagr_data[t] for t in tickers],
        ["EPS 5y CAGR"] + [eps_cagr_data[t] for t in tickers],
    ]

    print("\nLatest Comparison:")
    print(tabulate(rows, headers=headers, tablefmt="github"))

