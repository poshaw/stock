# src/ticker.py

from dataclasses import dataclass, field
import os
import json
import logging
import requests
from src.config import HEADERS
from src.domestic import ensure_dir
from src.sic_sector_map import SIC_SECTOR_MAP
from src.tag_map import TAGS

logger = logging.getLogger("ticker")

@dataclass
class Ticker:
    symbol: str
    cik: str = field(init=False)
    company_name: str = field(init=False)
    exchange: str = field(init=False)
    sector: str = field(init=False, default="Unknown")
    submission_data: dict = field(init=False, repr=False)
    metrics: dict = field(default_factory=dict)

    def __post_init__(self):
        self.symbol = self.symbol.upper()
        self.submission_data = self._load_or_fetch_submissions()
        self._extract_metadata()
        self._determine_filer_type()

    def _load_or_fetch_submissions(self):
        """Loads SEC submission data from cache or fetches from SEC.gov if not cached."""
        path = f"data/cache/{self.symbol}/submissions.json"

        if os.path.exists(path):
            logger.debug(f"{self.symbol}: Loading cached submissions from {path}")
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        # If not cached, fetch from SEC
        cik = self._find_cik_from_master()
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        logger.debug(f"{self.symbol}: Fetching submissions from SEC: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        ensure_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
            logger.debug(f"{self.symbol}: Submissions cached to {path}")

        return data

    def _find_cik_from_master(self):
        """Looks up the CIK in company_tickers.json, downloading if needed."""
        path = "data/cache/company_tickers.json"

        if os.path.exists(path):
            logger.debug("Loading cached company_tickers.json")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            url = "https://www.sec.gov/files/company_tickers.json"
            logger.debug(f"Fetching company_tickers.json from SEC: {url}")
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            ensure_dir(path)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
                logger.debug(f"company_tickers.json cached to {path}")

        for record in data.values():
            if record["ticker"].upper() == self.symbol:
                return str(record["cik_str"]).zfill(10)

        raise ValueError(f"CIK not found for ticker {self.symbol}")

    def _extract_metadata(self):
        """Extract metadata like CIK, company name, exchange, and sector."""
        self.cik = self.submission_data.get("cik", "").zfill(10)
        self.company_name = self.submission_data.get("name", "Unknown")
        exchanges = self.submission_data.get("exchanges", [])
        self.exchange = exchanges[0] if exchanges else "Unknown"
        sic = self.submission_data.get("sic", "")
        self.sector = SIC_SECTOR_MAP.get(str(sic)[:2], "Unknown") if sic else "Unknown"

    def _determine_filer_type(self):
        try:
            forms = self.submission_data.get("filings", {}).get("recent", {}).get("form", [])
            self.is_foreign = any(f.strip().upper() == "20-F" for f in forms)
            logger.debug(f"{self.symbol}: Filing type determined → {'Foreign (20-F)' if self.is_foreign else 'Domestic (GAAP)'}")
        except Exception as e:
            logger.warning(f"{self.symbol}: Failed to determine filer type, defaulting to Domestic. Error: {e}")
            self.is_foreign = False

    def load_operating_cash_flow(self):
        tag_key = "operating_cash_flow"
        tag_list = TAGS[tag_key]

        if tag_key in self.metrics:
            logger.debug(f"{self.symbol}: Using cached metric for {tag_key}")
            return

        # Attempt to load from cache file
        cache_path = f"data/cache/{self.symbol}/{tag_key}.json"
        if os.path.exists(cache_path):
            logger.debug(f"{self.symbol}: Loading {tag_key} from cache")
            with open(cache_path, "r", encoding="utf-8") as f:
                self.metrics[tag_key] = json.load(f)
            return
