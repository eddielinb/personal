import os
import time
import pytz
import calendar
import copy
import numpy as np
import ujson as json
import msgpack
import gzip
import logging
import cStringIO as StringIO
import threading
from abc import abstractmethod, ABCMeta
from datetime import datetime
from datetime import timedelta

from base_io import ImCloudBase


__logger = logging.getLogger(__file__)


def get_cdir():
    # this function is to be used from cython code (.pyx), because __file__
    # is not defined when module is loaded.
    return os.path.abspath(os.path.dirname(__file__))


class StopWatch(object):
    def __init__(self):
        self._start = 0
        self._end = 0

    @property
    def elapsed_sec(self):
        return self._end - self._start

    def start(self):
        self._start = time.time()
        return self._start

    def stop(self):
        self._end = time.time()
        return self._end


class RecursiveTimer(ImCloudBase):
    __metaclass__ = ABCMeta

    def __init__(self, delay, recursive=False, daemon=True):
        """
        constructor
        :param delay: initial delay for timer
        :type delay: int
        :param recursive: flag of continuous calling timer
        :type recursive: bool
        :param daemon: flag of Timer execute with daemon mode
        :type daemon: bool
        :return:
        """
        super(RecursiveTimer, self).__init__()
        self._delay = delay
        self._recursive = recursive
        self._daemon = daemon
        self._timer = None

    def start(self):
        """
        start Timer
        :return:
        """
        self.cancel()
        self._timer = threading.Timer(self._delay, self._elapsed)
        self._timer.daemon = self._daemon
        self._timer.start()

    @abstractmethod
    def elapsed(self):
        pass

    def _elapsed(self):
        """
        callback of threading.Timer function
        :return:
        """
        self.elapsed()
        if self._recursive:
            self.start()

    def cancel(self):
        # check existence and whether caller is same as the timer thread itself
        if self._timer is not None and \
                        threading.current_thread().ident != self._timer.ident:
            self._timer.cancel()
            self._timer.join()
            self._logger.info("timer joined: %s",
                              self._timer.ident)
        elif self._timer is None:
            pass
        else:
            self._logger.debug(
                    "timer tried to cancel in the same ident: %s",
                    self._timer.ident)


def to_utc_timestamp(dt):
    """Converts to utc timestamp from datetime.
    If the dt is naive, return the time in local time.

    Args:
        dt: Datetime object

    Return:
        UTC timestamp(int)
    """
    if dt.tzinfo is None:
        # naive
        aware_dt = pytz.utc.localize(dt)
    else:
        # aware
        aware_dt = copy.deepcopy(dt)

    return calendar.timegm(aware_dt.astimezone(pytz.utc).timetuple())


def to_datetime(timestamp, timezone='Asia/Tokyo'):
    """Converts to datetime from utc timestamp.

    Args:
        timestamp: UTC Unix timestamp
        timezone: Timezone

    Return:
        Datetime object
    """
    return datetime.fromtimestamp(timestamp, pytz.timezone(timezone))


def localize(dt, timezone='Asia/Tokyo'):
    """Localizes datetime(converts naive datetime to aware datetime).

    Args:
        dt: Datetime object(naive)
        timezone: Timezone

    Return:
        Localized datetime object(aware)
    """
    return pytz.timezone(timezone).localize(dt)


def convert_list_to_numpy(arr):
    """Converts list to numpy array and None to numpy.nan.
    :param arr: A list
    :type arr: list
    :return Converted numpy array.
    """
    return np.array(arr, dtype=np.float32)


def convert_numpy_to_list(arr):
    """Converts numpy array to list and numpy.nan to None.

    Args:
        arr: A numpy array

    Return:
        Converted list.
    """
    return [None if ele is None or isinstance(
        ele, float) and np.isnan(ele) else ele for ele in arr]


def nansum(arr1, arr2):
    """Sum numpy array1 and array2.
           nan + nan = nan
           nan + number = number
           number + number = number

    Args:
        arr1: Numpy array
        arr2: Numpy array

    Return:
        Numpy array.
    """
    arr = [np.nan if np.isnan(i) and np.isnan(j)
           else 0 for i, j in zip(arr1, arr2)]
    tmp1 = [0 if np.isnan(i) else i for i in arr1]
    tmp2 = [0 if np.isnan(i) else i for i in arr2]
    return np.array(tmp1) + np.array(tmp2) + np.array(arr)


