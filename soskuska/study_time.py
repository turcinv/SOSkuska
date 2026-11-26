"""Timezone-aware ISO study timestamps, shared by queries and local-day reports."""
from datetime import date, datetime

DAY_MICROSECONDS = 86400 * 1000000


def utc_key(value):
    """Exact integer instant, including offsets that cross datetime's year bounds."""
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    offset = parsed.utcoffset()
    if offset is None:
        raise ValueError('Study timestamps must include a time zone.')
    wall = ((parsed.toordinal()-1)*DAY_MICROSECONDS
            + (parsed.hour*3600 + parsed.minute*60 + parsed.second)*1000000
            + parsed.microsecond)
    offset_us = (offset.days*86400 + offset.seconds)*1000000 + offset.microseconds
    return wall - offset_us


def local_day(value):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() is None:
        raise ValueError('Study timestamps must include a time zone.')
    try:
        return parsed.astimezone().date().isoformat()
    except (OverflowError, OSError, ValueError):
        # Some hosts cannot convert dates near years 1/9999 to local time.
        # Keep these accepted backup rows readable with a bounded UTC-day fallback.
        ordinal = utc_key(value)//DAY_MICROSECONDS + 1
        return date.fromordinal(max(1, min(date.max.toordinal(), ordinal))).isoformat()


def display_time(value):
    parsed = datetime.fromisoformat(value)
    try:
        return parsed.astimezone().strftime("%Y-%m-%d %H:%M")
    except (OverflowError, OSError, ValueError):
        return parsed.isoformat(sep=' ', timespec='minutes')


def register_sql_functions(db):
    db.create_function('study_utc_key', 1, utc_key, deterministic=True)
    db.create_function('study_local_day', 1, local_day)
