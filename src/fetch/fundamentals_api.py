# src/fetch/fundamentals_api.py

import requests
import os
import sqlite3
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"
DB_FILE = "data/stocks.db"

_cache = {}

def get_fundamentals(ticker):
    if ticker in _cache and "fundamentals" in _cache[ticker]:
        return _cache[ticker]["fundamentals"]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fundamentals_data (
            ticker TEXT PRIMARY KEY,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fundamentals_json TEXT
        );
    """)

    cursor.execute("""
        SELECT fetched_at, fundamentals_json FROM fundamentals_data WHERE ticker = ?
    """, (ticker,))
    row = cursor.fetchone()

    if row:
        fetched_at = datetime.fromisoformat(row[0])
        if datetime.now() - fetched_at < timedelta(days=1):
            fundamentals = json.loads(row[1])
            _cache.setdefault(ticker, {})["fundamentals"] = fundamentals
            conn.close()
            return fundamentals

    url = f"{BASE_URL}/income-statement/{ticker}?limit=5&apikey={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    fundamentals = []
    for entry in data:
        fundamentals.append({
            "date": entry["date"],
            "revenue": entry.get("revenue"),
            "netIncome": entry.get("netIncome"),
            "fcf": entry.get("freeCashFlow")
        })

    _cache.setdefault(ticker, {})["fundamentals"] = fundamentals
    cursor.execute("""
        INSERT INTO fundamentals_data (ticker, fetched_at, fundamentals_json)
        VALUES (?, CURRENT_TIMESTAMP, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            fetched_at = excluded.fetched_at,
            fundamentals_json = excluded.fundamentals_json
    """, (ticker, json.dumps(fundamentals)))
    conn.commit()
    conn.close()

    return fundamentals

def get_profile_data(ticker):
    if ticker in _cache and "profile" in _cache[ticker]:
        return _cache[ticker]["profile"]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile_data (
            ticker TEXT PRIMARY KEY,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profile_json TEXT
        );
    """)

    cursor.execute("""
        SELECT fetched_at, profile_json FROM profile_data WHERE ticker = ?
    """, (ticker,))
    row = cursor.fetchone()

    if row:
        fetched_at = datetime.fromisoformat(row[0])
        if datetime.now() - fetched_at < timedelta(days=1):
            profile = json.loads(row[1])
            _cache.setdefault(ticker, {})["profile"] = profile
            conn.close()
            return profile

    try:
        url = f"{BASE_URL}/profile/{ticker}?apikey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        profile = data[0] if data else {}
    except Exception:
        profile = {}

    _cache.setdefault(ticker, {})["profile"] = profile
    cursor.execute("""
        INSERT INTO profile_data (ticker, fetched_at, profile_json)
        VALUES (?, CURRENT_TIMESTAMP, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            fetched_at = excluded.fetched_at,
            profile_json = excluded.profile_json
    """, (ticker, json.dumps(profile)))
    conn.commit()
    conn.close()

    return profile

def get_market_cap(ticker):
    profile = get_profile_data(ticker)
    raw = profile.get("mktCap")
    if isinstance(raw, (int, float)):
        if raw >= 1_000_000_000_000:
            return f"{raw / 1_000_000_000_000:.1f}T"
        elif raw >= 1_000_000_000:
            return f"{raw / 1_000_000_000:.1f}B"
        elif raw >= 1_000_000:
            return f"{raw / 1_000_000:.1f}M"
        else:
            return f"{raw:,.0f}"
    return "(no data)"
