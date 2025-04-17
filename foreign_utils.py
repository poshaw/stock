import re
import logging
import requests
from bs4 import BeautifulSoup
from EDGAR_tags import HEADERS
import time
from requests.exceptions import HTTPError


logger = logging.getLogger("foreign_utils")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

BASE_ARCHIVES_URL = "https://www.sec.gov/Archives/"


session = requests.Session()


def safe_get(url, max_retries=5, base_delay=1.0, backoff=2.0):
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers={
                **HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            })
            response.raise_for_status()
            return response
        except HTTPError as e:
            wait = base_delay * (backoff ** attempt)
            logger.warning(f"GET failed ({attempt + 1}/{max_retries}) for {url}: {e}. Retrying in {wait:.1f}s.")
            time.sleep(wait)
    raise Exception(f"All {max_retries} attempts failed for URL: {url}")


def get_recent_20f_filings(cik, count=5):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    logger.debug(f"Fetching recent filings from: {url}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    results = []
    filings = data.get("filings", {}).get("recent", {})
    for form, date, accession in zip(filings.get("form", []),
                                     filings.get("filingDate", []),
                                     filings.get("accessionNumber", [])):
        if form.upper() != "20-F":
            continue
        acc = accession.replace("-", "")
        file_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{acc}-index.htm"
        results.append({"date": date, "url": file_url})
        if len(results) >= count:
            break

    return results


def fetch_20f_html(index_url):
    logger.debug(f"Fetching 20-F index HTML from: {index_url}")
    response = safe_get(index_url)
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        if "20-f" in link.text.lower() or "form 20-f" in link.text.lower():
            href = link["href"]
            if not href.startswith("http"):
                href = BASE_ARCHIVES_URL + href.lstrip("/")
            return fetch_full_20f_text(href)

    raise Exception("20-F document link not found in filing index.")

def fetch_full_20f_text(full_url):
    logger.debug(f"Fetching full 20-F text from: {full_url}")
    response = safe_get(full_url)
    return response.text


def extract_metric_from_20f(html_text, tags):
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(" ", strip=True)

    for tag in tags:
        pattern = re.compile(rf"{tag}[^\d\$]*([\$\d,\.\(\)-]+)", re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            for match in matches:
                try:
                    cleaned = match.replace("$", "").replace(",", "").strip()
                    value = int(float(cleaned.replace("(", "-").replace(")", "")))
                    return value
                except ValueError:
                    continue

    return None


def get_foreign_metric_data(ticker, cik, metric_key, tag_list):
    logger.debug(f"Getting foreign metric data for {ticker}, CIK {cik}, metric '{metric_key}'")
    filings = get_recent_20f_filings(cik)
    data = []

    for filing in filings:
        time.sleep(0.5)  # Respectful crawling delay
        try:
            html = fetch_20f_html(filing["url"])
            value = extract_metric_from_20f(html, tag_list)
            if value is not None:
                data.append({
                    "form": "20-F",
                    "end": filing["date"],
                    "val": value
                })
        except Exception as e:
            logger.warning(f"Error processing {filing['url']}: {e}")
            continue

    return data
