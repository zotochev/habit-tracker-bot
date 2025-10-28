import datetime
from zoneinfo import ZoneInfo


def seconds_to_time(seconds: int) -> datetime.time:
    return datetime.time(
        hour=seconds // 3600,
        minute=(seconds % 3600) // 60,
        second=seconds % 60,
    )


def time_to_seconds(time: datetime.time) -> int:
    return time.hour * 3600 + time.minute * 60 + time.second


def datetime_to_seconds(dt: datetime.datetime) -> int:
    return time_to_seconds(dt.time())


def timezone_offset(tz_name: str) -> datetime.timedelta:
    return datetime.datetime.now(ZoneInfo(tz_name)).utcoffset()
