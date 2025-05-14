from datetime import date
from .database import (
    save_prices,
    log_price_fetch,
    latest_price_date,
)

def ingest_prices_if_needed(conn, ticker, prices):
    today = date.today().isoformat()
    last_date = latest_price_date(conn, ticker)

    if last_date == today:
        print(f"[SKIP] {ticker}: already have today's data ({today})")
        return False

    print(f"[FETCH] {ticker}: saving {len(prices)} price records")
    save_prices(conn, ticker, prices)
    log_price_fetch(conn, ticker)
    return True
