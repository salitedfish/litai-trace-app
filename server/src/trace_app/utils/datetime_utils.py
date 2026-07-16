from datetime import datetime, timezone
from typing import Optional
import re


def parse_iso_format_datetime(date_string: str) -> Optional[datetime]:
    """
    解析ISO格式的日期时间字符串，兼容Python 3.6和更早版本

    支持格式:
    - 2023-12-25T10:30:00
    - 2023-12-25T10:30:00+08:00
    - 2023-12-25T10:30:00.123456
    - 2023-12-25T10:30:00.123456+08:00
    - 2023-12-25T10:30:00Z

    Args:
        date_string: ISO格式的日期时间字符串

    Returns:
        datetime对象，如果解析失败返回None
    """
    if not date_string:
        return None

    try:
        if hasattr(datetime, 'fromisoformat'):
            if date_string.endswith('Z'):
                date_string = date_string[:-1] + '+00:00'
            return datetime.fromisoformat(date_string)

        return _parse_iso_format_manually(date_string)

    except (ValueError, TypeError, AttributeError):
        return None


def _parse_iso_format_manually(date_string: str) -> Optional[datetime]:
    """
    手动解析ISO格式日期时间字符串（兼容Python 3.6）
    """
    try:
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'

        pattern = r'^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.(\d+))?(?:([\+\-]\d{2}:\d{2}))?$'
        match = re.match(pattern, date_string)

        if not match:
            return None

        date_part = match.group(1)
        time_part = match.group(2)
        microseconds_str = match.group(3)
        timezone_part = match.group(4)

        dt_string = f"{date_part} {time_part}"
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')

        if microseconds_str:
            microseconds_str = microseconds_str.ljust(6, '0')[:6]
            microseconds = int(microseconds_str)
            dt = dt.replace(microsecond=microseconds)

        if timezone_part:
            sign = 1 if timezone_part[0] == '+' else -1
            tz_hours = int(timezone_part[1:3])
            tz_minutes = int(timezone_part[4:6])

            from datetime import timezone, timedelta
            tz_offset = timedelta(hours=sign * tz_hours, minutes=sign * tz_minutes)
            tz = timezone(tz_offset)
            dt = dt.replace(tzinfo=tz)

        return dt

    except Exception:
        return None


def format_datetime_to_iso(dt: datetime) -> str:
    if not dt:
        return ""
    return dt.isoformat()


def ensure_utc_datetime(dt: datetime) -> datetime:
    if not dt:
        return dt

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    if dt.tzinfo != timezone.utc:
        return dt.astimezone(timezone.utc)

    return dt
