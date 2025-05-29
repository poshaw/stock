# src/foreign.py

import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import os
import json
from src.config import HEADERS

logger = logging.getLogger("foreign")

SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
BASE_ARCHIVES_URL = "https://www.sec.gov/Archives/"

def search_latest_20f_filings(cik, count=5):
    query = {
        "keys": str(int(cik)),
        "formType": "20-F",
        "start": 0,
        "count": count,
        "sort": "date",
        "order": "desc"
    }
    logger.debug(f"Searching for 20-F filings for CIK {cik}")
    response = requests.post(SEARCH_URL, json=query, headers=HEADERS)
    response.raise_for_status()
    hits = response.json().get("hits", {}).get("hits", [])

    filings = []
    for hit in hits:
        filing = hit["_source"]
        accession = filing["adsh"].replace("-", "")
        url = f"{BASE_ARCHIVES_URL}edgar/data/{filing['cik']}/{accession}/{accession}-index.htm"
        filings.append({"date": filing["filed"], "url": url})

    return filings

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

def get_foreign_metric_data(ticker, cik, tag_key, tag_search_list, force=False):
    path = f"data/cache/{ticker.lower()}/{tag_key}_20F.json"
    if not force:
        cached = load_json_cache(path)
        if cached:
            return cached

    results = []
    filings = search_latest_20f_filings(cik)
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
