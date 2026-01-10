import unittest
import re
import sys
import os
sys.path.append(os.getcwd())
from datetime import datetime

class TestTabNaming(unittest.TestCase):
    def test_next_serial_number(self):
        # Mock existing tab names
        existing_tabs = [
            "run 1 [2025-01-01_10-00-00]",   # Old format
            "Run 2 - [09/01/2026 22:18:51]", # New format
            "Dashboard",                     # Irrelevant
            "Run 5 - [10/01/2026 00:00:00]"  # Highest
        ]
        
        target_pattern = re.compile(r"^(?:run|Run)\s+(\d+).*")
        max_run = 0
        
        for t in existing_tabs:
            m = target_pattern.match(t)
            if m:
                print(f"Matched: '{t}' -> Num: {m.group(1)}")
                num = int(m.group(1))
                if num > max_run:
                    max_run = num
                    
        self.assertEqual(max_run, 5)
        next_run = max_run + 1
        self.assertEqual(next_run, 6)
        
        # Verify new format generation
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        new_name = f"Run {next_run} - [{now_str}]"
        print(f"Generated: {new_name}")
        
        self.assertTrue(new_name.startswith("Run 6 - ["))
        self.assertTrue(re.match(r"Run 6 - \[\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\]", new_name))

    def test_parse_tab_datetime(self):
        from src.utils import parse_tab_datetime
        
        # 1. Test New Format
        dt = parse_tab_datetime("Run 5 - [10/01/2026 22:30:15]")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 10)
        self.assertEqual(dt.hour, 22)
        
        # 2. Test Old Format
        dt_old = parse_tab_datetime("run 1 [2025-12-25_10-00-00]")
        self.assertIsNotNone(dt_old)
        self.assertEqual(dt_old.year, 2025)
        self.assertEqual(dt_old.month, 12)
        
        # 3. Test Invalid
        self.assertIsNone(parse_tab_datetime("Random Tab Name"))

if __name__ == '__main__':
    unittest.main()
