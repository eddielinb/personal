import unittest
import pytz
import time
from datetime import datetime

import test_settings as settings
from waves import *
from google_drive import GoogleDrive

PATHS = ['test']


class TestWaves(unittest.TestCase):
    def setUp(self):
        self._data = {
            'data_type': 7,
            'version': 1,
            'mac': '1234567890abcdef',
            'time_zone': 'Asia/Tokyo',
            'timestamps': [],
            'rssi': [],
            'data': [],
            'voltages': [],
            'logs': {}
        }

    def tearDown(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        res = gd.retrieve_all_files("", PATHS, ["root"], contains=True)
        for r in res:
            gd.delete_file(r['id'])

        res = gd.retrieve_all_files("", [], [settings.WAVES_PARENT_ID], contains=True)
        for r in res:
            gd.delete_file(r['id'])

    def assert_waves(self, w1, w2):
        self.assertEqual(len(w1.keys()), len(w2.keys()))
        for k1, k2 in zip(sorted(w1.keys()), sorted(w2.keys())):
            self.assertEqual(k1, k2)
            self.assertEqual(w1[k1], w2[k2])

    def test_pack_and_compress(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)
        cdata = waves._pack_and_compress(self._data)
        self.assertNotEqual(self._data, cdata)

        res = waves._decompress_and_unpack(cdata)
        self.assert_waves(self._data, res)

    def test_get_filename(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = "1234567890abcdef"
        dt = datetime(2016, 1, 2, 3, tzinfo=pytz.utc)
        fn = waves._get_filename(mac, dt)
        self.assertEqual(fn, "2016010203_1234567890ABCDEF.gz")

    def test_download_waves(self):
        waves = Waves(settings.CREDENTIALS_FILE, "0B7-tDKsp2J8JUnF6b1Q2eWhEZEE")
        mac = "98F170FFFEFBB782"
        data = waves.download_waves(mac, 1467673200)
        self.assertIsInstance(data, dict)

    def test_download_waves_parallel(self):
        waves = Waves(settings.CREDENTIALS_FILE, "0B7-tDKsp2J8JUnF6b1Q2eWhEZEE")

        mac = "98F170FFFEFBB782"
        sts = 1467676799
        ets = 1467676801

        pt1 = time.time()

        data = waves.download_waves_parallel(mac, sts, ets)

        pt2 = st1 = time.time()

        data1 = waves.download_waves(mac, 1467673200)
        data2 = waves.download_waves(mac, 1467676800)
        str_list = ["timestamps", "rssi", "voltages"]
        str_list_data = ["root_powers", "waves"]
        for str_element in str_list:
            data1[str_element] = data1[str_element][3599:3600]
            data2[str_element] = data2[str_element][0:1]
        for str_element in str_list_data:
            for channel in range(len(data1["data"])):
                data1["data"][channel][str_element] = data1["data"][channel][str_element][3599:3600]
                data2["data"][channel][str_element] = data2["data"][channel][str_element][0:1]
        for ts_second in range(1467673200, 1467676800):
            if ts_second in data1["logs"].keys():
                del data1["logs"][ts_second]
        for ts_second in range(1467676801, 1467680400):
            if ts_second in data2["logs"].keys():
                del data2["logs"][ts_second]

        for str_element in str_list:
            data1[str_element].extend(data2[str_element])
        for str_element in str_list_data:
            for channel in range(len(data["data"])):
                data1["data"][channel][str_element].extend(data2["data"][channel][str_element])
        data1["logs"].update(data2["logs"])

        st2 = time.time()

        # print "Parallel time: {}".format(pt2 - pt1)
        # print "Series time: {}".format(st2 - st1)

        self.assert_waves(data, data1)

    def test_download_waves_parallel_with_2_files(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = '1234567890abcdef'
        ts = int(time.time()) / 3600 * 3600

        data1 = {
            'data_type': 7,
            'version': 1,
            'mac': mac,
            'time_zone': 'Asia/Tokyo',
            'timestamps': range(ts, ts + 3600),
            'rssi': range(3600),
            'data': [
                {
                    "channel": 1,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                },
                {
                    "channel": 2,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                }
            ],
            'voltages': [[i + j for j in range(64)] for i in range(3600)],
            'logs': {
                ts: {
                    "status_code": 1,
                    "sub_code": 2,
                    "count": 100
                }
            }
        }
        waves.upload_waves(data1, mac, ts)

        data2 = {
            'data_type': 7,
            'version': 1,
            'mac': mac,
            'time_zone': 'Asia/Tokyo',
            'timestamps': range(ts + 3600, ts + 3600 * 2),
            'rssi': range(3600),
            'data': [
                {
                    "channel": 1,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                },
                {
                    "channel": 2,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                }
            ],
            'voltages': [[i + j for j in range(64)] for i in range(3600)],
            'logs': {
                ts + 3600: {
                    "status_code": 1,
                    "sub_code": 2,
                    "count": 100
                }
            }
        }
        waves.upload_waves(data2, mac, ts + 3600)
        res = waves.download_waves_parallel(mac, ts + 3599, ts + 3601)
        for key in ["data_type", "version", "mac", "time_zone"]:
            self.assertEqual(res[key], data1[key])
        self.assertEqual(res['timestamps'], [ts + 3599, ts + 3600])
        self.assertEqual(res['data'][0]['channel'], 1)
        self.assertEqual(res['data'][0]['root_powers'], [3599, 0])
        self.assertEqual(res['data'][0]['waves'], [[3599 + j for j in range(64)], range(64)])
        self.assertEqual(res['data'][1]['channel'], 2)
        self.assertEqual(res['data'][1]['root_powers'], [3599, 0])
        self.assertEqual(res['data'][1]['waves'], [[3599 + j for j in range(64)], range(64)])
        self.assertEqual(res['logs'], data2['logs'])

    def test_download_waves_parallel_with_empty_data(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)
        mac = '1234567890abcdef'
        ts = int(time.time()) / 3600 * 3600

        data1 = {
            'data_type': 7,
            'version': 1,
            'mac': mac,
            'time_zone': 'Asia/Tokyo',
            'timestamps': range(ts, ts + 3600),
            'rssi': range(3600),
            'data': [
                {
                    "channel": 1,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                },
                {
                    "channel": 2,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                }
            ],
            'voltages': [[i + j for j in range(64)] for i in range(3600)],
            'logs': {
                ts: {
                    "status_code": 1,
                    "sub_code": 2,
                    "count": 100
                }
            }
        }
        waves.upload_waves(data1, mac, ts)

        data2 = {
            'data_type': 7,
            'version': 1,
            'mac': mac,
            'time_zone': 'Asia/Tokyo',
            'timestamps': range(ts + 3600, ts + 3600 * 2),
            'data': [],
            'logs': {}
        }
        waves.upload_waves(data2, mac, ts + 3600)
        res = waves.download_waves_parallel(mac, ts + 3599, ts + 3601)
        for key in ["data_type", "version", "mac", "time_zone"]:
            self.assertEqual(res[key], data1[key])
        self.assertEqual(res['timestamps'], [ts + 3599, ts + 3600])
        self.assertEqual(res['data'][0]['channel'], 1)
        self.assertEqual(res['data'][0]['root_powers'], [3599, None])
        self.assertEqual(res['data'][0]['waves'], [[3599 + j for j in range(64)], None])
        self.assertEqual(res['data'][1]['channel'], 2)
        self.assertEqual(res['data'][1]['root_powers'], [3599, None])
        self.assertEqual(res['data'][1]['waves'], [[3599 + j for j in range(64)], None])
        self.assertEqual(res['logs'], {})

    def test_download_waves_parallel_with_no_data(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = '1234567890abcdef'
        ts = int(time.time()) / 3600 * 3600

        data1 = {
            'data_type': 7,
            'version': 1,
            'mac': mac,
            'time_zone': 'Asia/Tokyo',
            'timestamps': range(ts, ts + 3600),
            'rssi': range(3600),
            'data': [
                {
                    "channel": 1,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                },
                {
                    "channel": 2,
                    "root_powers": range(3600),
                    "waves": [[i + j for j in range(64)] for i in range(3600)]
                }
            ],
            'voltages': [[i + j for j in range(64)] for i in range(3600)],
            'logs': {
                ts: {
                    "status_code": 1,
                    "sub_code": 2,
                    "count": 100
                }
            }
        }
        waves.upload_waves(data1, mac, ts)

        res = waves.download_waves_parallel(mac, ts + 3599, ts + 3601)
        for key in ["data_type", "version", "mac", "time_zone"]:
            self.assertEqual(res[key], data1[key])
        self.assertEqual(res['timestamps'], [ts + 3599, ts + 3600])
        self.assertEqual(res['data'][0]['channel'], 1)
        self.assertEqual(res['data'][0]['root_powers'], [3599, None])
        self.assertEqual(res['data'][0]['waves'], [[3599 + j for j in range(64)], None])
        self.assertEqual(res['data'][1]['channel'], 2)
        self.assertEqual(res['data'][1]['root_powers'], [3599, None])
        self.assertEqual(res['data'][1]['waves'], [[3599 + j for j in range(64)], None])
        self.assertEqual(res['logs'], {})

    def test_download_waves_parallel_hourly(self):
        waves = Waves(settings.CREDENTIALS_FILE, "0B7-tDKsp2J8JUnF6b1Q2eWhEZEE")

        mac = "98F170FFFEFBB782"
        sts = 1467676799
        ets = 1467676801

        pt1 = time.time()

        data = waves.download_waves_parallel(mac, sts, ets, hourly=True)

        pt2 = st1 = time.time()

        data1 = waves.download_waves(mac, 1467673200)
        data2 = waves.download_waves(mac, 1467676800)

        st2 = time.time()

        # print "Parallel time: {}".format(pt2 - pt1)
        # print "Series time: {}".format(st2 - st1)

        self.assert_waves(data[1467673200], data1)
        self.assert_waves(data[1467676800], data2)

    def test_download_waves_parallel_with_mac(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        sts = 1467676799
        ets = 1467676800

        # None
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=None,
                          sts=sts,
                          ets=ets)

        # empty
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac="",
                          sts=sts,
                          ets=ets)

        # invalid
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac="1234567890abcdeg",
                          sts=sts,
                          ets=ets)

        # short
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac="1234567890abcde",
                          sts=sts,
                          ets=ets)

        # long
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac="1234567890abcdeff",
                          sts=sts,
                          ets=ets
                          )

    def test_download_waves_parallel_with_ts(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = "1234567890abcdef"
        sts = 1467676799
        ets = 1467676800

        # None sts
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=mac,
                          sts=None,
                          ets=ets)

        # None ets
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=mac,
                          sts=sts,
                          ets=None)

        # empty
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=mac,
                          ts="")

        # negative
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=mac,
                          ts=-1)

        # float
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=mac,
                          sts=time.time(),
                          ets=time.time()+3600)

    def test_download_waves_parallel_with_data(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = "1234567890abcdef"
        sts = 1467676799
        ets = 1467676800

        # empty
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data="",
                          mac=mac,
                          sts=sts,
                          ets=ets)

        # no data
        self.assertRaises(Exception,
                          waves.download_waves_parallel,
                          data=self._data,
                          mac=mac,
                          sts=sts,
                          ets=ets)


    def test_upload_waves(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = '1234567890abcdef'
        ts = int(time.time())
        waves.upload_waves(self._data, mac, ts)

        data = waves.download_waves(mac, ts)
        self.assert_waves(data, self._data)

    def test_upload_waves_with_data(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = '1234567890abcdef'
        ts = int(time.time())

        # None
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=None,
                          mac=mac,
                          ts=ts)

        # empty
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data="",
                          mac=mac,
                          ts=ts)

    def test_upload_waves_with_mac(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        ts = int(time.time())

        # None
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac=None,
                          ts=ts)

        # empty
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac="",
                          ts=ts)

        # invalid
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac="1234567890abcdeg",
                          ts=ts)

        # short
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac="1234567890abcde",
                          ts=ts)

        # long
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac="1234567890abcdeff",
                          ts=ts)

    def test_upload_waves_with_ts(self):
        waves = Waves(settings.CREDENTIALS_FILE, settings.WAVES_PARENT_ID)

        mac = "1234567890abcdef"

        # None
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac=mac,
                          ts=None)

        # empty
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac=mac,
                          ts="")

        # negative
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac=mac,
                          ts=-1)

        # float
        self.assertRaises(Exception,
                          waves.upload_waves,
                          data=self._data,
                          mac=mac,
                          ts=time.time())
