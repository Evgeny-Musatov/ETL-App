import pandas as pd
from datetime import datetime, timedelta
from src.utils import parse_tab_date, parse_col_date, is_date_header, normalize_columns
from src.config import SOURCE_SHEET_ID, START_DATE, END_DATE

DAYS_IN_WEEK = 7

def get_tabs_in_range(sh, start_date=None, end_date=None, target_year=None):
    """
    Get tabs filtered by date.
    If start_date/end_date are provided (or in config), use them.
    Otherwise, replicate the logic: find latest date, look back 6 days (7 days total).
    
    target_year: If provided, forces Year for parsing tab dates (DDMM).
    """
    dated_tabs = []

    for ws in sh.worksheets():
        date = parse_tab_date(ws.title, year=target_year)
        if date:
            dated_tabs.append((ws.title, date))

    if not dated_tabs:
        # If no tabs found with target_year, maybe try default? 
        # But if target_year is explicit (e.g. from user), valid to fail or return empty?
        # Let's just warn or return empty if stricter logic needed.
        # For now, raise logic as before but with context.
        if target_year:
             # retry with default year just to see? No, trust input.
             pass
        # If we return emtpy list, caller handles it?
        # The original code raised ValueError.
        pass

    if not dated_tabs:
         raise ValueError(f"No valid DDMM tabs found (Year used: {target_year or 'Default'})")

    dated_tabs.sort(key=lambda x: x[1])

    # Determine range
    if start_date or end_date:
        # User defined range
        s = start_date or datetime.min
        e = end_date or datetime.max
        # Ensure we compare date only
        # Tabs are datetime(Y, M, D, 0, 0) usually
        week_tabs = [
            title for title, date in dated_tabs
            if s <= date <= e
        ]
        print(f"Filter Range: {s} -> {e}")
        return week_tabs, s, e
    else:
        # Default logic
        latest_date = dated_tabs[-1][1]
        week_start = latest_date - timedelta(days=DAYS_IN_WEEK - 1)
        
        week_tabs = [
            title for title, date in dated_tabs
            if week_start <= date <= latest_date
        ]
        return week_tabs, week_start, latest_date


def process_worksheet(ws, target_year=None):
    """
    Handles sheets where:
    - Model name is a merged row across columns
    - Data rows follow until next model row
    - If date columns exist, pivot them.
    - If no date columns, the sheet represents the date in tab_date.
    """
    data = ws.get_all_values()
    if not data:
        return pd.DataFrame()

    headers = data[0]
    rows = data[1:]

    processed = []
    current_model = None

    # Parse tab date once
    tab_date = parse_tab_date(ws.title, year=target_year)

    for row in rows:
        if not any(row):
            continue  # skip empty rows

        first_cell = row[0].strip()

        # MODEL HEADER ROW (merged across columns)
        if first_cell and all((cell or "").strip() == "" for cell in row[1:]):
            current_model = first_cell
            continue

        # DATA ROW
        if current_model:
            # We must handle headers length mismatch safely
            safe_row = row + [""] * (len(headers) - len(row))
            row_dict = dict(zip(headers, safe_row[:len(headers)]))
            row_dict["model"] = current_model
            row_dict["tab_date"] = tab_date
            processed.append(row_dict)

    df = pd.DataFrame(processed)

    if df.empty:
        return df

    # Detect date-like columns in the sheet headers
    date_cols = [col for col in df.columns if is_date_header(col)]

    if not date_cols:
        # Return as-is, BUT 'date' column is missing here, only 'tab_date'.
        return df

    # Melt date columns into rows
    id_vars = [c for c in df.columns if c not in date_cols]
    melted = df.melt(id_vars=id_vars, value_vars=date_cols, var_name="day_col", value_name="value")

    # drop empty values
    melted["value"] = melted["value"].replace("", pd.NA)
    melted = melted.dropna(subset=["value"]).copy()

    # parse the day_col into a proper datetime (use YEAR if year missing)
    def _make_date(row):
        # PRIORITY: Trust tab_date if it exists (User Requirement)
        if row.get("tab_date"):
            return row.get("tab_date")
            
        parsed = parse_col_date(row["day_col"], year=target_year)
        if parsed:
            return parsed
        return None

    melted["date"] = melted.apply(_make_date, axis=1)

    # Drop the original sheet-level tab_date (redundant with 'date')
    melted = melted.drop(columns=["tab_date"], errors="ignore")

    # Drop any columns that are empty strings or whitespace-only names
    melted = melted.loc[:, [c for c in melted.columns if str(c).strip() != ""]]

    # Rename the 'value' column (contains user names) to 'user_name'
    if "value" in melted.columns:
        melted = melted.rename(columns={"value": "user_name"})
        melted["user_name"] = melted["user_name"].astype(str).str.strip()

    # tidy up by removing the temporary 'day_col' identifier
    melted = melted.drop(columns=["day_col"], errors="ignore")

    # ensure 'date' and 'user_name' are near the front
    cols = [c for c in melted.columns if c not in ["date", "user_name"]]
    cols = ["date", "user_name"] + cols
    melted = melted[cols]

    return melted


