import unittest
import pandas as pd
import sys
import os
sys.path.append(os.getcwd())
from datetime import datetime
from src.etl import process_worksheet, run_etl_pipeline

# Mock Worksheet
class MockSheet:
    def __init__(self, title, data):
        self.title = title
        self._data = data

    def get_all_values(self):
        return self._data

class MockClient:
    def open_by_key(self, key):
        return MockSpreadsheet()

class MockSpreadsheet:
    def worksheets(self):
        return [] # Not used in this specific test of logic
    def worksheet(self, title):
        return None

class TestETLLogic(unittest.TestCase):
    def test_mixed_sheets_date_coalescing(self):
        # Sheet 1: Pivotable (has date header)
        # Title: 0101 (Jan 1st)
        # Schema relies on value being the user_name
        ws1_data = [
            ["Role", "01/01"],
            ["ModelA", ""],
            ["Admin", "Alice"]
        ]
        ws1 = MockSheet("0101", ws1_data)
        
        # Sheet 2: Not Pivotable (no date header)
        # Title: 0201 (Jan 2nd)
        # Processed as-is. Logic will treat this as a row with 'tab_date'.
        ws2_data = [
            ["user_name", "Count"],
            ["ModelA", ""],
            ["Bob", "50"]
        ]
        ws2 = MockSheet("0201", ws2_data)

        # 1. Process individually
        df1 = process_worksheet(ws1)
        df2 = process_worksheet(ws2)

        # 2. Simulate pipeline concat + fix
        dfs = [df1, df2]
        df = pd.concat(dfs, ignore_index=True)

        # Normalize columns normally happens here, let's mock it roughly if needed, 
        # but here we just cared about 'date' vs 'tab_date'.
        
        # Mimic the ETL logic block
        if "tab_date" in df.columns:
            if "date" not in df.columns:
                df["date"] = df["tab_date"]
            else:
                df["date"] = df["date"].fillna(df["tab_date"])

        print("Combined (Post-Fix):")
        print(df[["user_name", "date"] if "user_name" in df.columns else df.columns])

        # 3. Assertions
        # Row 0: Alice (from melted sheet)
        # Verify first row
        row0 = df.iloc[0]
        # logic: value -> user_name. So Alice should be user_name.
        self.assertEqual(row0["user_name"], "Alice")
        self.assertEqual(row0["date"], datetime(2025, 1, 1))

        # Row 1: Bob (from non-melted sheet)
        row1 = df.iloc[1]
        self.assertEqual(row1["user_name"], "Bob")
        self.assertEqual(row1["date"], datetime(2025, 1, 2))

if __name__ == '__main__':
    unittest.main()
