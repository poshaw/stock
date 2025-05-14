import csv
import argparse
from src.db import database, ingest
from src.fetch import daily_prices
from src.logic.compare import compare_stocks
import logging

logging.basicConfig(level=logging.DEBUG)

def load_tickers(path="data/tickers.csv"):
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        return [row["ticker"].upper() for row in reader]

def fetch_all():
    conn = database.get_connection()
    database.init_schema(conn)
    tickers = load_tickers()
    for ticker in tickers:
        try:
            prices = daily_prices.get_prices(ticker, limit=30)
            ingest.ingest_prices_if_needed(conn, ticker, prices)
        except Exception as e:
            print(f"[ERROR] Failed to process {ticker}: {e}")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Stock data CLI tool")
    parser.add_argument("--compare", nargs="+", help="Compare tickers by latest close")
    args = parser.parse_args()

    if args.compare:
        compare_stocks([ticker.upper() for ticker in args.compare])
    else:
        fetch_all()

if __name__ == "__main__":
    main()
