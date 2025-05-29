#!/usr/bin/env python3

import argparse
import csv
import logging
import requests
from src.sec import get_cik, get_gaap_tag, extract_quarterly_values

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

    # grab the tickers from tickers.csv
    logger.info("Starting ticker load...")
    domestic, foreign = load_tickers()
    logger.info(f"Loaded {len(domestic)} domestic tickers: {domestic}")
    logger.info(f"Loaded {len(foreign)} foreign tickers: {foreign}")

    # match tickers to CIK numbers from sec.gov using cached data if available
    all_tickers = domestic + foreign
    TAG = "NetCashProvidedByUsedInOperatingActivities"
    cik_map = {}

    for ticker in all_tickers:
        try:
            cik = get_cik(ticker, force=args.force)
            cik_map[ticker] = cik
            logger.info(f"{ticker} → CIK: {cik}")
        except Exception as e:
            logger.error(f"Failed to fetch CIK for {ticker}: {e}")

    for ticker, cik in cik_map.items():
        try:
            tag_data = get_gaap_tag(ticker, cik, TAG, force=args.force)
            entries = extract_quarterly_values(tag_data)

            if not entries:
                logger.warning(f"{ticker}: No quarterly values found for tag '{TAG}'")
            else:
                for entry in entries:
                    logger.info(f"{ticker} {entry['end']}: {entry['val']:,}")

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"{ticker}: Tag '{TAG}' not found on SEC (404)")
            else:
                logger.error(f"{ticker}: HTTP error fetching tag '{TAG}': {e}")
        except Exception as e:
            logger.error(f"{ticker}: Unexpected error processing tag '{TAG}': {e}")




            logger.info(f"{ticker} → CIK: {cik}")

            #tag_data = get_gaap_tag(ticker, cik, TAG, force=args.force)
            #entries = extract_quarterly_values(tag_data)

            #for entry in entries:
            #    logger.info(f"{ticker} {entry['end']}: {entry['val']:,}")

            try:
                tag_data = get_gaap_tag(ticker, cik, TAG, force=args.force)
                entries = extract_quarterly_values(tag_data)

                if not entries:
                    logger.warning(f"{ticker}: No quarterly values found for tag '{TAG}'")
                else:
                    for entry in entries:
                        logger.info(f"{ticker} {entry['end']}: {entry['val']:,}")

            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    logger.warning(f"{ticker}: Tag '{TAG}' not found on SEC (404)")
                else:
                    logger.error(f"{ticker}: HTTP error fetching tag '{TAG}': {e}")
            except Exception as e:
                logger.error(f"{ticker}: Unexpected error processing tag '{TAG}': {e}")


        except Exception as e:
            logger.error(f"Failed to process {ticker}: {e}")

    return 0