def nonesum(arr1, arr2):
    """Sum array1 and array2.
           None + None = None
           None + number = number
           number + number = number

    Args:
        arr1: List
        arr2: List

    Return:
        Numpy array.
    """
    arr = [None] * len(arr1)
    cnt = 0
    for i, j in zip(arr1, arr2):
        if i is not None:
            if j is not None:
                arr[cnt] = i + j
            else:
                arr[cnt] = i
        else:
            if j is not None:
                arr[cnt] = j
        cnt += 1
    return arr


def nonemax(arr1, arr2):
    """max value of array1 and array2.
           None + None = None
           None + number = number
           number1 + number2 = max(number1, number2)
    :param arr1: List
    :type arr1: list
    :param arr2: List
    :type arr2: list
    :return list
    """
    arr = [None] * len(arr1)
    cnt = 0
    for i, j in zip(arr1, arr2):
        if i is not None:
            if j is not None:
                arr[cnt] = max(i, j)
            else:
                arr[cnt] = i
        else:
            if j is not None:
                arr[cnt] = j
        cnt += 1
    return arr


def sum_without_nan(arr):
    """Sum array without nan

    Args:
        arr: Numpy array

    Return:
        Summed value. If all elements are np.nan, return np.nan.
    """
    tmp = arr[~np.isnan(arr)]
    if len(tmp) > 0:
        return sum(tmp)
    else:
        return np.nan


def sum_without_none(arr):
    """Sum array without none

    Args:
        arr: A list

    Return:
        Summed value. If all elements are None, return None.
    """
    tmp = [a for a in arr if a is not None]
    if len(tmp) > 0:
        return sum(tmp)
    else:
        return None


def ave_without_nan(arr):
    """Calculate average in array without nan

    Args:
        arr: Numpy array

    Return:
        Average value. If all elements are np.nan, return np.nan.
    """
    tmp = arr[~np.isnan(arr)]
    if len(tmp) > 0:
        return sum(tmp) / len(tmp)
    else:
        return np.nan


def ave_without_none(arr):
    """Calculate average in list without None
    :param arr: summation target array
    :type arr: list
    Return:
        Average value. If all elements are None, return None.
    """
    tmp = [a for a in arr if a is not None]
    if len(tmp) > 0:
        return sum(tmp) / len(tmp)
    else:
        return None


def floor_timestamp_for_interval(timestamp, zoom, timezone):
    """
    Floors timestamp.
    :param timestamp: Unix timestamp
    :type timestamp: int
    :param zoom: minute, 10minute, hour, 6hours, day, month or year
    :type zoom: str
    :param timezone: Timezone
    :type timezone: str
    :return floored timestamp
    """
    if zoom not in ["minute", "10minute", "hour", "6hours",
                    "day", "month", "year"]:
        raise AttributeError(
            "zoom must be in "
            "'minute', '10minute', 'hour', '6hours', 'day', 'month', 'year'"
            " not %s" % zoom)

    dt = to_datetime(timestamp, timezone)
    if zoom == "minute":
        dt = datetime(dt.year, dt.month, dt.day,
                      dt.hour, dt.minute, tzinfo=pytz.timezone(timezone))
    elif zoom == "10minute":
        dt = datetime(dt.year, dt.month, dt.day,
                      dt.hour, dt.minute / 10 * 10,
                      tzinfo=pytz.timezone(timezone))
    elif zoom == "hour":
        dt = datetime(dt.year, dt.month, dt.day,
                      dt.hour, tzinfo=pytz.timezone(timezone))
    elif zoom == "6hours":
        dt = datetime(dt.year, dt.month, dt.day,
                      dt.hour / 6 * 6, tzinfo=pytz.timezone(timezone))
    elif zoom == "day":
        dt = datetime(dt.year, dt.month, dt.day,
                      tzinfo=pytz.timezone(timezone))
    elif zoom == "month":
        dt = datetime(dt.year, dt.month, 1,
                      tzinfo=pytz.timezone(timezone))
    elif zoom == "year":
        dt = datetime(dt.year, 1, 1,
                      tzinfo=pytz.timezone(timezone))

    return int(to_utc_timestamp(dt))


