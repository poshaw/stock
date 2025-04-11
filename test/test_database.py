import unittest
import sqlite3
from database import get_db_connection, create_table_if_not_exists, insert_metric_data

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_connection()
        create_table_if_not_exists(self.conn)

    def test_insert_and_retrieve_data(self):
        ticker = "MSFT"
        metric = "Operating Cash Flow"
        entries = [
            {"form": "10-K", "end": "2024-06-30", "val": 123456000},
            {"form": "10-K", "end": "2023-06-30", "val": 98765000},
        ]

        insert_metric_data(self.conn, ticker, metric, entries)

        cursor = self.conn.cursor()
        cursor.execute("SELECT ticker, date, metric, value FROM edgar_metrics WHERE ticker = ? ORDER BY date DESC", (ticker,))
        results = cursor.fetchall()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], ticker)
        self.assertEqual(results[0][1], "2024-06-30")
        self.assertEqual(results[0][2], metric)
        self.assertEqual(results[0][3], 123456000)

    def tearDown(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM edgar_metrics WHERE ticker = 'MSFT'")
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    unittest.main()
