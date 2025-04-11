#!/usr/bin/env python3

import os
import unittest
from unittest.mock import patch, Mock
from EDGAR_utils import (
        get_cik,
        ticker_cik_map,
        fetch_tag_data,
        extract_last_5_10k_values,
)

# Sample data that mimics what the SEC returns
mock_sec_response = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc"},
    "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft Corp"}
}

class TestCIKLookup(unittest.TestCase):

    def setUp(self):
        self.test_filename = "test_tickers.txt"
        with open(self.test_filename, "w") as f:
            f.write("AAPL\nMSFT\nINVALID\n")

    @patch("EDGAR_utils.requests.get")
    def test_http_error_raises(self, mock_get):
        mock_get.return_value = Mock(status_code=500)
        
        with self.assertRaises(Exception):
            get_cik("AAPL")

    @patch("EDGAR_utils.requests.get")
    def test_valid_ticker(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response
        
        self.assertEqual(get_cik("AAPL"), "0000320193")

    @patch("EDGAR_utils.requests.get")
    def test_case_insensitive(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response
        
        self.assertEqual(get_cik("msft"), "0000789019")

    @patch("EDGAR_utils.requests.get")
    def test_invalid_ticker_raises(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response
        
        with self.assertRaises(ValueError):
            get_cik("ZZZZ")

    @patch("EDGAR_utils.requests.get")
    def test_ticker_cik_map(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response

        result = ticker_cik_map(self.test_filename)
        self.assertEqual(result["AAPL"], "0000320193")
        self.assertEqual(result["MSFT"], "0000789019")
        self.assertIsNone(result["INVALID"])

    def tearDown(self):
        if os.path.exists("test_tickers.txt"):
            os.remove("test_tickers.txt")

class TestTagDataExtraction(unittest.TestCase):

    @patch("EDGAR_utils.requests.get")
    def test_fetch_tag_data_success(self, mock_get):
        mock_json = {
            "entityName": "Microsoft Corp",
            "units": {
                "USD": [
                    {"form": "10-K", "end": "2023-06-30", "val": 1000},
                    {"form": "10-K", "end": "2022-06-30", "val": 900},
                    {"form": "10-K", "end": "2021-06-30", "val": 800},
                    {"form": "10-K", "end": "2020-06-30", "val": 700},
                    {"form": "10-K", "end": "2019-06-30", "val": 600},
                    {"form": "10-K", "end": "2018-06-30", "val": 500},  # Should be excluded (only top 5)
                    {"form": "10-Q", "end": "2023-03-31", "val": 999},  # Should be ignored
                    {"form": "10-K", "end": "2023-06-30", "val": 1000},  # Duplicate
                ]
            }
        }
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = mock_json
        mock_get.return_value = mock_response

        cik = "0000789019"
        tag = "NetCashProvidedByUsedInOperatingActivities"
        data = fetch_tag_data(cik, tag)

        self.assertIn("entityName", data)
        self.assertEqual(data["entityName"], "Microsoft Corp")

        values = extract_last_5_10k_values(data)
        self.assertEqual(len(values), 5)
        self.assertEqual(values[0]["end"], "2023-06-30")
        self.assertEqual(values[-1]["end"], "2019-06-30")
        self.assertTrue(all(entry["form"] == "10-K" for entry in values))

if __name__ == "__main__":
    unittest.main()