def ceil_timestamp_for_interval(timestamp, zoom, timezone):
    """
    Ceils timestamp
    :param timestamp: Unix timestamp
    :type timestamp: int
    :param zoom: minute, 10minute, hour, 6hours, day, month or year
    :type zoom: str
    :param timezone: Timezone
    :type timezone: str
    """
    if zoom not in ["minute", "10minute", "hour", "6hours",
                    "day", "month", "year"]:
        raise AttributeError(
            "zoom must be in "
            "'minute', '10minute, 'hour', '6hours', 'day', 'month', 'year'"
            " not %s" % zoom)

    ts = floor_timestamp_for_interval(timestamp, zoom, timezone)
    if ts == timestamp:
        return ts

    if zoom in ["minute", "10minute", "hour", "6hours", "day"]:
        if zoom == "minute":
            td = timedelta(minutes=1)
        elif zoom == "10minute":
            td = timedelta(minutes=10)
        elif zoom == "hour":
            td = timedelta(hours=1)
        elif zoom == "6hours":
            td = timedelta(hours=6)
        elif zoom == "day":
            td = timedelta(days=1)

        dt = to_datetime(ts, timezone) + td
        return int(to_utc_timestamp(dt))

    if zoom in ["month", "year"]:
        if zoom == "month":
            dt = to_datetime(ts, timezone)
            y = dt.year
            m = dt.month + 1
            if m > 12:
                y += 1
                m -= 12
            dt = datetime(y, m, 1, tzinfo=pytz.timezone(timezone))
        if zoom == "year":
            dt = to_datetime(ts, timezone)
            y = dt.year + 1
            dt = datetime(y, 1, 1, tzinfo=pytz.timezone(timezone))
        return int(to_utc_timestamp(dt))


def floor_timestamp_for_file(timestamp, zoom, timezone):
    """Floors timestamp.
        second: 3600 seconds = 1 hour
        minute: 1440 minutes = 1 day
        hour:     24 hours   = 1 day
        6hours:    4 hours   = 1 day
        day:     365 days    = 1 year
        month:    12 months  = 1 year
        year:      1 year    = 1 year

    :param timestamp: Unix timestamp
    :param zoom: minute, 10minute, hour, 6hours, day, week, month or year
    :param timezone: Timezone
    """
    if zoom not in ["minute", "10minute", "hour", "6hours",
                    "day", "month", "year"]:
        raise AttributeError(
            "zoom must be in "
            "'minute', '10minute, 'hour', '6hours', 'day', 'month', 'year'"
            " not %s" % zoom)

    dt = to_datetime(timestamp, timezone)
    if zoom in ["minute", "10minute", "hour", "6hours"]:
        dt = datetime(dt.year, dt.month, dt.day,
                      tzinfo=pytz.timezone(timezone))
    elif zoom in ["day", "month", "year"]:
        dt = datetime(dt.year, 1, 1, tzinfo=pytz.timezone(timezone))

    return int(to_utc_timestamp(dt))


def ceil_timestamp_for_file(timestamp, zoom, timezone):
    """Ceils timestamp.
        second: 3600 seconds = 1 hour
        minute: 1440 minutes = 1 day
        hour:     24 hours   = 1 day
        6hours:    4 hours   = 1 day
        day:     365 days    = 1 year
        month:    12 months  = 1 year
        year:      1 year    = 1 year

    :param timestamp: Unix timestamp
    :param zoom: minute, hour, 6hours, day, week, month or year
    :param timezone: Timezone
    """
    if zoom not in ["minute", "10minute", "hour", "6hours",
                    "day", "month", "year"]:
        raise

    ts = floor_timestamp_for_file(timestamp, zoom, timezone)
    if ts == timestamp:
        return ts

    if zoom in ["minute", "hour", "6hours"]:
        td = timedelta(days=1)
        dt = to_datetime(ts, timezone) + td
        return int(to_utc_timestamp(dt))
    if zoom in ["day", "month", "year"]:
        dt = to_datetime(ts, timezone)
        dt = datetime(dt.year + 1, 1, 1, tzinfo=pytz.timezone(timezone))
        return int(to_utc_timestamp(dt))


