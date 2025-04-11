#!/usr/bin/env python3

import sys
import requests
from cik_lookup import get_cik, ticker_cik_map
from EDGAR_tags import HEADERS, TAGS

def load_tickers(filename="tickers.txt"):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

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

def main(argv):
    tickers = load_tickers()
    cik_map = ticker_cik_map()

    # Example: Get first ticker and use a tag from TAGS list
    ticker = tickers[0]
    cik = cik_map[ticker]
    # tag = TAGS[0]  # Example: "NetIncomeLoss" or similar
    tag = TAGS["Operating Cash Flow"][0]

    print(f"Getting tag '{tag}' for ticker '{ticker}' with CIK {cik}")
    tag_data = fetch_tag_data(cik, tag)

    # Print part of the result
    results = extract_last_5_10k_values(tag_data)
    for r in results:
        print(f"{r['end']}: {r['val']:,}")


    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
