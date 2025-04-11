#!/usr/bin/env python3

import sys
import requests
import EDGAR_utils as edgar
from EDGAR_tags import HEADERS, TAGS
import database as db

def load_tickers(filename="tickers.txt"):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def main(argv):
    tickers = load_tickers()
    cik_map = edgar.ticker_cik_map()

    # Example: Get first ticker and use a tag from TAGS list
    ticker = tickers[0]
    cik = cik_map[ticker]
    metric_key = "Operating Cash Flow"
    tag = TAGS[metric_key][0]

    print(f"Getting tag '{tag}' for ticker '{ticker}' with CIK {cik}")
    tag_data = edgar.fetch_tag_data(cik, tag)

    results = edgar.extract_last_5_10k_values(tag_data)
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, value FROM edgar_metrics
        WHERE ticker = ? AND metric = ?
        ORDER BY date DESC
    """, (ticker, metric_key))
    rows = cursor.fetchall()
    for date, value in rows:
        print(f"{date}: {value:,}")
    conn.close()

    # Store results in database
    conn = db.get_db_connection()
    db.create_table_if_not_exists(conn)
    db.insert_metric_data(conn, ticker, metric_key, results)
    conn.close()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
