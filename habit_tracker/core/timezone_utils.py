from datetime import datetime, time, date
from zoneinfo import ZoneInfo


DUMMY_DATE = date(1990, 4, 7)


def utc_to_local(utc_time: time, tz: str) -> time:
    utc_datetime = datetime.now(ZoneInfo("UTC")).replace(hour=utc_time.hour, minute=utc_time.minute, second=0, microsecond=0)
    local_datetime = utc_datetime.astimezone(ZoneInfo(tz))

    return local_datetime.time()


def local_to_utc(local_time: time, tz: str) -> time:
    local_datetime = datetime.now(ZoneInfo(tz)).replace(hour=local_time.hour, minute=local_time.minute, second=0, microsecond=0)
    utc_datetime = local_datetime.astimezone(ZoneInfo("UTC"))

    return utc_datetime.time()


if __name__ == '__main__':
    t = time(11, 14)
    tz_ = "Europe/Belgrade"

    new_t = local_to_utc(t, tz_)
    print(new_t)
    print(utc_to_local(new_t, tz_))
