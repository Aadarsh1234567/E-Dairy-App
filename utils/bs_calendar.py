"""
bs_calendar.py — Bikram Sambat calendar utilities for Santosh E-Dairy.

All dates in the application are stored in the database as AD (ISO format)
because SQLite has no BS date type. This module handles:
  - AD <-> BS conversion
  - Formatting BS dates in Nepali and English
  - BS-aware today/now
  - Nepali digit conversion
  - Validation helpers

Library: nepali-datetime (covers 1975–2100 BS)
"""

import datetime
import nepali_datetime

# ── Nepali month names (full) ─────────────────────────────────────────────────
MONTH_NAMES_NE = (
    None,
    'वैशाख', 'जेष्ठ', 'असार', 'श्रावण',
    'भदौ',   'आश्विन','कार्तिक','मंसिर',
    'पौष',   'माघ',   'फाल्गुण','चैत्र',
)

MONTH_NAMES_EN = (
    None,
    'Baisakh', 'Jestha',  'Ashadh',   'Shrawan',
    'Bhadra',  'Ashwin',  'Kartik',   'Mangsir',
    'Poush',   'Magh',    'Falgun',   'Chaitra',
)

# Nepali weekday names indexed EXACTLY as nepali_datetime.date.weekday() returns them.
# VERIFIED: weekday() returns 1=Monday, 2=Tuesday, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 0=Sunday
# (confirmed against AD ground truth: 2026-06-15 Monday -> weekday()=1, 2026-06-21 Sunday -> weekday()=0)
# Index 0 of this tuple = Sunday (matches weekday()==0), index 1 = Monday, etc.
WEEKDAY_NAMES_NE = (
    'आइतबार',   # 0 = Sunday
    'सोमबार',   # 1 = Monday
    'मंगलबार',  # 2 = Tuesday
    'बुधवार',   # 3 = Wednesday
    'बिहिबार',  # 4 = Thursday
    'शुक्रबार', # 5 = Friday
    'शनिबार',   # 6 = Saturday
)
WEEKDAY_NAMES_EN = (
    'Sunday',    # 0
    'Monday',    # 1
    'Tuesday',   # 2
    'Wednesday', # 3
    'Thursday',  # 4
    'Friday',    # 5
    'Saturday',  # 6
)

# Nepali digit map
_NP_DIGITS = '०१२३४५६७८९'


# ── Digit conversion ──────────────────────────────────────────────────────────

def to_np_digits(value) -> str:
    """Convert an integer or string of digits to Nepali digits."""
    return ''.join(_NP_DIGITS[int(ch)] if ch.isdigit() else ch for ch in str(value))


def np_digit_pad(n: int, width: int = 2) -> str:
    """Return n as zero-padded Nepali digit string."""
    return to_np_digits(str(n).zfill(width))


# ── Core conversion ───────────────────────────────────────────────────────────

def ad_to_bs(ad_date: datetime.date) -> nepali_datetime.date:
    """Convert a Python date (AD) to a nepali_datetime.date (BS)."""
    return nepali_datetime.date.from_datetime_date(ad_date)


def bs_to_ad(bs_date: nepali_datetime.date) -> datetime.date:
    """Convert a nepali_datetime.date (BS) to a Python date (AD)."""
    return bs_date.to_datetime_date()


def bs_today() -> nepali_datetime.date:
    """Return today's date in BS."""
    return nepali_datetime.date.today()


def bs_now() -> nepali_datetime.datetime:
    """Return current datetime in BS (Nepal time UTC+5:45)."""
    return nepali_datetime.datetime.now()


# ── Formatting ────────────────────────────────────────────────────────────────

def format_bs_date(
    bs_date: nepali_datetime.date,
    lang:    str = "NE",
    include_weekday: bool = False,
) -> str:
    """
    Format a BS date as a readable string.

    NE examples:
        २०८३ असार १  (without weekday)
        मंगलबार, २०८३ असार १  (with weekday)

    EN examples:
        2083 Ashadh 01
        Tuesday, 2083 Ashadh 01
    """
    if lang == "NE":
        year  = to_np_digits(bs_date.year)
        month = MONTH_NAMES_NE[bs_date.month]
        day   = to_np_digits(bs_date.day)
        date_str = f"{year} {month} {day}"
        if include_weekday:
            wd = WEEKDAY_NAMES_NE[bs_date.weekday()]
            return f"{wd}, {date_str}"
        return date_str
    else:
        year  = bs_date.year
        month = MONTH_NAMES_EN[bs_date.month]
        day   = str(bs_date.day).zfill(2)
        date_str = f"{year} {month} {day}"
        if include_weekday:
            wd = WEEKDAY_NAMES_EN[bs_date.weekday()]
            return f"{wd}, {date_str}"
        return date_str


