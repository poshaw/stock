# src/main.py

import argparse
import csv
import logging
import requests
import sys

from src.domestic import get_cik, get_gaap_tag, extract_quarterly_values
from src.foreign import get_foreign_metric_data, get_foreign_filing_index
from src.tag_map import TAGS
from src.domestic import get_cached_or_fetch_json
from src.ticker import Ticker

logger = logging.getLogger("main")

def configure_logging(verbosity):
    if verbosity >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

def parse_args():
    parser = argparse.ArgumentParser(description="SEC data fetcher")

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity (-v, -vv, etc.)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch all cached data"
    )

    return parser.parse_args()

def load_tickers(csv_file="tickers.csv"):
    tickers = []

    try:
        with open(csv_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row["ticker"].strip().upper()
                tickers.append(ticker)

    except FileNotFoundError:
        logger.error(f"Ticker file not found: {csv_file}")
    except Exception as e:
        logger.exception(f"Error reading {csv_file}: {e}")

    return tickers

def main(argv):
    args = parse_args()
    configure_logging(args.verbose)

    logger.info("Starting ticker load...")
    tickers = load_tickers()
    logger.info(f"Loaded {len(tickers)} tickers: {tickers}")

    ticker_objects = {}

    # Step 1: Initialize each Ticker
    for ticker_str in tickers:
        try:
            t = Ticker(ticker_str)
            t.load_operating_cash_flow()
            ticker_objects[t.symbol] = t
            logger.info(f"Initialized Ticker: {t.symbol} | CIK: {t.cik} | Exchange: {t.exchange} | Sector: {t.sector}")
        except Exception as e:
            logger.error(f"Failed to initialize Ticker '{ticker_str}': {e}")
