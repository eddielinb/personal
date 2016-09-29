# -*- coding: utf-8 -*-
import unittest

import test_settings as settings
from gd_meter_info import *

PATHS = ['test']
INPUT_PATHS = PATHS + [u'入力']
OUTPUT_PATHS_SUCCEEDED = PATHS + [u'出力', u'成功']
OUTPUT_PATHS_FAILED = PATHS + [u'出力', u'失敗']


class TestGDMeterInfo(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        gd = GDMeterInfo(settings.CREDENTIALS_FILE, PATHS)
        res = gd.retrieve_all_files("", PATHS, ["root"], contains=True)
        for r in res:
            gd.delete_file(r['id'])

    def test_get_all_input_csv_files(self):
        gd = GDMeterInfo(settings.CREDENTIALS_FILE, PATHS)
        files = gd.get_all_input_csv_files()
        self.assertEqual(files, [])

        # input
        gd.upload_data("test1", [INPUT_PATHS], "20160601_1.csv")
        files = gd.get_all_input_csv_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # input - no csv
        gd.upload_data("test2", [INPUT_PATHS], "test2.txt")
        files = gd.get_all_input_csv_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # input - invalid filename / format
        gd.upload_data("test2", [INPUT_PATHS], "20160601-1.csv")
        files = gd.get_all_input_csv_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # input - invalid filename / date
        gd.upload_data("test2", [INPUT_PATHS], "20161602_1.csv")
        files = gd.get_all_input_csv_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # input - invalid filename / date
        gd.upload_data("test2", [INPUT_PATHS], "20160631_1.csv")
        files = gd.get_all_input_csv_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # output
        gd.upload_data("test3", [OUTPUT_PATHS_SUCCEEDED], "test3.csv")
        files = gd.get_all_input_csv_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

    def put_csv_data(self):
        gd = GDMeterInfo(settings.CREDENTIALS_FILE, PATHS)

        # succeeded
        files = gd.retrieve_all_files('', OUTPUT_PATHS_SUCCEEDED, ["root"], contains=True)
        self.assertEqual(files, [])

        gd.put_csv_data("20160601_1.csv", "csv data", succeeded=True)
        files = gd.retrieve_all_files('', OUTPUT_PATHS_SUCCEEDED, ["root"], contains=True)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # overwrite
        gd.put_csv_data("20160601_1.csv", "csv data", succeeded=True)
        files = gd.retrieve_all_files('', OUTPUT_PATHS_SUCCEEDED, ["root"], contains=True)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "20160601_1.csv")

        # failed
        files = gd.retrieve_all_files('', OUTPUT_PATHS_FAILED, ["root"], contains=True)
        self.assertEqual(files, [])

        gd.put_csv_data("test2.csv", "csv data", succeeded=False)
        files = gd.retrieve_all_files('', OUTPUT_PATHS_FAILED, ["root"], contains=True)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], "test2.csv")

    def put_csv_data_with_filename(self):
        gd = GDMeterInfo(settings.CREDENTIALS_FILE, PATHS)

        # None
        self.assertRaises(Exception,
                          gd.put_csv_data,
                          filename=None,
                          data="csv data",
                          succeeded=True)

        # empty
        self.assertRaises(Exception,
                          gd.put_csv_data,
                          filename='',
                          data="csv data",
                          succeeded=True)

    def put_csv_data_with_data(self):
        gd = GDMeterInfo(settings.CREDENTIALS_FILE, PATHS)

        # None
        self.assertRaises(Exception,
                          gd.put_csv_data,
                          filename="20160601_1.csv",
                          data=None,
                          succeeded=True)

        # empty
        self.assertRaises(Exception,
                          gd.put_csv_data,
                          filename='20160601_1.csv',
                          data='',
                          succeeded=True)

    def put_csv_data_with_succeeded(self):
        gd = GDMeterInfo(settings.CREDENTIALS_FILE, PATHS)

        # None
        self.assertRaises(Exception,
                          gd.put_csv_data,
                          filename="20160601_1.csv",
                          data="csv data",
                          succeeded=None)

        # empty
        self.assertRaises(Exception,
                          gd.put_csv_data,
                          filename="20160601_1.csv",
                          data="csv data",
                          succeeded="")
