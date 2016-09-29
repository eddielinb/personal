import unittest

from timestamp_utils import *


def utc_timestamp(dt):
    return calendar.timegm(dt.timetuple())


class TimestampTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_from_datetime(self):
        dt = datetime(2014, 3, 10, 1, 45, tzinfo=pytz.utc)
        ts = Timestamp.from_datetime(dt)
        self.assertEqual(utc_timestamp(ts.local_datetime),
                         utc_timestamp(ts.utc_datetime))

        dt = datetime(2014, 3, 10, 1, 45, tzinfo=pytz.timezone('Asia/Tokyo'))
        ts = Timestamp.from_datetime(dt)
        self.assertNotEqual(utc_timestamp(ts.local_datetime),
                            utc_timestamp(ts.utc_datetime))
        self.assertEqual(utc_timestamp(ts.utc_datetime), ts.timestamp)

    def test_add(self):
        dt = datetime(2014, 3, 10, 1, 45, tzinfo=pytz.utc)
        ts = Timestamp.from_datetime(dt)

        added = ts.add(minutes_to_seconds(30))
        correct = datetime(2014, 3, 10, 2, 15, tzinfo=pytz.utc)
        self.assertEqual(utc_timestamp(correct), added.timestamp)

        added = ts.add(hours_to_seconds(1))
        correct = datetime(2014, 3, 10, 2, 45, tzinfo=pytz.utc)
        self.assertEqual(utc_timestamp(correct), added.timestamp)

        added = ts.add(days_to_seconds(1))
        correct = datetime(2014, 3, 11, 1, 45, tzinfo=pytz.utc)
        self.assertEqual(utc_timestamp(correct), added.timestamp)

        dt = datetime(2014, 3, 10, 1, 45, tzinfo=pytz.timezone('Asia/Tokyo'))
        ts = Timestamp.from_datetime(dt)
        added = ts.add(minutes_to_seconds(30))
        correct = datetime(2014, 3, 10, 2, 15,
                           tzinfo=pytz.timezone('Asia/Tokyo'))
        self.assertEqual(utc_timestamp(correct.astimezone(pytz.utc)),
                         added.timestamp)
        self.assertEqual(added.local_datetime.hour, 2)
        self.assertEqual(added.local_datetime.minute, 15)

    def test_add_with_summertime(self):
        us_central_tz = pytz.timezone('US/Central')
        dt = us_central_tz.localize(datetime(2014, 3, 10, 1, 45))
        ts = Timestamp.from_datetime(dt)
        added = ts.add(minutes_to_seconds(30))
        correct = us_central_tz.localize(datetime(2014, 3, 10, 2, 15))
        self.assertEqual(utc_timestamp(correct.astimezone(pytz.utc)),
                         added.timestamp)
        self.assertEqual(added.local_datetime.hour, 2)
        self.assertEqual(added.local_datetime.minute, 15)

    def test_subtract(self):
        dt = datetime(2014, 3, 10, 2, 15, tzinfo=pytz.utc)
        ts = Timestamp.from_datetime(dt)
        sub = ts.subtract(minutes_to_seconds(30))
        correct = datetime(2014, 3, 10, 1, 45, tzinfo=pytz.utc)
        self.assertEqual(utc_timestamp(correct), sub.timestamp)

        dt = datetime(2014, 3, 10, 2, 15, tzinfo=pytz.timezone('Asia/Tokyo'))
        ts = Timestamp.from_datetime(dt)
        sub = ts.subtract(minutes_to_seconds(30))
        correct = datetime(2014, 3, 10, 1, 45,
                           tzinfo=pytz.timezone('Asia/Tokyo'))
        self.assertEqual(utc_timestamp(correct.astimezone(pytz.utc)),
                         sub.timestamp)
        self.assertEqual(sub.local_datetime.hour, 1)
        self.assertEqual(sub.local_datetime.minute, 45)

    def test_subtract_with_summertime(self):
        us_central_tz = pytz.timezone('US/Central')
        dt = us_central_tz.localize(datetime(2014, 3, 10, 2, 15))
        ts = Timestamp.from_datetime(dt)
        sub = ts.subtract(minutes_to_seconds(30))
        correct = us_central_tz.localize(datetime(2014, 3, 10, 1, 45))
        self.assertEqual(utc_timestamp(correct.astimezone(pytz.utc)),
                         sub.timestamp)
        self.assertEqual(sub.local_datetime.hour, 1)
        self.assertEqual(sub.local_datetime.minute, 45)
