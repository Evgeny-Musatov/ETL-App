import sys
import os
from src import config
from src import sheets
from src import etl

def main():
    print("🚀 Starting ETL Pipeline (CLI Mode)")
    
    # 1. Connect
    client = sheets.connect()
    if not client:
        print("❌ Could not connect to Google Sheets")
        return

    print("\n✅ Connected to Google Sheets")
    
    # 2. Run ETL
    # Use config dates if present, else None (auto-detect last week)
    df_week = etl.run_etl_pipeline(client)

    if df_week.empty:
        print("⚠️ No data processed.")
        return

    print("\n✅ DataFrame created")
    print("Rows:", len(df_week))
    print("Columns:", df_week.columns.tolist())
    
    # 3. Write
    sheets.write_latest_week(client, df_week)

if __name__ == "__main__":
    main()
