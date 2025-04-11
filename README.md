# 📈 Stock: SEC EDGAR Data Tracker

This Python script fetches, stores, and analyzes financial data for public companies using SEC EDGAR filings.

## 🚀 Features

- Pulls financial data (e.g., Operating Cash Flow) from [sec.gov](https://www.sec.gov) EDGAR XBRL API
- Tracks multiple tickers defined in `tickers.txt`
- Stores data in a local SQLite database (`edgar_data.db`)
- Skips duplicate SEC requests by logging fetch times
- CLI interface with verbosity flags (`-v`, `-vv`)
- Easily extendable to support additional financial metrics

---

## ⚙️ Setup

```bash
git clone git@github.com:poshaw/stock.git
cd stock
```

Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
```

Install dependencies:
```bash
python -m pip install --upgrade pip requests
```

---

## 🧪 Run Tests

```bash
python -m unittest discover -s test
```

---

## 📊 Usage

```bash
python main.py -v
```

- `-v`: enables INFO-level output
- `-vv`: enables DEBUG-level output

The script will:
- Loop over tickers in `tickers.txt`
- Pull the latest 10-K Operating Cash Flow data
- Store it in `edgar_data.db`
- Avoid redundant SEC calls if fetched within the last week

---


