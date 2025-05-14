from dotenv import load_dotenv
import os
import requests

load_dotenv()  # Loads from .env in project root

API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_prices(ticker, limit=30):
    url = f"{BASE_URL}/historical-price-full/{ticker}?timeseries={limit}&apikey={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    results = []
    for row in data.get("historical", []):
        results.append({
            "date": row["date"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"]
        })

    return results
