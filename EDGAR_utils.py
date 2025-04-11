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

def fetch_tag_data(cik, tag):
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
    print(f"Fetching data for tag: '{tag}' from {url}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def extract_last_5_10k_values(tag_data):
    try:
        records = tag_data["units"]["USD"]
    except KeyError:
        print("No USD records found.")
        return []

    # Filter only 10-K filings
    ten_ks = [entry for entry in records if entry.get("form") == "10-K"]

    # Remove duplicates based on the "end" date
    seen = set()
    unique_10ks = []
    for entry in ten_ks:
        end_date = entry.get("end")
        if end_date and end_date not in seen:
            seen.add(end_date)
            unique_10ks.append(entry)

    # Sort by end date descending
    unique_10ks.sort(key=lambda x: x["end"], reverse=True)

    # Return last 5
    return unique_10ks[:5]
