# src/utils.py

from datetime import datetime, timedelta
import json
import logging
import os

logger = logging.getLogger("utils")


def is_cache_expired(path: str, max_age_days: int = 7) -> bool:
    if not os.path.exists(path):
        logger.debug(f"No data cached for {path}")
        return true

    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    age = datetime.now() - mtime
    if age > timedelta(days=max_age_days):
        logger.debug(f"Cache expired for {path}")
        return True

    logger.debug(f"Cache valid for {path} (age: {age.days} days)")
    return False
