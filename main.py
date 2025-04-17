#!/usr/bin/env python3

import sys
import requests
import logging
import EDGAR_utils as edgar
from EDGAR_tags import HEADERS, TAGS
import database as db
from datetime import datetime, timedelta

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("main")

def load_tickers(filename="tickers.txt"):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def print_metric_data(conn, ticker, metric_key):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, value FROM edgar_metrics
        WHERE ticker = ? AND metric = ?
        ORDER BY date DESC
    """, (ticker, metric_key))
    rows = cursor.fetchall()
    for date, value in rows:
        logger.info(f"{ticker} {date}: {value:,}")

def process_ticker(conn, ticker, cik, metric_key, tag):
    if db.was_fetched_recently(conn, ticker, metric_key):
        logger.info(f"Skipping fetch for {ticker} - data already fetched for '{metric_key}' within the past week.")
        print_metric_data(conn, ticker, metric_key)
        return

    logger.info(f"Getting metric '{metric_key}' for ticker '{ticker}' with CIK {cik}")
    try:
        tag_data = edgar.fetch_tag_data(cik, tag)
        results = edgar.extract_last_5_10k_values(tag_data)

        if not results:
            logger.warning(f"No 10-K data found for {ticker} and tag '{tag}'. Skipping.")
            return

        db.insert_metric_data(conn, ticker, metric_key, results)
        db.log_fetch(conn, ticker, metric_key)
        print_metric_data(conn, ticker, metric_key)

    except requests.HTTPError as e:
        logger.error(f"HTTP error while fetching data for {ticker}: {e}")
    except Exception as e:
        logger.error(f"Error processing {ticker}: {e}")


def main(argv):
    # Set logging level based on verbosity flags
    if "-vv" in argv:
        logger.setLevel(logging.DEBUG)
    elif "-v" in argv:
        logger.setLevel(logging.INFO)

    tickers = load_tickers()
    cik_map = edgar.ticker_cik_map()

    metric_key = "Operating Cash Flow"
    tag = TAGS[metric_key][0]

    conn = db.get_db_connection()
    db.create_table_if_not_exists(conn)
    db.prune_old_fetch_logs(conn)

    for ticker in tickers:
        cik = cik_map.get(ticker)
        if not cik:
            logger.warning(f"Skipping unknown ticker: {ticker}")
            continue
        process_ticker(conn, ticker, cik, metric_key, tag)

    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
