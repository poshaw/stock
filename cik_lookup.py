#!/usr/bin/env python3

import requests
from EDGAR_tags import HEADERS

url = "https://www.sec.gov/files/company_tickers.json"

def get_cik(ticker: str) -> str:
    """
    Looks up a single ticker's CIK using live data from the SEC.
    """
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from SEC.")
    
    data = response.json()
    ticker = ticker.upper()
    
    for entry in data.values():
        if entry["ticker"] == ticker:
            return str(entry["cik_str"]).zfill(10)
            
    raise ValueError(f"Ticker '{ticker}' not found in SEC database.")
    
def ticker_cik_map(filename="tickers.txt") -> dict:
    """
    Reads tickers from tickers.txt file and returns a {ticker: CIK} dictionary.
    """
    
    with open(filename, "r") as f:
        tickers = [line.strip().upper() for line in f if line.strip()]
    
    result = {}
    for ticker in tickers:
        try:
            cik = get_cik(ticker)
            result[ticker] = cik
        except ValueError:
            result[ticker] = None  # or skip if you prefer

    return result
