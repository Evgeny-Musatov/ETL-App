import sys
import os
sys.path.append(os.getcwd())
try:
    from src.utils import parse_tab_datetime
    print("Import successful")
    dt = parse_tab_datetime("Run 5 - [10/01/2026 22:30:15]")
    print(f"Result: {dt}")
except Exception as e:
    import traceback
    traceback.print_exc()
