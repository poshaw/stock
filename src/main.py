# src/main.py

import argparse
import csv
import inspect
import logging
import requests
import sys

from src.domestic import (
    get_cik,
    get_gaap_tag,
    extract_quarterly_values,
    get_cached_or_fetch_json,
)

from src.foreign import (
    get_foreign_metric_data,
    get_foreign_filing_index,
)

from src.tag_map import TAGS
from src.ticker import Ticker

logger = logging.getLogger("main")

def configure_logging(verbosity):
    """
    Configure the global logging level based on user-specified verbosity.

    Parameters:
    ----------
    verbosity : int
        Determines the logging level:
        - 0: WARNING (default)
        - 1: INFO
        - 2 or higher: DEBUG

    This function sets the logging level globally using logging.basicConfig().
    Useful for controlling how much detail is shown during program execution.
    """
    if verbosity >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

def parse_args():
    """
    Parse command-line arguments for the SEC data tool.

    Returns:
    -------
    argparse.Namespace
        An object containing parsed arguments:
        - verbose (int): Controls logging verbosity. Use -v or -vv for INFO/DEBUG.
        - force (bool): If True, bypasses cache and forces re-fetch of data.

    This function defines and parses command-line flags using argparse, providing
    user control over verbosity and data refresh behavior.
    """
    parser = argparse.ArgumentParser(description="Fetch and analyze SEC filing data for stock evaluation")

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
            "--tickers",
            default="tickers.csv",
            help="Path to ticker CSV"
    )

    return parser.parse_args()

def load_tickers(csv_file="tickers.csv"):
    """
    Load a list of tickers from a CSV file.

    Parameters:
    ----------
    csv_file : str
        Path to a CSV file containing a column named 'ticker'. Default is 'tickers.csv'.

    Returns:
    -------
    list of str
        A list of uppercased tickers read from the file.

    Notes:
    -----
    - The CSV file must contain a column named 'ticker'.
    - Leading/trailing whitespace is stripped, and tickers are converted to uppercase.
    - Logs an error if the file is missing or malformed.
    """
    logger.debug(f"method {inspect.currentframe().f_code.co_name} called")
    logger.info(f"Loading tickers[] from {csv_file}")
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

    logger.info(f"Loaded {len(tickers)} tickers: \n\t{tickers}")
    return tickers

def main(verbosity: int, force: bool, csv_file: str = "tickers.csv"):
    """
    Main entry point for the SEC data processing pipeline.

    Parameters:
    ----------
    verbosity : int
        Controls logging level (0=WARNING, 1=INFO, 2=DEBUG).
    force : bool
        If True, bypasses cached data and forces refetch from SEC.
    csv_file : str, optional
        Path to a CSV file containing ticker symbols under the column "ticker".
        Defaults to "tickers.csv".

    Workflow:
    --------
    1. Loads ticker symbols from the specified CSV file.
    2. For each ticker:
        - Initializes a Ticker object.
        - Loads or fetches operating cash flow data (10-K or 20-F).
        - Stores the Ticker instance in a dictionary.
        - Logs a formatted summary of the ticker's metadata and metrics.

    Notes:
    -----
    - Errors during individual ticker initialization are logged and do not halt execution.
    - The final output is logged via each Ticker's __str__ method.
    """
    tickers = load_tickers(csv_file)

    ticker_objects = {}

    # Step 1: Initialize each Ticker
    for ticker in tickers:
        try:
            t = Ticker(ticker)
            t.load_operating_cash_flow()
            ticker_objects[t.ticker] = t
            logger.info("%s", t)  # Prints the Ticker __str__ method

        except Exception as e:
            logger.error(f"Failed to initialize Ticker '{ticker}': {e}")

if __name__ == "__main__":
    args = parse_args()
    configure_logging(args.verbose)
    sys.exit(main(verbosity=args.verbose, force=args.force, csv_file=args.tickers))