def create_timestamps(sts, ets, zoom, timezone):
    """Creates timestamps from sts to ets based on zoom.

    Args:
        sts: Unix timestamp
        ets: Unix timestamp
        zoom: Zoom level
        timezone: Timezone

    Return:
        A list of timestamps
    """
    fsts = floor_timestamp_for_file(sts, zoom, timezone)
    cets = ceil_timestamp_for_file(ets, zoom, timezone)

    if zoom == "minute":
        return range(fsts, cets, 60)
    if zoom == "hour":
        return range(fsts, cets, 3600)
    if zoom == "6hours":
        return range(fsts, cets, 21600)
    if zoom == "day":
        # XXX not support DST.
        return range(fsts, cets, 86400)
    if zoom == "month":
        tss = []
        while fsts < cets:
            tss.append(fsts)
            fsts = ceil_timestamp_for_interval(fsts + 1, "month", timezone)
        return tss
    if zoom == "year":
        tss = []
        while fsts < cets:
            tss.append(fsts)
            fsts = ceil_timestamp_for_interval(fsts + 1, "year", timezone)
        return tss


def serialize_and_compress(dict_obj):
    """
    Compress dictionary object by gzip.
    :param dict_obj: serializing object
    :return Compressed data
    """
    fobj = StringIO.StringIO()
    gzipobj = gzip.GzipFile(fileobj=fobj, mode="wb")
    # try:
    #     gzipobj.write(msgpack.packb(dict_obj, encoding="utf-8"))
    # except:
    #     backward compatibility
    #     gzipobj.write(json.dumps(dict_obj))
    gzipobj.write(json.dumps(dict_obj))
    gzipobj.close()

    fobj.seek(0, 0)
    res = fobj.read()
    fobj.close()

    return res


def decompress_and_deserialize(cdata):
    """
    Decompress gzip object as dictionary.
    :param cdata: Compressed data
    :return dictionary object
    """
    gzipobj = gzip.GzipFile(fileobj=StringIO.StringIO(cdata))
    data = gzipobj.read()
    try:
        return msgpack.unpackb(data, encoding='utf-8')
    except:
        # backward compatibility
        return json.loads(data)


def is_none_data(data):
    """Checks if data is none or not.
    :param data: Common data format.
    :type data: data_container.CommonData
    :return True or False
    """
    return data['data'][0]['whp'].count(None) == len(data['data'][0]['whp'])


def call_with_retry(func, func_args, max_retry=10, retry_interval=10):
    """
    call function with retry. during retry any exception are ignored.
    :param func: the function to call
    :type func: Function
    :param func_args: arguments of function
    :type func_args: tuple
    :param max_retry: maximum retry count
    :type max_retry: int
    :param retry_interval: interval of next trial
    :type retry_interval: int
    :return: function's return value
    """
    try:
        return func(*func_args)
    except Exception as e:
        if max_retry <= 0:
            raise e
        __logger.info("retry to get data(%s) as %s.", max_retry, e.message)
        time.sleep(retry_interval)
        return call_with_retry(func, func_args, max_retry-1)


def accumulate(powers, interval, to_wh=True):
    """
    accumulate powers(Ws) and convert to Wh power
    :param powers: A list of Ws powers
    :type powers: list
    :param interval: interval of summation
    :type interval: int
    :param to_wh: if set True, calculate Wh
    :type to_wh: bool
    :return: A list of Wh powers
    """
    idx = 0
    res = []
    while idx < len(powers):
        ave = ave_without_none(powers[idx:idx + interval])
        if ave is not None:
            if to_wh:
                none_cnt = powers[idx:idx + interval].count(None)
                ave *= (interval - none_cnt) / 3600.0
            res.append(int(round(ave)))
        else:
            res.append(None)
        idx += interval

    return res


def main():
    # naive
    dt = datetime(1970, 1, 1)
    print dt, to_utc_timestamp(dt)

    # utc
    dt = datetime(1970, 1, 1, tzinfo=pytz.utc)
    print dt, to_utc_timestamp(dt)

    # jst
    dt = datetime(1970, 1, 1, tzinfo=pytz.timezone("Asia/Tokyo"))
    print dt, to_utc_timestamp(dt)

if __name__ == '__main__':
    main()
