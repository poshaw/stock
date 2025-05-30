# src/ticker.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import inspect
import json
import logging
import os
import requests
from src.config import HEADERS
from src.domestic import ensure_dir
from src.sic_sector_map import SIC_SECTOR_MAP
from src.tag_map import TAGS

logger = logging.getLogger("ticker")


@dataclass
class Ticker:
    """
    Represents a stock ticker and encapsulates logic to retrieve and cache SEC data.

    Attributes:
    ----------
    ticker : str
        Ticker symbol (e.g., "AAPL", "MSFT").
    cik : str
        Central Index Key assigned by the SEC (set after initialization).
    company_name : str
        Name of the company associated with the ticker.
    exchange : str
        Primary exchange where the ticker is listed (e.g., "NYSE", "Nasdaq").
    sector : str
        Broad industry sector determined via SIC code mapping.
    submission_data : dict
        Raw data loaded from SEC submissions endpoint.
    metrics : dict
        Cached financial metrics, such as operating cash flow.
    is_foreign : bool
        Whether the company files 20-F (foreign) or 10-K (domestic).
    """
    ticker: str
    cik: str = field(init=False)
    company_name: str = field(init=False)
    exchange: str = field(init=False)
    sector: str = field(init=False, default="Unknown")
    is_foreign: bool = field(init=False)
    submission_data: dict = field(init=False, repr=False)
    metrics: dict = field(default_factory=dict)

    def __post_init__(self):
        logger.debug(f"method {inspect.currentframe().f_code.co_name} called")
        self.ticker = self.ticker.upper()
        self.submission_data = self._load_or_fetch_submissions()
        self._extract_metadata()
        self._determine_filer_type()

    def _is_cache_expired(self, path: str, max_age_days: int = 7) -> bool:
        if not os.path.exists(path):
            logger.debug(f"{self.ticker}: Cache check → {path} does not exist")
            return True

        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        age = datetime.now() - mtime
        if age > timedelta(days=max_age_days):
            logger.debug(f"{self.ticker}: Cache expired for {path} (age: {age.days} days)")
            return True

        logger.debug(f"{self.ticker}: Cache valid for {path} (age: {age.days} days)")
        return False

    def _load_or_fetch_submissions(self, max_age_days=7):
        logger.debug(f"method {inspect.currentframe().f_code.co_name} called")
        path = f"data/cache/{self.ticker}/submissions.json"

        if not self._is_cache_expired(path, max_age_days):
            logger.debug(f"{self.ticker}: Loading cached submissions from {path}")
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        cik = self._find_cik_from_master()
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        logger.debug(f"{self.ticker}: Fetching submissions from SEC: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        ensure_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
            logger.debug(f"{self.ticker}: Submissions cached to {path}")

        return data

    def _find_cik_from_master(self, max_age_days=7):
        path = "data/cache/company_tickers.json"

        if not self._is_cache_expired(path, max_age_days):
            logger.debug(f"{self.ticker}: Loading cached CIK data from {path}")
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
            if record["ticker"].upper() == self.ticker:
                return str(record["cik_str"]).zfill(10)

        raise ValueError(f"CIK not found for ticker {self.ticker}")

    def _extract_metadata(self):
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
            logger.debug(f"{self.ticker}: Filing type determined → {'Foreign (20-F)' if self.is_foreign else 'Domestic (GAAP)'}")
        except Exception as e:
            logger.warning(f"{self.ticker}: Failed to determine filer type, defaulting to Domestic. Error: {e}")
            self.is_foreign = False

    def load_operating_cash_flow(self, max_age_days=7):
        tag_key = "operating_cash_flow"
        tag_list = TAGS[tag_key]

        if tag_key in self.metrics:
            logger.debug(f"{self.ticker}: Using in-memory metric for {tag_key}")
            return

        path = f"data/cache/{self.ticker}/{tag_key}.json"

        if not self._is_cache_expired(path, max_age_days):
            logger.debug(f"{self.ticker}: Loading {tag_key} from cache")
            with open(path, "r", encoding="utf-8") as f:
                self.metrics[tag_key] = json.load(f)
            return

        logger.debug(f"{self.ticker}: No fresh cache for {tag_key} — metric needs to be fetched externally")

    def __str__(self):
        lines = [
            "\n" + "=" * 60,
            f" Company : {self.company_name}",
            f" Ticker  : {self.ticker}",
            f" CIK     : {self.cik}",
            f" Sector  : {self.sector}",
            f" Exchange: {self.exchange}",
            ""
        ]

        ocf_data = self.metrics.get("operating_cash_flow")
        if ocf_data:
            lines.append(" Operating Cash Flow (last 5 years):")
            for entry in ocf_data:
                lines.append(f"   {entry['end']}: ${entry['val']:,}")
        else:
            lines.append(" Operating Cash Flow: [No data available]")

        lines.append("=" * 60)
        return "\n".join(lines)

    def __repr__(self):
        return f"<Ticker {self.ticker} ({self.exchange}) CIK={self.cik}>"

