import time
from datetime import datetime, timedelta
import pytz
import calendar


def days_to_seconds(day):
    return day * 24 * 60 * 60


def hours_to_seconds(hour):
    return hour * 60 * 60


def minutes_to_seconds(minutes):
    return minutes * 60


class Timestamp:
    def __init__(self, ts, tz=pytz.utc):
        self._tz = tz
        self._timestamp(ts)

    @property
    def timezone(self):
        return self._tz

    @property
    def local_datetime(self):
        return datetime.fromtimestamp(self._ts, tz=self._tz)

    @property
    def utc_datetime(self):
        return datetime.utcfromtimestamp(self._ts).replace(tzinfo=pytz.utc)

    @property
    def timestamp(self):
        return int(self._ts)

    def _timestamp(self, ts):
        if not isinstance(ts, int):
            raise TypeError('ts must be int not %s' % type(ts))
        else:
            self._ts = ts

    def convert_timezone(self, tz):
        return Timestamp(self._timestamp, tz)

    def add(self, sec):
        dt = self._tz.normalize(self.local_datetime + timedelta(seconds=sec))
        return Timestamp.from_datetime(dt)

    def subtract(self, sec):
        dt = self._tz.normalize(self.local_datetime - timedelta(seconds=sec))
        return Timestamp.from_datetime(dt)

    @classmethod
    def from_datetime(cls, dt):
        if dt is None:
            return Timestamp(0)

        t = dt
        if dt.tzinfo is not None:
            t = dt.astimezone(pytz.utc)
        return Timestamp(calendar.timegm(t.timetuple()), tz=dt.tzinfo)

    @classmethod
    def from_detail(cls, year, month, day, hour=0, minute=0, second=0, tzinfo=pytz.utc):
        return cls.from_datetime(datetime(year, month, day, hour, minute, second, 0, tzinfo))


def main():
    dt = datetime(2013, 3, 10, 1, 45, tzinfo=pytz.timezone('US/Central'))
    print dt
    ts = Timestamp.from_datetime(dt)
    print ts.timestamp
    print ts.local_datetime
    print ts.utc_datetime
    print timedelta(days=2)
    print timedelta(hours=48)
    add = ts.add(minutes_to_seconds(30))
    print add.timestamp
    print add.local_datetime
    print add.utc_datetime
    sub = add.subtract(days_to_seconds(2))
    print sub.timestamp
    print sub.local_datetime
    print sub.utc_datetime


if __name__ == '__main__':
    main()
