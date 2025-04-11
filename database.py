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
