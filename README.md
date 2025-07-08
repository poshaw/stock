# 📈 Stock: SEC EDGAR Data Tracker

A Python-based CLI tool to fetch, cache, and analyze financial data for public companies using SEC EDGAR filings.

## 🚀 Features

- Pulls structured financial data (e.g., Operating Cash Flow, Net Income, CapEx) via [sec.gov](https://www.sec.gov) XBRL API
- Supports both US GAAP (`10-K`, `10-Q`) and IFRS (`20-F`) filers
- Smart caching system avoids redundant requests and saves bandwidth
- Customizable ticker tracking via `tickers.csv`
- SQLite integration (optional) for historical persistence (`edgar_data.db`)
- CLI-based control with logging verbosity and cache override options
- Easily extendable with custom financial metrics and tag mappings

---

## ⚙️ Setup

```bash
git clone https://github.com/poshaw/stock.git
cd stock


Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
source .venv/Scripts/activate # Windows
```

Install dependencies:
```bash
python -m pip install --upgrade pip requests beautifulsoup4
```

---

## 🧪 Run Tests

```bash
python -m unittest discover -s test
```

---

## 📊 Usage

```bash
python -m src.main [OPTIONS]
```

### Common Options

- Fetch data for one or more specific tickers:  
  ``--fetch MSFT TSM``

- Fetch data for all tickers listed in `tickers.csv`:  
  ``--fetchall``

- Force re-fetch all data, ignoring cache:  
  ``--force``

- Set logging verbosity (INFO or DEBUG):  
  ``-v``, ``-vv``


### Examples
```bash
# Fetch all tickers from tickers.csv using cache
python run.py --fetchall

# Fetch all tickers and force fresh data
python run.py --fetchall --force

# Fetch data only for MSFT
python run.py --fetch MSFT

# Force fresh fetch just for TSM
python run.py --fetch TSM --force
```

## 🧠 What It Does
- Loads ticker symbols from tickers.csv (or from --fetch)
- Fetches EDGAR filings and financial metric data via the SEC XBRL API
- Tries multiple fallback tags per metric to increase reliability
- Stores each metric to data/cache/{ticker}/{metric}.json
- Supports both domestic (10-K, 10-Q) and foreign (20-F) filers
- Optionally persists or analyzes data via SQLite (edgar_data.db)

## 🛠️ Extend It
- To track more metrics, add new entries to src/tag_map.py
