# src/main.py

import argparse
import csv
import logging

from .fetch import (
        run_fetch
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

    parser.add_argument(
        "--tickersPath",
        default="tickers.csv",
        help="Path to CSV file containing tickers"
    )



    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fetch",
        nargs="+",
        help="Fetch SEC data for one or more tickers (e.g. --fetch MSFT TSM"
    )

    group.add_argument(
        "--fetchall",
        action="store_true",
        help="Fetch SEC data for all tickers in tickers.csv"
    )

    return parser.parse_args()


def main(argv):
    args = parse_args()
    configure_logging(args.verbose)

    run_fetch(
        force=args.force,
        csv_file=args.tickersPath,
        fetch=args.fetch,
        fetchall=args.fetchall
    )
