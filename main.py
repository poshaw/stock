#!/usr/bin/env python3

import sys
import requests
import EDGAR_utils as edgar
from EDGAR_tags import HEADERS, TAGS

def load_tickers(filename="tickers.txt"):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def main(argv):
    tickers = load_tickers()
    cik_map = edgar.ticker_cik_map()

    # Example: Get first ticker and use a tag from TAGS list
    ticker = tickers[0]
    cik = cik_map[ticker]
    # tag = TAGS[0]  # Example: "NetIncomeLoss" or similar
    tag = TAGS["Operating Cash Flow"][0]

    print(f"Getting tag '{tag}' for ticker '{ticker}' with CIK {cik}")
    tag_data = edgar.fetch_tag_data(cik, tag)

    # Print part of the result
    results = edgar.extract_last_5_10k_values(tag_data)
    for r in results:
        print(f"{r['end']}: {r['val']:,}")


    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
