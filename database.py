import sqlite3

def get_db_connection():
    return sqlite3.connect("edgar_data.db")

def create_table_if_not_exists(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edgar_metrics (
            ticker TEXT,
            date TEXT,
            metric TEXT,
            value INTEGER,
            PRIMARY KEY (ticker, date, metric)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fetch_log (
            ticker TEXT,
            metric TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticker_cik (
            ticker TEXT PRIMARY KEY,
            cik TEXT
        );
    """)
    conn.commit()


def insert_metric_data(conn, ticker, metric_key, entries):
    cursor = conn.cursor()
    for entry in entries:
        if entry.get("form") != "10-K":
            continue

        end_date = entry.get("end")
        value = entry.get("val")

        if not end_date or value is None:
            continue

        sql = """
            INSERT INTO edgar_metrics (ticker, date, metric, value)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ticker, date, metric) DO UPDATE SET value = excluded.value
        """
        cursor.execute(sql, (ticker, end_date, metric_key, value))
    conn.commit()

def log_fetch(conn, ticker, metric):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fetch_log (ticker, metric)
        VALUES (?, ?)
    """, (ticker, metric))
    conn.commit()

def was_fetched_recently(conn, ticker, metric, days=7):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(fetched_at) FROM fetch_log
        WHERE ticker = ? AND metric = ? AND fetched_at > datetime('now', ?)
    """, (ticker, metric, f'-{days} days'))
    recent = cursor.fetchone()[0]
    return bool(recent)

def prune_old_fetch_logs(conn, months=3):
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM fetch_log
        WHERE fetched_at < datetime('now', ?)
    """, (f'-{months} months',))
    conn.commit()

def get_cik_from_db(conn, ticker):
    cursor = conn.cursor()
    cursor.execute("SELECT cik FROM ticker_cik WHERE ticker = ?", (ticker.upper(),))
    result = cursor.fetchone()
    return result[0] if result else None

def save_cik_to_db(conn, ticker, cik):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ticker_cik (ticker, cik)
        VALUES (?, ?)
        ON CONFLICT(ticker) DO UPDATE SET cik = excluded.cik
    """, (ticker.upper(), cik))
    conn.commit()
