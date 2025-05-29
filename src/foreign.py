# src/foreign.py

import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import os
import json

from src.config import HEADERS
from src.domestic import get_cached_or_fetch_json

logger = logging.getLogger("foreign")

SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
BASE_ARCHIVES_URL = "https://www.sec.gov/Archives/"

def search_latest_20f_filings(cik, limit=5):
    padded_cik = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
    
    logger.debug(f"Fetching recent filings for CIK {padded_cik}")
    logger.debug(f"Headers being sent to SEC: {HEADERS}")

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    forms = data.get("filings", {}).get("recent", {})
    result = []

    for i, form in enumerate(forms.get("form", [])):
        if form == "20-F":
            accession_number = forms["accessionNumber"][i].replace("-", "")
            filing_date = forms["filingDate"][i]
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/index.json"
            result.append({
                "date": filing_date,
                "url": url
            })
            if len(result) >= limit:
                break

    return result

def get_foreign_filing_index(cik, ticker, force=False, limit=5):
    path = f"data/cache/{ticker.lower()}/20f_index_urls.json"

    def fetch():
        return search_latest_20f_filings(cik, limit=limit)

    return get_cached_or_fetch_json(path, fetch, max_age_days=7, force=force)

def fetch_20f_text(filing_url):
    logger.debug(f"Fetching 20-F filing index from: {filing_url}")
    time.sleep(1)
    response = requests.get(filing_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    doc_links = soup.find_all("a", href=True)
    for link in doc_links:
        if "20-f" in link.text.lower() or "form 20-f" in link.text.lower():
            full_url = BASE_ARCHIVES_URL + link["href"].lstrip("/")
            logger.debug(f"Fetching full 20-F document: {full_url}")
            doc_resp = requests.get(full_url, headers=HEADERS)
            doc_resp.raise_for_status()
            return doc_resp.text

    raise Exception("20-F document not found in index page")

def extract_metric(html_text, tags):
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(" ", strip=True)

    for tag in tags:
        pattern = re.compile(rf"{tag}[^\d\$]*([\$\d,.\(\)-]+)", re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            val = matches[0].replace(",", "").replace("$", "").strip()
            try:
                return int(float(val.replace("(", "-").replace(")", "")))
            except ValueError:
                continue

    return None

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_json_cache(path, data):
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_json_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_foreign_metric_data(ticker, cik, tag_key, tag_search_list, force=False, filing_urls=None):
    path = f"data/cache/{ticker.lower()}/{tag_key}_20F.json"
    if not force:
        cached = load_json_cache(path)
        if cached:
            return cached

    results = []
    filings = filing_urls or search_latest_20f_filings(cik)
    for filing in filings:
        try:
            html = fetch_20f_text(filing["url"])
            val = extract_metric(html, tag_search_list)
            if val is not None:
                results.append({"date": filing["date"], "val": val})
        except Exception as e:
            logger.warning(f"{ticker} {filing['date']}: failed to parse 20-F: {e}")
            continue

    write_json_cache(path, results)
    return results
