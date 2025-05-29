# src/sec.py

from src.config import HEADERS
import os
import json
import requests
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger("sec")

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def is_cache_stale(path, max_age_days):
    if not os.path.exists(path):
        return True
    age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))
    return age > timedelta(days=max_age_days)

def load_cached_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_cache(path, data):
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def get_cached_or_fetch_json(path, fetch_func, max_age_days, force=False):
    if not force and not is_cache_stale(path, max_age_days):
        logger.debug(f"Loading cached data: {path}")
        return load_cached_json(path)

    logger.info(f"Fetching fresh data for: {path}")
    data = fetch_func()
    write_json_cache(path, data)
    return data

def get_cik(ticker: str, force=False):
    cache_path = "data/cache/company_tickers.json"

    def fetch_cik_master():
        time.sleep(1)  # Give the SEC some breathing room
        url = "https://www.sec.gov/files/company_tickers.json"

        logger.debug(f"Requesting: {url} with headers: {HEADERS}")

        response = requests.get(url, headers=HEADERS)

        logger.debug(f"SEC response status: {response.status_code}")

        response.raise_for_status()
        return response.json()

    data = get_cached_or_fetch_json(
        path=cache_path,
        fetch_func=fetch_cik_master,
        max_age_days=30,
        force=force
    )

    ticker = ticker.upper()
    for entry in data.values():
        if entry.get("ticker") == ticker:
            return str(entry["cik_str"]).zfill(10)

    raise ValueError(f"CIK not found for ticker: {ticker}")
