# src/main.py

import argparse
import csv
import logging

from .fetch import (
        sec_data,
        update_company_tickers,
        get_last_filing_date
)

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

    tickers = load_tickers()
    logger.info(f"Loaded {len(tickers)} tickers: {tickers}")

    update_company_tickers()

    for t in tickers:
        sec_data(t)
