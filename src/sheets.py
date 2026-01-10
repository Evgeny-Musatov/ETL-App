import gspread
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from src.config import SERVICE_ACCOUNT_FILE, SOURCE_SHEET_ID, TARGET_SHEET_ID

def connect():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Verify file exists
    try:
        print(f"DEBUG: Attempting to load credentials from {SERVICE_ACCOUNT_FILE}")
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, scope
        )
        print("DEBUG: Credentials loaded. Authorizing gspread...")
        client = gspread.authorize(creds)
        print("DEBUG: gspread authorized.")
        return client
    except Exception as e:
        print(f"Error connecting using {SERVICE_ACCOUNT_FILE}: {e}")
        return None

def write_df_to_sheet(sh, df, worksheet_name, clear=True, index=None):
    """Write a pandas DataFrame to a gspread Spreadsheet object.

    - Converts datetime 'date' column to YYYY-MM-DD strings
    - Creates the worksheet if missing (at optional index), otherwise clears it
    - Writes header + rows
    """
    df_to_write = df.copy()

    # format date column as ISO string if present
    if "date" in df_to_write.columns:
        try:
            df_to_write["date"] = pd.to_datetime(df_to_write["date"]).dt.strftime("%Y-%m-%d")
        except Exception:
            df_to_write["date"] = df_to_write["date"].astype(str)

    # Safely build rows: convert NA to empty string without forcing dtype conversions
    rows = [df_to_write.columns.tolist()]
    for row in df_to_write.itertuples(index=False, name=None):
        safe_row = ["" if (pd.isna(cell) or cell is pd.NA) else str(cell) for cell in row]
        rows.append(safe_row)

    try:
        try:
            ws = sh.worksheet(worksheet_name)
            if clear:
                ws.clear()
        except gspread.WorksheetNotFound:
            # Create with some buffer
            # index=0 makes it the first tab (leftmost)
            ws = sh.add_worksheet(title=worksheet_name, rows=str(len(rows) + 20), cols=str(len(df_to_write.columns) + 5), index=index)

        # update using a single batch
        ws.update(rows)
    except Exception as e:
        raise RuntimeError(f"Failed to write worksheet '{worksheet_name}': {e}")


def get_all_tabs(client, target_sheet_id=None):
    if not target_sheet_id:
        target_sheet_id = TARGET_SHEET_ID or SOURCE_SHEET_ID
    sh = client.open_by_key(target_sheet_id)
    return [ws.title for ws in sh.worksheets()]

def delete_tabs(client, tab_names, target_sheet_id=None):
    if not target_sheet_id:
        target_sheet_id = TARGET_SHEET_ID or SOURCE_SHEET_ID
    sh = client.open_by_key(target_sheet_id)
    
    deleted = []
    failed = []
    
    for name in tab_names:
        try:
            ws = sh.worksheet(name)
            sh.del_worksheet(ws)
            deleted.append(name)
        except Exception as e:
            failed.append((name, str(e)))
            
    return deleted, failed

def write_latest_week(client, df, target_sheet_id=None, worksheet_name=None):
    import re
    # default to TARGET_SHEET_ID from config, or fallback to SOURCE_SHEET_ID
    if not target_sheet_id:
        target_sheet_id = TARGET_SHEET_ID or SOURCE_SHEET_ID
    
    sh = client.open_by_key(target_sheet_id)
    
    if not worksheet_name:
        # User request: "Run <serial> - [DD/MM/YYYY HH:MM:SS]"
        # Find next serial number (support both "run 1" and "Run 1 -" formats)
        max_run = 0
        pattern = re.compile(r"^(?:run|Run)\s+(\d+).*")
        
        for ws in sh.worksheets():
            m = pattern.match(ws.title)
            if m:
                try:
                    num = int(m.group(1))
                    if num > max_run:
                        max_run = num
                except ValueError:
                    pass
        
        next_run = max_run + 1
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        worksheet_name = f"Run {next_run} - [{now_str}]"

    print(f"Writing to Sheet ID: {target_sheet_id}")
    print(f"Target Tab: {worksheet_name}")

    try:
        # Pass index=0 to ensure it's created on the far left
        write_df_to_sheet(sh, df, worksheet_name=worksheet_name, index=0)
        print(f"✅ Written cleaned DataFrame to spreadsheet {target_sheet_id} worksheet '{worksheet_name}'")
        return worksheet_name
    except Exception as e:
        print(f"❌ Failed to write to sheet: {e}")
        raise e
