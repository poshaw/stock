# tests/test_utils.py
import os
import tempfile
from datetime import datetime, timedelta
from src.utils import (
        is_cache_stale,
        ensure_dir,
)

def test_is_cache_stale_new_file(tmp_path):
    f = tmp_path / "test.json"
    f.write_text("hello")
    assert is_cache_stale(str(f), max_age_days=1) is False

def test_is_cache_stale_missing_file(tmp_path):
    f = tmp_path / "missing.json"
    assert is_cache_stale(str(f), max_age_days=1) is True

def test_ensure_dir_creates_parent(tmp_path):
    f = tmp_path / "a" / "b" / "file.json"
    ensure_dir(str(f)) # should create a/b
    assert os.path.isdir(f.parent)

