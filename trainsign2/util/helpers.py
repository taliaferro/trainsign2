from datetime import datetime
from zoneinfo import ZoneInfo


def time_format(tz: str, format: str = "%Y-%m-%dT%H:%M:%S"):
    zone = ZoneInfo(tz)
    now = datetime.now(zone)
    return now.strftime(format)
