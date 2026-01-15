import json
import os
from datetime import datetime

# Path to config.json (assumed to be in the project root, one level up from src if running from root)
# But since we run from root, it is just "config.json"
CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"⚠️ Config file not found at {CONFIG_PATH}. Creating skeleton...")
        skeleton = {
            "source_sheet_id": "",
            "target_sheet_id": "",
            "service_account_file": "src/gcp-service-account/service_account.json",
            "start_date": "",
            "end_date": ""
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(skeleton, f, indent=4)
        print("✅ Created config.json. Please update it with your settings.")
        return skeleton
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_config = load_config()

SOURCE_SHEET_ID = _config.get("source_sheet_id")
TARGET_SHEET_ID = _config.get("target_sheet_id")
YEAR = datetime.now().year
SERVICE_ACCOUNT_FILE = _config.get("service_account_file", "src/gcp-service-account/service_account.json")

# Optional date range
START_DATE_STR = _config.get("start_date")
END_DATE_STR = _config.get("end_date")

START_DATE = datetime.strptime(START_DATE_STR, "%Y-%m-%d") if START_DATE_STR else None
END_DATE = datetime.strptime(END_DATE_STR, "%Y-%m-%d") if END_DATE_STR else None