def coerce_numeric_columns(df_in):
    df = df_in.copy()
    skip = {"date", "user_name", "model", "notes", "others"}
    for c in list(df.columns):
        if c in skip:
            continue
        s = df[c].astype(str).str.strip()
        non_empty = s[s.notna() & (s != "")]
        if non_empty.empty:
            continue
        # require that a reasonable fraction contains digits
        if non_empty.str.contains(r"\d").mean() < 0.3:
            continue

        cleaned = s.astype(str)
        # convert parentheses negative like (1,234)
        cleaned = cleaned.str.replace(r"^\((.+)\)$", r"-\1", regex=True)
        # remove currency symbols, commas, % signs, spaces
        cleaned = cleaned.str.replace(r"[^0-9\.\-]", "", regex=True)
        cleaned = cleaned.replace("", pd.NA)
        num = pd.to_numeric(cleaned, errors="coerce")
        if num.notna().sum() == 0:
            continue

        # if all numeric values are integer-like, convert to nullable Int64
        non_null = num.dropna()
        if (non_null % 1 == 0).all():
            df[c] = num.astype('Int64')
        else:
            df[c] = num.astype('float')

        print(f"🔢 Converted column '{c}' to numeric ({df[c].notna().sum()} values)")
    return df


def run_etl_pipeline(client, start_date=None, end_date=None):
    """
    Main pipeline function.
    Can operate with explicit start/end dates (e.g. passed from GUI)
    OR fallback to config / auto-calculation.
    """
    # Prefer arguments > config > None
    s_date = start_date or START_DATE
    e_date = end_date or END_DATE

    # --- YEAR INJECTION LOGIC ---
    # If s_date is provided, use its year. Otherwise None (default to config/current)
    target_year = s_date.year if s_date else None
    
    sh = client.open_by_key(SOURCE_SHEET_ID)
    if not sh:
        raise ValueError("Could not open source sheet")

    week_tabs, week_start, latest_date = get_tabs_in_range(sh, s_date, e_date, target_year=target_year)
    print("📅 Detected week tabs:", week_tabs)
    print(f"Range: {week_start.date()} -> {latest_date.date()}")

    dfs = []

    for tab in week_tabs:
        ws = sh.worksheet(tab)
        # Pass target_year here too!
        df_day = process_worksheet(ws, target_year=target_year)
        dfs.append(df_day)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # === BUG FIX START ===
    # If a sheet was NOT melted (because it had no date headers), it has 'tab_date' but no 'date' column 
    # (or 'date' is NaN if other sheets had it).
    # We must coalesce 'date' from 'tab_date'.
    
    if "tab_date" in df.columns:
        if "date" not in df.columns:
            df["date"] = df["tab_date"]
        else:
            df["date"] = df["date"].fillna(df["tab_date"])
        
        # We can drop tab_date now
        df = df.drop(columns=["tab_date"], errors="ignore")
    # === BUG FIX END ===

    # ensure 'date' is datetime and filter to the week range
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        # Filter logic
        # We might have pivoted columns from a sheet that contains dates OUTSIDE the week_tabs range?
        # Typically the 'week_tabs' logic selects TABS. 
        # But if a tab contains 'Dec 12' and 'Dec 13', and our range includes both, we good.
        # Just to be safe, filter again by the determined range.
        ts_start = pd.Timestamp(week_start)
        ts_end = pd.Timestamp(latest_date)
        # Adjust end to encompass the full day if needed, but usually dates are 00:00:00
        
        df = df[(df["date"] >= ts_start) & (df["date"] <= ts_end)]

    # Normalize column names to snake_case
    df = normalize_columns(df)

    # Remove unwanted summary rows (case-insensitive)
    if "user_name" in df.columns:
        uname = df["user_name"].astype(str).str.strip().str.lower()
        # exact patterns (including misspellings seen in source)
        exact_remove = {"total active accounts today", "total sub yestrerday", "total active accounts yestrerday"}
        mask_exact = uname.isin(exact_remove)

        # broader pattern: lines starting with 'total active accounts' or 'total sub' and containing 'today' or 'yest'
        mask_broad = ((uname.str.contains(r"^total\s+active\s+accounts")) | (uname.str.contains(r"^total\s+sub"))) & (uname.str.contains(r"today|yest"))

        total_mask = mask_exact | mask_broad
        removed = total_mask.sum()
        if removed:
            print(f"🔽 Dropping {removed} summary rows (total/summary lines)")
            df = df[~total_mask].copy()

    # Merge total_account_followers* columns
    follower_cols = [c for c in df.columns if c.startswith("total_account_followers")]
    if follower_cols:
        # create numeric versions (strip non-digits)
        num_cols = []
        for c in follower_cols:
            num_c = f"{c}_num"
            df[num_c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^0-9]', '', regex=True), errors='coerce')
            num_cols.append(num_c)

        # coalesce per-row (first non-null) then per-user take the max across rows
        df['__taf_row'] = df[num_cols].bfill(axis=1).iloc[:,0]

        # per user_name, take max observed and map back
        taf_by_user = df.groupby('user_name')['__taf_row'].max().dropna()
        df['total_account_followers'] = df['user_name'].map(taf_by_user)

        # drop temporary
        to_drop = [c for c in follower_cols if c != 'total_account_followers'] + num_cols + ['__taf_row']
        df = df.drop(columns=to_drop, errors='ignore')

        filled = df['total_account_followers'].notna().sum()
        print(f"🔀 Merged {len(follower_cols)} follower columns into 'total_account_followers' ({filled} users with values)")

    df = coerce_numeric_columns(df)

    return df
