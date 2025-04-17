#!/usr/bin/env python3

import sys
import requests
import logging
import EDGAR_utils as edgar
import foreign_utils as foreign
from EDGAR_tags import HEADERS, TAGS
import database as db
from datetime import datetime, timedelta

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("main")
logging.getLogger("foreign_utils").setLevel(logger.level)
logging.getLogger("foreign_utils").addHandler(logging.StreamHandler(sys.stdout))


def load_tickers(domestic_file="tickers.txt", foreign_file="foreign_tickers.txt"):
    domestic = []
    foreign = []
    with open(domestic_file, "r") as f:
        domestic = [line.strip().upper() for line in f if line.strip()]
    with open(foreign_file, "r") as f:
        foreign = [line.strip().upper() for line in f if line.strip()]
    return domestic, foreign

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

def process_ticker(conn, ticker, cik, metric_key, tag_list, is_foreign):
    if db.was_fetched_recently(conn, ticker, metric_key):
        logger.info(f"Skipping fetch for {ticker} - data already fetched for '{metric_key}' within the past week.")
        print_metric_data(conn, ticker, metric_key)
        return

    logger.info(f"Getting metric '{metric_key}' for ticker '{ticker}' with CIK {cik}")

    if is_foreign:
        results = foreign.get_foreign_metric_data(ticker, cik, metric_key, tag_list)
        if results:
            db.insert_metric_data(conn, ticker, metric_key, results)
            db.log_fetch(conn, ticker, metric_key)
            print_metric_data(conn, ticker, metric_key)
        else:
            logger.error(f"No data extracted for foreign filer {ticker}")
        return

    for tag in tag_list:
        try:
            tag_data = edgar.fetch_tag_data(cik, tag)
            results = edgar.extract_last_5_10k_values(tag_data)

            if not results:
                logger.warning(f"No data found for {ticker} using tag '{tag}'. Trying next...")
                continue

            db.insert_metric_data(conn, ticker, metric_key, results)
            db.log_fetch(conn, ticker, metric_key)
            print_metric_data(conn, ticker, metric_key)
            return

        except requests.HTTPError as e:
            logger.warning(f"Tag '{tag}' not found for {ticker}: {e}")

    logger.error(f"No valid tag found for {ticker} for metric '{metric_key}'")

def main(argv):
    if "-vv" in argv:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("foreign_utils").setLevel(logging.DEBUG)
    elif "-v" in argv:
        logger.setLevel(logging.INFO)

    tickers, foreign_tickers = load_tickers()
    cik_map = edgar.ticker_cik_map()

    conn = db.get_db_connection()
    db.create_table_if_not_exists(conn)
    db.prune_old_fetch_logs(conn)

    for metric_key, tag_list in TAGS.items():
        for ticker in tickers:
            cik = cik_map.get(ticker)
            if not cik:
                logger.warning(f"Skipping unknown ticker: {ticker}")
                continue
            process_ticker(conn, ticker, cik, metric_key, tag_list, is_foreign=False)

        for ticker in foreign_tickers:
            cik = cik_map.get(ticker)
            if not cik:
                logger.warning(f"Skipping unknown foreign ticker: {ticker}")
                continue
            process_ticker(conn, ticker, cik, metric_key, tag_list, is_foreign=True)

    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
