import unittest
import zlib

from utils import *


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    # ---------------------------------
    # to_utc_timestamp
    # ---------------------------------
    def test_to_utc_timestamp(self):
        # naive

        # UK
        dt = datetime(1970, 1, 1, tzinfo=pytz.timezone("Europe/London"))
        ts = to_utc_timestamp(dt)
        self.assertEqual(int(ts), 60)

        # JST
        dt = datetime(1970, 1, 1, 9, tzinfo=pytz.timezone("Asia/Tokyo"))
        ts = to_utc_timestamp(dt)
        self.assertEqual(int(ts), 0)

    def test_to_utc_timestamp_with_dt(self):
        # None
        self.assertRaises(Exception,
                          to_utc_timestamp,
                          dt=None)

        # empty
        self.assertRaises(Exception,
                          to_utc_timestamp,
                          dt="")

        # zero
        self.assertRaises(Exception,
                          to_utc_timestamp,
                          dt=0)

    # ---------------------------------
    # to_datetime
    # ---------------------------------
    def test_to_datetime(self):
        # UK
        dt = datetime(1970, 1, 1, tzinfo=pytz.timezone("Europe/London"))
        res = to_datetime(60, timezone="Europe/London")
        self.assertEqual(dt, res)

        # JST
        dt = datetime(1970, 1, 1, 9, tzinfo=pytz.timezone("Asia/Tokyo"))
        res = to_datetime(0, timezone="Asia/Tokyo")
        self.assertEqual(dt, res)

    def test_to_datetime_with_timestamp(self):
        # None
        self.assertRaises(Exception,
                          to_datetime,
                          timestamp=None)

        # empty
        self.assertRaises(Exception,
                          to_datetime,
                          timestamp="")

    # ---------------------------------
    # localize
    # ---------------------------------
    def test_localize(self):
        # UK XXX DST
        #        dt = datetime(1970, 1, 1)
        #        res = localize(dt, "Europe/London")
        #        dt = datetime(1970, 1, 1, tzinfo=pytz.timezone("Europe/London"))
        #        self.assertEqual(dt, res)

        # JST
        dt = datetime(1970, 1, 1, 9)
        res = localize(dt, "Asia/Tokyo")
        dt = datetime(1970, 1, 1, 9, tzinfo=pytz.timezone("Asia/Tokyo"))
        self.assertEqual(dt, res)

    def test_localize_with_dt(self):
        # None
        self.assertRaises(Exception,
                          localize,
                          dt=None,
                          timestamp=0)

        # empty
        self.assertRaises(Exception,
                          localize,
                          dt="",
                          timestamp=0)

    def test_localize_with_timestamp(self):
        # None
        self.assertRaises(Exception,
                          localize,
                          dt=datetime.now(),
                          timestamp=None)

        # empty
        self.assertRaises(Exception,
                          localize,
                          dt=datetime.now(),
                          timestamp="")

    # ---------------------------------
    # convert_list_to_numpy
    # ---------------------------------
    def test_convert_list_to_numpy(self):
        arr = [None, 1, 2, None, 3]
        res = convert_list_to_numpy(arr)
        for i, j in zip(arr, res):
            if i is None:
                self.assertTrue(np.isnan(j))
            else:
                self.assertEqual(i, j)

    # ---------------------------------
    # convert_numpy_to_list
    # ---------------------------------
    def test_convert_numpy_to_list(self):
        nparr = np.array([np.nan, 1, 2, np.nan, 3])
        res = convert_numpy_to_list(nparr)
        for i, j in zip(nparr, res):
            if np.isnan(i):
                self.assertEqual(j, None)
            else:
                self.assertEqual(i, j)

    def test_convert_numpy_to_list_with_arr(self):
        # None
        self.assertRaises(Exception,
                          convert_numpy_to_list,
                          arr=None)

    # ---------------------------------
    # nansum
    # ---------------------------------
    def test_nansum(self):
        arr1 = np.array([np.nan, 1, 2, np.nan, np.nan])
        arr2 = np.array([np.nan, 3, np.nan, np.nan, 3])
        res = nansum(arr1, arr2)
        self.assertTrue(np.isnan(res[0]))
        self.assertTrue(res[1] == 4)
        self.assertTrue(res[2] == 2)
        self.assertTrue(np.isnan(res[3]))
        self.assertTrue(res[4] == 3)

    def test_nansum_with_arr(self):
        # None
        self.assertRaises(Exception,
                          nansum,
                          arr1=None,
                          arr2=np.array([0]))

        # None
        self.assertRaises(Exception,
                          nansum,
                          arr1=np.array([0]),
                          arr2=None)

    # ---------------------------------
    # sum_without_nan
    # ---------------------------------
    def test_sum_without_nan(self):
        arr = np.array([np.nan, 1, 2, np.nan, np.nan])
        self.assertEqual(sum_without_nan(arr), 3)

    def test_sum_without_nan_with_arr(self):
        # None
        self.assertRaises(Exception,
                          sum_without_nan,
                          arr=None)

    # ---------------------------------
    # floor_timestamp_for_interval
    # ---------------------------------
    def test_floor_timestamp_for_interval(self):
        ts = 54005
        for zoom in ["minute", "hour", "6hours", "day", "month", "year"]:
            fts = floor_timestamp_for_interval(ts, zoom, "Asia/Tokyo")
            if zoom in ["minute", "hour", "6hours", "day"]:
                self.assertEqual(fts, 54000)
            if zoom in ["month", "year"]:
                self.assertEqual(fts, -9 * 3600)

    def test_floor_timestamp_for_interval_with_timestamp(self):
        # None
        self.assertRaises(Exception,
                          floor_timestamp_for_interval,
                          ts=None,
                          zoom="minute",
                          timezone="Asia/Tokyo")

    def test_floor_timestamp_for_interval_with_zoom(self):
        # None
        self.assertRaises(Exception,
                          floor_timestamp_for_interval,
                          ts=0,
                          zoom=None,
                          timezone="Asia/Tokyo")

    def test_floor_timestamp_for_interval_with_timezone(self):
        # None
        self.assertRaises(Exception,
                          floor_timestamp_for_interval,
                          ts=0,
                          zoom="minute",
                          timezone="None")

    # ---------------------------------
    # ceil_timestamp_for_interval
    # ---------------------------------
    def test_ceil_timestamp_for_interval(self):
        ts = 53995
        for zoom in ["minute", "hour", "6hours", "day", "month", "year"]:
            fts = ceil_timestamp_for_interval(ts, zoom, "Asia/Tokyo")
            if zoom in ["minute", "hour", "6hours", "day"]:
                self.assertEqual(fts, 54000)
            if zoom in ["month"]:
                self.assertEqual(fts, 86400 * 31 - 9 * 3600)
            if zoom in ["year"]:
                self.assertEqual(fts, 86400 * 365 - 9 * 3600)

    def test_ceil_timestamp_for_interval_with_timestamp(self):
        # None
        self.assertRaises(Exception,
                          ceil_timestamp_for_interval,
                          ts=None,
                          zoom="minute",
                          timezone="Asia/Tokyo")

    def test_ceil_timestamp_for_interval_with_zoom(self):
        # None
        self.assertRaises(Exception,
                          ceil_timestamp_for_interval,
                          ts=0,
                          zoom=None,
                          timezone="Asia/Tokyo")

    def test_ceil_timestamp_for_interval_with_timezone(self):
        # None
        self.assertRaises(Exception,
                          ceil_timestamp_for_interval,
                          ts=0,
                          zoom="minute",
                          timezone="None")

    # ---------------------------------
    # floor_timestamp_for_file
    # ---------------------------------
    def test_floor_timestamp_for_file(self):
        ts = 54005
        for zoom in ["minute", "hour", "6hours", "day", "month", "year"]:
            fts = floor_timestamp_for_file(ts, zoom, "Asia/Tokyo")
            if zoom in ["minute", "hour", "6hours"]:
                self.assertEqual(fts, 54000)
            if zoom in ["day", "month", "year"]:
                self.assertEqual(fts, -9 * 3600)

    def test_floor_timestamp_for_file_with_timestamp(self):
        # None
        self.assertRaises(Exception,
                          floor_timestamp_for_file,
                          ts=None,
                          zoom="minute",
                          timezone="Asia/Tokyo")

    def test_floor_timestamp_for_file_with_zoom(self):
        # None
        self.assertRaises(Exception,
                          floor_timestamp_for_file,
                          ts=0,
                          zoom=None,
                          timezone="Asia/Tokyo")

    def test_floor_timestamp_for_file_with_timezone(self):
        # None
        self.assertRaises(Exception,
                          floor_timestamp_for_file,
                          ts=0,
                          zoom="minute",
                          timezone="None")

    # ---------------------------------
    # ceil_timestamp_for_file
    # ---------------------------------
    def test_ceil_timestamp_for_file(self):
        ts = 53995
        for zoom in ["minute", "hour", "6hours", "day", "month", "year"]:
            fts = ceil_timestamp_for_file(ts, zoom, "Asia/Tokyo")
            if zoom in ["minute", "hour", "6hours"]:
                self.assertEqual(fts, 54000)
            if zoom in ["day", "month", "year"]:
                self.assertEqual(fts, 86400 * 365 - 9 * 3600)

    def test_ceil_timestamp_for_file_with_timestamp(self):
        # None
        self.assertRaises(Exception,
                          ceil_timestamp_for_file,
                          ts=None,
                          zoom="minute",
                          timezone="Asia/Tokyo")

    def test_ceil_timestamp_for_file_with_zoom(self):
        # None
        self.assertRaises(Exception,
                          ceil_timestamp_for_file,
                          ts=0,
                          zoom=None,
                          timezone="Asia/Tokyo")

    def test_ceil_timestamp_for_file_with_timezone(self):
        # None
        self.assertRaises(Exception,
                          ceil_timestamp_for_file,
                          ts=0,
                          zoom="minute",
                          timezone="None")

    # ---------------------------------
    # create_timestamps
    # ---------------------------------
    def test_create_timestamps(self):
        for zoom in ["minute", "hour", "6hours", "day", "month", "year"]:
            tss = create_timestamps(54005, 54006, zoom, "Asia/Tokyo")
            if zoom == "minute":
                self.assertEqual(tss, range(54000, 54000 + 86400, 60))
            if zoom == "hour":
                self.assertEqual(tss, range(54000, 54000 + 86400, 3600))
            if zoom == "6hours":
                self.assertEqual(tss, range(54000, 54000 + 86400, 3600 * 6))
            if zoom == "day":
                self.assertEqual(
                    tss,
                    range(-9 * 3600, -9 * 3600 + 86400 * 365, 86400))
            if zoom == "month":
                res = []
                for i in range(1, 13):
                    dt = datetime(1970, i, 1,
                                  tzinfo=pytz.timezone("Asia/Tokyo"))
                    res.append(to_utc_timestamp(dt))
                self.assertEqual(tss, res)
            if zoom == "year":
                self.assertEqual(tss, [-9 * 3600])

    def test_create_timestamps_with_sts(self):
        # None
        self.assertRaises(Exception,
                          create_timestamps,
                          sts=None,
                          ets=54006,
                          zoom="minute",
                          timezone="Asia/Tokyo")

    def test_create_timestamps_with_ets(self):
        # None
        self.assertRaises(Exception,
                          create_timestamps,
                          sts=54005,
                          ets=None,
                          zoom="minute",
                          timezone="Asia/Tokyo")

    def test_create_timestamps_with_zoom(self):
        # None
        self.assertRaises(Exception,
                          create_timestamps,
                          sts=54005,
                          ets=54006,
                          zoom=None,
                          timezone="Asia/Tokyo")

    def test_create_timestamps_with_timezone(self):
        # None
        self.assertRaises(Exception,
                          create_timestamps,
                          sts=54005,
                          ets=54006,
                          zoom="minute",
                          timezone=None)

    # ---------------------------------
    # compress_json_by_gzip
    # ---------------------------------
    def test_compress_json_by_gzip(self):
        jsonobj = {"hoge": 1, "poge": 2}
        data = serialize_and_compress(jsonobj)

        self.assertNotEqual(data, jsonobj)

        res = decompress_and_deserialize(data)
        self.assertEqual(jsonobj, res)

    # ---------------------------------
    # decompress_as_json_by_gzip
    # ---------------------------------
    def test_decompress_as_json_by_gzip(self):
        jsonobj = {"hoge": 1, "poge": 2}
        data = serialize_and_compress(jsonobj)

        self.assertNotEqual(data, jsonobj)

        res = decompress_and_deserialize(data)
        self.assertEqual(jsonobj, res)

    def test_decompress_as_json_by_gzip_with_cdata(self):
        # None
        self.assertRaises(Exception,
                          decompress_and_deserialize,
                          cdata=None)

        # zlib
        jsonobj = {"hoge": 1, "poge": 2}
        cdata = zlib.compress(json.dumps(jsonobj))
        self.assertRaises(Exception,
                          decompress_and_deserialize,
                          cdata=cdata)

if __name__ == '__main__':
    unittest.main()
