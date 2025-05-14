# src/fetch/sec.py

import requests
import os
import time
import sqlite3
import json
from .sec_headers import HEADERS

SEC_DB = "data/stocks.db"
BASE_XBRL_URL = "https://data.sec.gov/api/xbrl/companyconcept"


def get_cik(ticker):
    ticker = ticker.lower()
    conn = sqlite3.connect(SEC_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_cache (
            ticker TEXT PRIMARY KEY,
            tag TEXT,
            fetched_at TEXT,
            raw_json TEXT
        );
    """)

    cursor.execute("""
        SELECT raw_json FROM sec_cache WHERE tag = 'ticker_map'
    """)
    row = cursor.fetchone()
    data = {}

    if row:
        data = json.loads(row[0])
        for entry in data.values():
            if entry["ticker"].lower() == ticker:
                conn.close()
                return str(entry["cik_str"]).zfill(10)

    print(f"[SEC] Fetching company_tickers.json")
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    cursor.execute("""
        INSERT OR REPLACE INTO sec_cache (ticker, tag, fetched_at, raw_json)
        VALUES (?, 'ticker_map', datetime('now'), ?)
    """, ("__ticker_map__", json.dumps(data)))
    conn.commit()
    conn.close()

    for entry in data.values():
        if entry["ticker"].lower() == ticker:
            return str(entry["cik_str"]).zfill(10)

    raise ValueError(f"CIK not found for ticker: {ticker}")


def fetch_tag_data(cik, tag):
    url = f"{BASE_XBRL_URL}/CIK{cik}/us-gaap/{tag}.json"
    print(f"[SEC] Fetching {tag} for CIK {cik} from {url}")
    response = requests.get(url, headers=HEADERS)
    time.sleep(0.5)
    response.raise_for_status()
    return response.json()


def get_sec_value(ticker, tag):
    conn = sqlite3.connect(SEC_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_cache (
            ticker TEXT,
            tag TEXT,
            fetched_at TEXT,
            raw_json TEXT,
            PRIMARY KEY (ticker, tag)
        );
    """)

    cursor.execute("""
        SELECT raw_json FROM sec_cache WHERE ticker = ? AND tag = ?
    """, (ticker, tag))
    row = cursor.fetchone()

    if row:
        print(f"[SEC] Loaded {tag} for {ticker} from cache.")
        data = json.loads(row[0])
    else:
        cik = get_cik(ticker)
        data = fetch_tag_data(cik, tag)
        cursor.execute("""
            INSERT OR REPLACE INTO sec_cache (ticker, tag, fetched_at, raw_json)
            VALUES (?, ?, datetime('now'), ?)
        """, (ticker, tag, json.dumps(data)))
        conn.commit()

    conn.close()

    try:
        records = data["units"]["USD"]
        annual = [r for r in records if r.get("form") in ("10-K", "20-F")]
        annual.sort(key=lambda x: x["end"], reverse=True)
        return annual[0]["val"]
    except Exception as e:
        print(f"[SEC] Failed to extract {tag}: {e}")
        return None


def get_sec_value_series(ticker, tag):
    conn = sqlite3.connect(SEC_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT raw_json FROM sec_cache WHERE ticker = ? AND tag = ?
    """, (ticker, tag))
    row = cursor.fetchone()

    if row:
        print(f"[SEC] Loaded {tag} for {ticker} from cache.")
        data = json.loads(row[0])
    else:
        cik = get_cik(ticker)
        data = fetch_tag_data(cik, tag)
        cursor.execute("""
            INSERT OR REPLACE INTO sec_cache (ticker, tag, fetched_at, raw_json)
            VALUES (?, ?, datetime('now'), ?)
        """, (ticker, tag, json.dumps(data)))
        conn.commit()

    conn.close()

    try:
        # Try in order of most likely to exist
        for unit in ["USD", "perShareUSD", "USD/shares", "shares"]:
            if unit in data.get("units", {}):
                records = data["units"][unit]
                annual = [r for r in records if r.get("form") in ("10-K", "20-F")]
                annual.sort(key=lambda x: x["end"], reverse=True)
                return [(entry["end"], entry["val"]) for entry in annual]
        raise ValueError("No usable unit found in data")
    except Exception as e:
        print(f"[SEC] Failed to extract historical {tag}: {e}")
        return []


def get_fundamentals(ticker):
    return {
        "netIncome": get_sec_value(ticker, "NetIncomeLoss"),
        "revenue": get_sec_value(ticker, "Revenues"),
        "fcf": get_sec_value(ticker, "NetCashProvidedByUsedInOperatingActivities")
    }


def get_sec_eps(ticker):
    net_income = get_sec_value(ticker, "NetIncomeLoss")
    shares = get_sec_value(ticker, "WeightedAverageNumberOfDilutedSharesOutstanding")
    if isinstance(net_income, (int, float)) and isinstance(shares, (int, float)) and shares > 0:
        return net_income / shares
    return None

