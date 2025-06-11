# src/import.py

import logging
import requests

from .utils import (
        is_cache_expired,
)

logger = logging.getLogger("import")

def update_company_tickers(max_age_days=7):
    path = "data/cache/company_tickers.json"

    if is_cache_expired(path, max_age_days):
        url = "https://www.sec.gov/files/company_tickers.json"
        logger.debug(f"Fetching company_tickers.json from SEC: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        ensure_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
            logger.debug(f"company_tickers.json cached to {path}")
    else:
        logger.debug(f"{path} is up to date")

def sec_data(ticker):
    logger.debug(f"processing ticker: {ticker}")
