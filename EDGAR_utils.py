#!/usr/bin/env python3

from database import get_db_connection, get_cik_from_db, save_cik_to_db
import requests
from EDGAR_tags import HEADERS


def get_cik(ticker: str) -> str:
    """
    First check local DB for CIK. If not found, fetch from SEC and cache.
    """
    ticker = ticker.upper()
    conn = get_db_connection()
    cik = get_cik_from_db(conn, ticker)
    if cik:
        return cik

    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from SEC.")
    data = response.json()

    for entry in data.values():
        if entry["ticker"] == ticker:
            cik = str(entry["cik_str"]).zfill(10)
            save_cik_to_db(conn, ticker, cik)
            return cik

    raise ValueError(f"Ticker '{ticker}' not found in SEC database.")
    
def ticker_cik_map(domestic_file="tickers.txt", foreign_file="foreign_tickers.txt") -> dict:
    all_tickers = []
    with open(domestic_file, "r") as f:
        all_tickers += [line.strip().upper() for line in f if line.strip()]
    with open(foreign_file, "r") as f:
        all_tickers += [line.strip().upper() for line in f if line.strip()]

    result = {}
    for ticker in all_tickers:
        try:
            cik = get_cik(ticker)
            result[ticker] = cik
        except ValueError:
            result[ticker] = None
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

    # Accept both 10-K and 20-F (foreign annual reports)
    annual_forms = {"10-K", "20-F"}
    annuals = [entry for entry in records if entry.get("form") in annual_forms]


    # Remove duplicates based on the "end" date
    seen = set()
    unique_annuals = []
    for entry in annuals:
        end_date = entry.get("end")
        if end_date and end_date not in seen:
            seen.add(end_date)
            unique_annuals.append(entry)

    # Sort by end date descending
    unique_annuals.sort(key=lambda x: x["end"], reverse=True)

    # Return last 5
    return unique_annuals[:5]
