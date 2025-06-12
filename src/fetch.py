# src/fetch.py

import json
import logging
import os
import pickle
import requests
import time

from datetime import (
        datetime,
        timedelta,
)

from typing import (
        Dict,
        Optional,
)

from .config import (
        HEADERS,
)

from .tag_map import (
        TAGS,
)

from .utils import (
        is_cache_stale,
        ensure_dir,
)

logger = logging.getLogger("fetch")


# Global cache
_ticker_cik_cache = {}


def get_cache_path(ticker: str = "") -> str:
    return os.path.join("data", "cache", ticker.lower())


def update_company_tickers(max_age_days=30):
    """
    This function updates the rarely changed list of sec.gov company tickers 
    which we use to map tickers to CIK numbers
    """
    global _ticker_cik_cache

    company_tickers_json = os.path.join(get_cache_path(), "company_tickers.json")
    company_tickers_pickle = os.path.join(get_cache_path(), "company_tickers.pkl")


    # Step 1: Download JSON if cache expired
    if is_cache_stale(company_tickers_json, max_age_days=max_age_days):
        url = "https://www.sec.gov/files/company_tickers.json"
        logger.debug(f"Fetching company_tickers.json from SEC: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            raise RuntimeError("Downloaded content is not valid JSON")

        ensure_dir(os.path.dirname(company_tickers_json))

        with open(company_tickers_json, "w", encoding="utf-8") as f:
            json.dump(data, f)
        logger.debug(f"company_tickers.json cached to {company_tickers_json}")

    # Step 2: Return if already cached in memory
    if _ticker_cik_cache:
        return _ticker_cik_cache

    # Step 3: Try to load from pickle if newer than JSON
    if os.path.exists(company_tickers_pickle) and (
        os.path.getmtime(company_tickers_pickle) > os.path.getmtime(company_tickers_json)
    ):
        with open(company_tickers_pickle, "rb") as pf:
            _ticker_cik_cache = pickle.load(pf)
            logger.debug(f"Tickers loaded from pickle cache: {company_tickers_pickle}")
            return _ticker_cik_cache

    # Step 4: Load from JSON and rebuild pickle
    with open(company_tickers_json, "r", encoding="utf-8") as jf:
        raw_data = json.load(jf)

    _ticker_cik_cache = {
        record["ticker"].upper(): str(record["cik_str"]).zfill(10)
        for record in raw_data.values()
    }

    logger.debug(f"Saving tickers CIK to pickle cache: {company_tickers_pickle}")
    with open(company_tickers_pickle, "wb") as pf:
        pickle.dump(_ticker_cik_cache, pf)

    return _ticker_cik_cache

def get_cik(ticker: str) -> str:
    """
    Returns A CIK number for a given ticker
    """
    if not _ticker_cik_cache:
        update_company_tickers()
    try:
        return _ticker_cik_cache[ticker.upper()]
    except KeyError:
        raise ValueError(f"Ticker '{ticker}' not found in CIK cache.")


def get_cik_submissions(ticker: str, max_age_days=90) -> dict:
    # path = f"data/cache/{ticker.lower()}/submissions.json"
    path = os.path.join(get_cache_path(ticker), "submissions.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cik=get_cik(ticker)

    if not is_cache_stale(path, max_age_days=max_age_days):
        logger.debug(f"{ticker}: Loading cached submissions from {path}")
        with open(path, "r", encoding="utf-8") as f:
            data_submission = json.load(f)

    else:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        logger.debug(f"{ticker}: Fetching submissions from SEC: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data_submission = response.json()

        # save the this download to cache
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data_submission, f)
            logger.debug(f"{ticker}: Submissions cached to {path}")

    if cik != data_submission.get("cik", "").zfill(10):
        # we're not finding the same data
        logger.debug("CIKs don't match")

    return data_submission

def get_last_filing_date(ticker: str) -> Optional[datetime]:
    data_submissions = get_cik_submissions(ticker)

    recent = data_submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])

    latest_date = None
    
    for form, filing_date_str in zip(forms, filing_dates):
        if form in ("10-Q", "10-K", "20-F"):
            try:
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d")
                if latest_date is None or filing_date > latest_date:
                    latest_date = filing_date
            except ValueError:
                continue # Skip malformed date
    if latest_date is None:
        logger.warning(f"No 10-Q or 10-K filings found for {ticker}")
        raise ValueError(f"No valid 10-Q or 10-K filings found for {ticker}")

    logger.debug(f"Last filing date: for {ticker}: {latest_date}")
    return latest_date

def is_domestic(ticker: str) -> bool:
    try:
        data_submissions = get_cik_submissions(ticker)
        forms = data_submissions.get("filings", {}).get("recent", {}).get("form", [])
        forms_normalized = [f.strip().upper() for f in forms]
        is_domestic = "10-K" in forms_normalized
    except (KeyError, AttributeError, TypeError) as e:
        logger.warning(f"{ticker}: Failed to determine filer type, defaulting to Domestic. Error: {e}")
        is_domestic = True

    logger.debug(
        f"{ticker}: Filing type determined → {'Domestic (10-K)' if is_domestic else 'Foreign (20-F)'}"
    )
    return is_domestic


def get_next_expected_filing_date(ticker: str) -> Optional[datetime]:
    last_filing_date = get_last_filing_date(ticker)
    if last_filing_date is None:
        return None  # or raise an exception

    if is_domestic(ticker):
        # 10-Q/10-K filings are due 30-60 days later depending on filer type
        next_filing_date = last_filing_date + timedelta(days=30)
    else:
        # 20-F filings are usually due 4–6 months after FYE; use 178 days (~6 months)
        next_filing_date = last_filing_date + timedelta(days=178)

    return next_filing_date


def sec_data(ticker: str):
    logger.info(f"Processing ticker: {ticker}")
    cik = get_cik(ticker)
    ensure_dir(get_cache_path(ticker))

    for metric, tag_list in TAGS.items():
        path = os.path.join(get_cache_path(ticker), f"{metric}.json")

        if not is_cache_stale(path, ticker):
            logger.debug(f"{ticker}: {metric} cache is still valid — skipping download.")
            continue

        for tag in tag_list:
            time.sleep(2)  # avoid SEC rate limits
            namespace, tagname = tag.split(":")
            url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{namespace}/{tagname}.json"
            logger.debug(f"{ticker}: Requesting {url}")

            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                logger.debug(f"{ticker}: Tag fetch response: {response.status_code}")
                response.raise_for_status()

                data = response.json()

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)

                logger.info(f"{ticker}: Saved {metric} data using tag: {tag}")
                break  # success, move to next metric

            except requests.HTTPError as e:
                logger.warning(f"{ticker}: Tag failed for {metric} ({tag}): {e}")
            except Exception as e:
                logger.error(f"{ticker}: Unexpected error fetching tag {tag}: {e}")

