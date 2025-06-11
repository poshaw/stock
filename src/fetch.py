# src/fetch.py

from datetime import datetime
import json
import logging
import os
import pickle
import requests
import time
from typing import Dict

from .config import (
        HEADERS,
)

from .tag_map import (
        TAGS,
)

from .utils import (
        is_cache_expired,
        ensure_dir,
)

logger = logging.getLogger("import")

company_tickers_json = "data/cache/company_tickers.json"
company_tickers_pickle = "data/cache/company_tickers.pkl"

# Global cache
_ticker_cik_cache = {}

def update_company_tickers(max_age_days=7):
    global _ticker_cik_cache

    # Step 1: Download JSON if cache expired
    if is_cache_expired(company_tickers_json, max_age_days):
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

    else:
        logger.debug(f"{company_tickers_json} is up to date")

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
    if not _ticker_cik_cache:
        update_company_tickers()
    try:
        return _ticker_cik_cache[ticker.upper()]
    except KeyError:
        raise ValueError(f"Ticker '{ticker}' not found in CIK cache.")

def sec_data(ticker: str):
    cik = get_cik(ticker)
    logger.info(f"Processing ticker: {ticker}  CIK: {cik}")

    os.makedirs(f"data/cache/{ticker.lower()}", exist_ok=True)

    for metric, tag_list in TAGS.items():
        path = f"data/cache/{ticker.lower()}/{metric}.json"
        if is_cache_expired(path):
            for tag in tag_list:
                time.sleep(2)  # avoid SEC rate limits
                namespace, tagname = tag.split(":")
                url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{namespace}/{tagname}.json"
                logger.debug(f"Requesting: {url}")

                try:
                    response = requests.get(url, headers=HEADERS, timeout=10)
                    logger.debug(f"Tag fetch response: {response.status_code}")
                    response.raise_for_status()

                    data = response.json()

                    # Save result to cache
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f)

                    logger.info(f"Saved {metric} data using tag: {tag}")
                    break  # success, move on to next metric

                except requests.HTTPError as e:
                    logger.warning(f"Tag failed for {metric} ({tag}): {e}")
                except Exception as e:
                    logger.error(f"Unexpected error fetching tag {tag} for {ticker}: {e}")

