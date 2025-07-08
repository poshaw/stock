# src/main.py

import argparse
import logging
import os
import sys

from datetime import (
        datetime
)

from .fetch import (
        run_fetch
)

logger = logging.getLogger("main")

def configure_logging(verbosity: int):
    log_level = logging.WARNING  # default
    if verbosity >= 2:
        log_level = logging.DEBUG
    elif verbosity == 1:
        log_level = logging.INFO

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime("run_%Y%m%d_%H%M%S.log")
    log_path = os.path.join(log_dir, log_filename)

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)  # Always save everything to file

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Clear root handlers and reconfigure
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.DEBUG)  # Capture all levels globally
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    logging.debug(f"Logging initialized. Console level: {log_level}, File: {log_path}")

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

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
