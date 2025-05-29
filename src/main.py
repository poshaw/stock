#!/usr/bin/env python3

import csv
import sys
import argparse
import logging
from src.sec import get_cik

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
    domestic = []
    foreign = []

    try:
        with open(csv_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row["ticker"].strip().upper()
                is_foreign = row.get("is_foreign", "").strip().lower() == "true"

                if is_foreign:
                    foreign.append(ticker)
                else:
                    domestic.append(ticker)

    except FileNotFoundError:
        logger.error(f"Ticker file not found: {csv_file}")
    except Exception as e:
        logger.exception(f"Error reading {csv_file}: {e}")

    return domestic, foreign

def main(argv):
    args = parse_args()
    configure_logging(args.verbose)
    logger.info("Starting ticker load...")

    domestic, foreign = load_tickers()
    logger.info(f"Loaded {len(domestic)} domestic tickers: {domestic}")
    logger.info(f"Loaded {len(foreign)} foreign tickers: {foreign}")

    all_tickers = domestic + foreign
    for ticker in all_tickers:
        try:
            cik = get_cik(ticker, force=args.force)
            logger.info(f"{ticker} → CIK: {cik}")
        except Exception as e:
            logger.error(f"Failed to fetch CIK for {ticker}: {e}")

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
