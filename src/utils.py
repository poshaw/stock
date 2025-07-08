# src/utils.py

from datetime import datetime, timedelta
import json
import logging
import os
from typing import Optional

logger = logging.getLogger("utils")


def is_cache_stale(path: str, ticker: Optional[str] = None, max_age_days: int = 7) -> bool:
    if ticker and not isinstance(ticker, str):
        raise TypeError(f"Expected ticker to be a string, got {type(ticker)}")

    if not os.path.exists(path):
        logger.debug(f"No data cached for {path}")
        return True

    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    now = datetime.now()

    # Filing-based check if ticker is provided
    if ticker:
        try:
            from .fetch import get_last_filing_date
            last_filing_date = get_last_filing_date(ticker)
            if mtime < last_filing_date:
                logger.debug(f"{ticker}: {path} is older than last filing date ({last_filing_date.date()}) → stale")
                return True
        except Exception as e:
            logger.warning(f"{ticker}: Could not determine filing-based staleness. Error: {e}")

    # Fallback to age check
    age = now - mtime
    if age > timedelta(days=max_age_days):
        logger.debug(f"Cache expired for {path} (age: {age.days} days > {max_age_days} days)")
        return True

    logger.debug(f"Cache valid for {path} (age: {age.days} days)")
    return False


def ensure_dir(path: str):
    """
    Ensures the given path is a directory, or the parent directory of a file path.
    If path ends with .json or similar, it treats it as a file path.
    """
    if os.path.splitext(path)[1]:  # has a file extension
        dir_path = os.path.dirname(path)
    else:
        dir_path = path
    os.makedirs(dir_path, exist_ok=True)

