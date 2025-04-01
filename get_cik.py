#!/usr/bin/env python3

import requests
import sys

def get_cik_for_ticker(ticker: str) -> str:
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": "Phil Shaw posop@hotmail.com"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from SEC.")
    
    data = response.json()
    
    ticker = ticker.upper()
    for entry in data.values():
        if entry["ticker"] == ticker:
            return str(entry["cik_str"]).zfill(10)
            
    raise ValueError(f"Ticker '{ticker}' not found in SEC database.")

def main(argv):
    symbol = "MSFT"
    try:
        cik = get_cik_for_ticker(symbol)
        print(f"CIK for {symbol.upper()}: {cik}")
    except Exception as e:
        print(f"Error: {e}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))