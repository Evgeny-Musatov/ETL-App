import unittest
import pandas as pd
import sys
import os
sys.path.append(os.getcwd())
from datetime import datetime
from src.etl import process_worksheet
from src.config import YEAR

# Mock Worksheet
class MockSheet:
    def __init__(self, title, data):
        self.title = title
        self._data = data

    def get_all_values(self):
        return self._data

class TestDateOverride(unittest.TestCase):
    def test_tab_date_overrides_header(self):
        # Scenario: Tab says "2212" (Dec 22), Header says "12.12" (Dec 12)
        # We want Dec 22 (from Tab)
        
        ws_data = [
            ["Role", "12.12"], # Header implies Dec 12
            ["MyModel", ""],    # REQUIRED: Model Header Row
            ["Admin", "Alice"]
        ]
        ws = MockSheet("2212", ws_data) # Tab implies Dec 22
        
        df = process_worksheet(ws)
        
        print("Resulting DataFrame:")
        print(df)
        
        # Expectation: date column is Dec 22, 2025
        expected_date = datetime(YEAR, 12, 22)
        actual_date = df.iloc[0]["date"]
        
        self.assertEqual(actual_date, expected_date, f"Date should be {expected_date} (Tab), but got {actual_date} (Header)")

if __name__ == '__main__':
    unittest.main()
