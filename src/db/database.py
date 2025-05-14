import sqlite3
from datetime import datetime, timedelta

DB_FILE = "data/stocks.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_schema(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_fetch_log (
            ticker TEXT PRIMARY KEY,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

def save_prices(conn, ticker, price_list):
    cursor = conn.cursor()
    for row in price_list:
        cursor.execute("""
            INSERT INTO daily_prices (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume
        """, (
            ticker,
            row["date"],
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["volume"]
        ))
    conn.commit()

def log_price_fetch(conn, ticker):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_fetch_log (ticker, fetched_at)
        VALUES (?, CURRENT_TIMESTAMP)
        ON CONFLICT(ticker) DO UPDATE SET fetched_at = excluded.fetched_at
    """, (ticker,))
    conn.commit()

def latest_price_date(conn, ticker):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(date) FROM daily_prices WHERE ticker = ?
    """, (ticker,))
    row = cursor.fetchone()
    return row[0] if row and row[0] else None # Returns a string like '2025-05-13'

