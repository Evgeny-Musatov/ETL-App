import re
from datetime import datetime

def parse_tab_date(tab_name, year=None):
    """
    Parses tab names. Supports:
    1. 'DDMM' (e.g. '1212') -> 12/12/YEAR
    2. 'DD/MM/YYYY' (e.g. '12/12/2026', '12-12-2026', '12.12.2026')
    Returns datetime or None
    """
    s = str(tab_name).strip()

    from src.config import YEAR as DEFAULT_YEAR
    target_year = year if year else DEFAULT_YEAR

    # 1. Try explicit full date formats (DD/MM/YYYY)
    full_date_patterns = [
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"
    ]
    for p in full_date_patterns:
        try:
            return datetime.strptime(s, p)
        except ValueError:
            pass

    # 2. Try DDMM (must be exactly 4 digits)
    if s.isdigit() and len(s) == 4:
        try:
            day = int(s[:2])
            month = int(s[2:])
            return datetime(target_year, month, day)
        except ValueError:
            pass

    return None


def parse_col_date(col_name, year=None):
    """Try to parse a column header into a datetime.
    Accepts formats like 'DDMM', 'DD/MM', 'DD-MM', 'DD.MM.YYYY', 'December 16', 'Dec 16', etc.
    Returns datetime or None.
    """
    s = str(col_name).strip()
    if not s:
        return None

    # common strptime patterns (without year -> year will be set to YEAR)
    patterns = [
        "%d/%m/%Y", "%d/%m", "%d-%m-%Y", "%d-%m", "%d.%m.%Y", "%d.%m", "%d%m",
        "%B %d", "%b %d", "%d %B", "%d %b", "%B %d, %Y", "%b %d, %Y"
    ]
    
    from src.config import YEAR as DEFAULT_YEAR
    target_year = year if year else DEFAULT_YEAR
    
    for p in patterns:
        try:
            dt = datetime.strptime(s, p)
            if dt.year == 1900:
                return datetime(target_year, dt.month, dt.day)
            return dt
        except Exception:
            pass

    # try to find month name and day inside the string (e.g. 'TOTAL ... (December 12)')
    m = re.search(r'(?P<month_name>[A-Za-z]+)\s*(?P<day>\d{1,2})', s)
    if m:
        month_name = m.group('month_name')
        day = int(m.group('day'))
        for fmt in ('%B', '%b'):
            try:
                month = datetime.strptime(month_name, fmt).month
                return datetime(target_year, month, day)
            except Exception:
                pass

    m = re.search(r'(?P<day>\d{1,2})\s*(?P<month_name>[A-Za-z]+)', s)
    if m:
        day = int(m.group('day'))
        month_name = m.group('month_name')
        for fmt in ('%B', '%b'):
            try:
                month = datetime.strptime(month_name, fmt).month
                return datetime(target_year, month, day)
            except Exception:
                pass

    # try extracting digits like '1212' -> DDMM
    digits = ''.join(ch for ch in s if ch.isdigit())
    if len(digits) == 4:
        try:
            day = int(digits[:2])
            month = int(digits[2:])
            return datetime(target_year, month, day)
        except ValueError:
            return None

    return None


def is_date_header(col_name):
    """Return True only if the column header is essentially a date label (no extra text).

    Examples that are True: 'December 16', 'Dec 16', '12/12', '1212', '16-12-2025', '16.12'
    Examples that are False: 'TOTAL ACCOUNT FOLLOWERS (December 12)', 'Followers/Lead Per Dollar'
    """
    s = str(col_name).strip()
    if not s:
        return False

    # Try exact-strptime matches used in parse_col_date (these require the whole string to be the date)
    patterns = [
        "%d/%m/%Y", "%d/%m", "%d-%m-%Y", "%d-%m", "%d.%m.%Y", "%d.%m", "%d%m",
        "%B %d", "%b %d", "%d %B", "%d %b", "%B %d, %Y", "%b %d, %Y"
    ]
    for p in patterns:
        try:
            datetime.strptime(s, p)
            return True
        except Exception:
            pass

    # require full match for month name + day patterns (avoid matching when surrounded by other words)
    if re.fullmatch(r"[A-Za-z]+\s*\d{1,2}(,\s*\d{4})?", s):
        return True
    if re.fullmatch(r"\d{1,2}\s*[A-Za-z]+(,\s*\d{4})?", s):
        return True

    # digits like '1212' or '12122025' (but only when the whole string is digits)
    if s.isdigit() and len(s) in (4,6,8):
        return True

    # simple numeric date with separators (e.g., '12/12', '12-12')
    if re.fullmatch(r"\d{1,2}([/\-.]\d{1,2})([/\-.]\d{2,4})?", s):
        return True

    return False


def normalize_columns(df):
    """Normalize DataFrame column names to snake_case lowercase and ensure uniqueness.

    Special handling:
    - Headers containing 'total account followers' become 'total_account_followers' (date suffix dropped).
    """
    def _norm_original(s):
        # Preprocess special cases before generic normalization
        s_orig = str(s).strip()
        s_low = s_orig.lower()
        if 'total account followers' in s_low:
            return 'total_account_followers'
        return s_orig

    def _norm(s):
        s = str(s).strip().lower()
        s = re.sub(r"[^0-9a-z]+", "_", s)
        s = re.sub(r"_+", "_", s)
        s = s.strip("_")
        return s

    preprocessed = [_norm_original(c) for c in df.columns]
    cols = [_norm(c) for c in preprocessed]

    # ensure uniqueness by appending suffixes
    seen = {}
    new_cols = []
    for c in cols:
        base = c or "col"
        if base in seen:
            seen[base] += 1
            new = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
            new = base
        new_cols.append(new)

    df_out = df.copy()
    df_out.columns = new_cols
    return df_out

def parse_tab_datetime(tab_name):
    """
    Parses datetime from tab names. Supports:
    1. New Format: Run N - [DD/MM/YYYY HH:MM:SS]
    2. Old Format: run N [YYYY-MM-DD_HH-MM-SS]
    
    Returns datetime object or None.
    """
    import re
    # 1. New Format: [10/01/2026 00:00:00]
    m_new = re.search(r"\[(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2}):(\d{2})\]", tab_name)
    if m_new:
        try:
            return datetime(
                int(m_new.group(3)), int(m_new.group(2)), int(m_new.group(1)),
                int(m_new.group(4)), int(m_new.group(5)), int(m_new.group(6))
            )
        except ValueError:
            pass

    # 2. Old Format: [2026-01-09_21-39-52]
    # Also handles slightly different variations if consistent with YYYY-MM-DD
    m_old = re.search(r"\[(\d{4})-(\d{2})-(\d{2})[_\s](\d{2})[-:](\d{2})[-:](\d{2})\]", tab_name)
    if m_old:
        try:
           return datetime(
               int(m_old.group(1)), int(m_old.group(2)), int(m_old.group(3)),
               int(m_old.group(4)), int(m_old.group(5)), int(m_old.group(6))
           )
        except ValueError:
            pass
            
    return None
