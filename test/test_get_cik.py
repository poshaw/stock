#!/usr/bin/env python3

import unittest
from get_cik import get_cik_for_ticker

class TestGetCIK(unittest.TestCase):

    def test_valid_ticker(self):
        cik = get_cik_for_ticker("AAPL")
        self.assertEqual(cik, "0000320193")

    def test_ticker_case_insensitive(self):
        cik = get_cik_for_ticker("msft")
        self.assertEqual(cik, "0000789019")

    def test_invalid_ticker(self):
        with self.assertRaises(ValueError):
            get_cik_for_ticker("INVALID123")

if __name__ == "__main__":
    unittest.main()