def format_ad_date_as_bs(
    ad_date: datetime.date,
    lang:    str = "NE",
    include_weekday: bool = False,
) -> str:
    """Convert an AD date and format it as BS string."""
    return format_bs_date(ad_to_bs(ad_date), lang=lang, include_weekday=include_weekday)


def format_bs_time(bs_dt: nepali_datetime.datetime, lang: str = "NE") -> str:
    """
    Format the time portion of a BS datetime.
    Returns 12-hour format with AM/PM in Nepali or English.

    NE: १०:३०  बिहान  /  ०३:४५  साँझ
    EN: 10:30 AM  /  03:45 PM
    """
    hour   = bs_dt.hour
    minute = bs_dt.minute

    if lang == "NE":
        h12    = hour % 12 or 12
        am_pm  = _time_of_day_ne(hour)
        h_str  = to_np_digits(str(h12).zfill(2))
        m_str  = to_np_digits(str(minute).zfill(2))
        return f"{h_str}:{m_str}  {am_pm}"
    else:
        h12   = hour % 12 or 12
        am_pm = "AM" if hour < 12 else "PM"
        return f"{h12:02d}:{minute:02d} {am_pm}"


def _time_of_day_ne(hour: int) -> str:
    """Return Nepali time-of-day label for given 24h hour."""
    if 4 <= hour < 12:
        return "बिहान"     # morning
    elif 12 <= hour < 16:
        return "दिउँसो"   # afternoon
    elif 16 <= hour < 20:
        return "साँझ"      # evening
    else:
        return "राति"      # night


def format_bs_datetime(
    ad_datetime: datetime.datetime | None = None,
    lang: str = "NE",
) -> str:
    """
    Full datetime string in BS.
    If ad_datetime is None, uses now (Nepal time).
    """
    if ad_datetime is None:
        bs_dt = bs_now()
    else:
        # Convert to Nepal timezone first
        bs_dt = nepali_datetime.datetime.from_datetime_datetime(ad_datetime)

    date_str = format_bs_date(bs_dt.date(), lang=lang, include_weekday=True)
    time_str = format_bs_time(bs_dt, lang=lang)
    return f"{date_str}   {time_str}"


# ── Database storage helpers ──────────────────────────────────────────────────

def today_ad() -> datetime.date:
    """Return today as AD date (for DB storage)."""
    return datetime.date.today()


def parse_db_date(db_value) -> datetime.date | None:
    """
    Parse a date from DB (string 'YYYY-MM-DD' or datetime.date).
    Returns None if value is None or unparseable.
    """
    if db_value is None:
        return None
    if isinstance(db_value, datetime.date):
        return db_value
    try:
        return datetime.date.fromisoformat(str(db_value))
    except (ValueError, TypeError):
        return None


def db_date_to_bs_str(db_value, lang: str = "NE") -> str:
    """
    Convert a DB date value directly to a formatted BS string.
    Returns '—' if the value is None or invalid.
    """
    ad = parse_db_date(db_value)
    if ad is None:
        return "—"
    return format_ad_date_as_bs(ad, lang=lang)


# ── Validation ────────────────────────────────────────────────────────────────

def is_valid_bs_date(year: int, month: int, day: int) -> bool:
    """Check whether a given BS year/month/day is valid."""
    try:
        nepali_datetime.date(year, month, day)
        return True
    except (ValueError, Exception):
        return False


def bs_date_from_parts(year: int, month: int, day: int) -> nepali_datetime.date | None:
    """Create a BS date from parts. Returns None if invalid."""
    try:
        return nepali_datetime.date(year, month, day)
    except Exception:
        return None


def days_in_bs_month(year: int, month: int) -> int:
    """Return the number of days in a given BS month."""
    try:
        import nepali_datetime as _nd
        # Find last valid day by trying from 32 downward
        for d in range(32, 28, -1):
            try:
                _nd.date(year, month, d)
                return d
            except Exception:
                continue
        return 30  # fallback
    except Exception:
        return 30
