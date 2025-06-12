# tests/test_utils.py
import os
import tempfile
from datetime import datetime, timedelta
from src.utils import is_cache_stale

def test_cache_is_missing():
    assert is_cache_stale("nonexistent.json", ticker="TEST")

def test_cache_is_expired():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = tmp.name
    ten_days_ago = (datetime.now() - timedelta(days=10)).timestamp()
    os.utime(path, (ten_days_ago, ten_days_ago))
    assert is_cache_stale(path, max_age_days=7)

def test_cache_is_fresh():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = tmp.name
    os.utime(path, None)
    assert not is_cache_stale(path, max_age_days=7)

