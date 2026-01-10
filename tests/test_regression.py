import unittest
from datetime import datetime
import sys
import os
sys.path.append(os.getcwd())

class TestRegression2025(unittest.TestCase):
    def test_parse_tab_date_with_year(self):
        from src.utils import parse_tab_date
        
        # Case 1: Tab name implies 12/12. If year=2025, should be 2025-12-12
        tab_name = "1212"
        dt = parse_tab_date(tab_name, year=2025)
        self.assertEqual(dt.year, 2025)
        self.assertEqual(dt.month, 12)
        self.assertEqual(dt.day, 12)

        # Case 2: No year provided -> Defaults to Config YEAR (2026)
        from src.config import YEAR
        dt_default = parse_tab_date(tab_name)
        self.assertEqual(dt_default.year, YEAR)

    def test_parse_col_date_with_year(self):
        from src.utils import parse_col_date
        
        # Case 1: "Dec 16" with year=2025
        dt = parse_col_date("Dec 16", year=2025)
        self.assertEqual(dt.year, 2025)
        self.assertEqual(dt.month, 12)
        self.assertEqual(dt.day, 16)
        
        # Case 2: "16.12" with year=2024
        dt2 = parse_col_date("16.12", year=2024)
        self.assertEqual(dt2.year, 2024)

if __name__ == '__main__':
    unittest.main()
