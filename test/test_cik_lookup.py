#!/usr/bin/env python3

import os
import unittest
from unittest.mock import patch, Mock
from cik_lookup import get_cik, ticker_cik_map

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

    @patch("cik_lookup.requests.get")
    def test_http_error_raises(self, mock_get):
        mock_get.return_value = Mock(status_code=500)
        
        with self.assertRaises(Exception):
            get_cik("AAPL")

    @patch("cik_lookup.requests.get")
    def test_valid_ticker(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response
        
        self.assertEqual(get_cik("AAPL"), "0000320193")

    @patch("cik_lookup.requests.get")
    def test_case_insensitive(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response
        
        self.assertEqual(get_cik("msft"), "0000789019")

    @patch("cik_lookup.requests.get")
    def test_invalid_ticker_raises(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_sec_response
        
        with self.assertRaises(ValueError):
            get_cik("ZZZZ")

    @patch("cik_lookup.requests.get")
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

if __name__ == "__main__":
    unittest.main()