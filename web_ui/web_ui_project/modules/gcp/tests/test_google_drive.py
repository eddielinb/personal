import unittest

import test_settings as settings
from google_drive import *

PATHS = ['test']


class TestGoogleDrive(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        res = gd.retrieve_all_files("", PATHS, ["root"], contains=True)
        for r in res:
            gd.delete_file(r['id'])

    def test_get_credentials(self):
        GoogleDrive(settings.CREDENTIALS_FILE)

    def test_get_credentials_with_credentials_file(self):
        # dummy
        self.assertRaises(Exception,
                          GoogleDrive,
                          settings.DUMMY_CREDENTIALS_FILE)

        # no file
        self.assertRaises(Exception,
                          GoogleDrive,
                          "hoge")

        # None
        self.assertRaises(Exception,
                          GoogleDrive,
                          None)

    def test_upload_data(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

    def test_upload_data_with_data(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        # None
        self.assertRaises(Exception,
                          gd.upload_data,
                          data=None,
                          to_paths=[PATHS],
                          to_filename="test1.txt")

        # empty
        self.assertRaises(Exception,
                          gd.upload_data,
                          data="",
                          to_paths=[PATHS],
                          to_filename="test1.txt")

        # BytesIO
        bio = io.BytesIO(b"\x00\x01")
        gd.upload_data(bio, [PATHS], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, b"\x00\x01")

    def test_upload_data_with_to_paths(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        # None
        self.assertRaises(Exception,
                          gd.upload_data,
                          data="test1",
                          to_paths=None,
                          to_filename="test1.txt")

        # empty
        self.assertRaises(Exception,
                          gd.upload_data,
                          data="test1",
                          to_paths="",
                          to_filename="test1.txt")

        # paths
        gd.upload_data("test1", [PATHS, PATHS + ["hoge"]], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

        res = gd.retrieve_all_files("test1.txt", PATHS + ["hoge"])
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

    def test_upload_data_with_to_filename(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        # None
        self.assertRaises(Exception,
                          gd.upload_data,
                          data="test1",
                          to_paths=[PATHS],
                          to_filename=None)

        # empty
        self.assertRaises(Exception,
                          gd.upload_data,
                          data="test1",
                          to_paths=[PATHS],
                          to_filename="")

    def test_upload_data_with_overwrite(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        gd.upload_data("test1", [PATHS], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

        gd.upload_data("test2", [PATHS], "test1.txt")
        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test2")

        gd.upload_data("test1", [PATHS], "test1.txt", overwrite=False)
        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 2)

    def test_upload_file(self):
        filename = "/tmp/test_google_drive"
        fp = open(filename, "w")
        fp.write("test1")
        fp.close()

        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_file(filename, [PATHS], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

    def test_upload_file_with_from_filename(self):
        filename = "/tmp/test_google_drive"
        fp = open(filename, "w")
        fp.write("test1")
        fp.close()

        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        # None
        self.assertRaises(Exception,
                          gd.upload_file,
                          from_filename=None,
                          to_paths=[PATHS],
                          to_filename="test1.txt")

        # empty
        self.assertRaises(Exception,
                          gd.upload_file,
                          from_filename="",
                          to_paths=[PATHS],
                          to_filename="test1.txt")

    def test_upload_file_with_to_paths(self):
        filename = "/tmp/test_google_drive"
        fp = open(filename, "w")
        fp.write("test1")
        fp.close()

        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        # None
        self.assertRaises(Exception,
                          gd.upload_file,
                          from_filename=filename,
                          to_paths=None,
                          to_filename="test1.txt")

        # empty
        self.assertRaises(Exception,
                          gd.upload_file,
                          from_filename=filename,
                          to_paths="",
                          to_filename="test1.txt")

        # paths
        gd.upload_file(filename, [PATHS, PATHS + ["hoge"]], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

        res = gd.retrieve_all_files("test1.txt", PATHS + ["hoge"])
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

    def test_upload_file_with_to_filename(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        # None
        self.assertRaises(Exception,
                          gd.upload_file,
                          from_filename="test1",
                          to_paths=[PATHS],
                          to_filename=None)

        # empty
        self.assertRaises(Exception,
                          gd.upload_file,
                          from_filename="test1",
                          to_paths=[PATHS],
                          to_filename="")

    def test_upload_file_with_overwrite(self):
        filename = "/tmp/test_google_drive"
        fp = open(filename, "w")
        fp.write("test1")
        fp.close()

        gd = GoogleDrive(settings.CREDENTIALS_FILE)

        gd.upload_file(filename, [PATHS], "test1.txt")

        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

        gd.upload_file(filename, [PATHS], "test1.txt")
        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        data = gd.download_file(res[0]['id'])
        self.assertEqual(data, "test1")

        gd.upload_file(filename, [PATHS], "test1.txt", overwrite=False)
        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 2)

    def test_download_file(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")
        res = gd.retrieve_all_files("test1.txt", PATHS)
        data = gd.download_file(res[0]['id'])
        self.assertEqual("test1", data)

    def test_download_file_with_file_id(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")
        gd.retrieve_all_files("test1.txt", PATHS)

        # None
        self.assertRaises(Exception,
                          gd.download_file,
                          file_id=None)

        # empty
        self.assertRaises(Exception,
                          gd.download_file,
                          file_id="")

        # unknown
        self.assertRaises(Exception,
                          gd.download_file,
                          file_id="hoge")

    def test_download_list_of_files(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        files =[]
        number_of_files = 6
        for file_number in range (number_of_files):
            gd.upload_data(("test %s" % file_number), [PATHS], ("test%s.txt" % file_number))
            files.append(gd.retrieve_all_files((("test%s.txt") %file_number),PATHS)[0]['id'])
        data = gd.download_list_of_files(files)
        for file_number in range (number_of_files):
            for download_data in data:
               if ("test%s" % file_number)== download_data:
                   self.assertEqual(("test%s" % file_number), download_data)

    def test_download_list_of_files_with_file_id(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")
        gd.retrieve_all_files("test1.txt", PATHS)

        # None
        self.assertRaises(Exception,
                          gd.download_list_of_files,
                          file_id=None)

        # empty
        self.assertRaises(Exception,
                          gd.download_list_of_files,
                          file_id="")

        # unknown
        self.assertRaises(Exception,
                          gd.download_list_of_files,
                          file_id="hoge")

    def test_delete_file(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")
        res = gd.retrieve_all_files("test1.txt", PATHS)

        gd.delete_file(res[0]['id'])

        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(res, [])

    def test_delete_file_with_file_id(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")
        gd.retrieve_all_files("test1.txt", PATHS)

        # None
        self.assertRaises(Exception,
                          gd.delete_file,
                          file_id=None)

        # empty
        self.assertRaises(Exception,
                          gd.delete_file,
                          file_id="")

        # unknown
        self.assertRaises(Exception,
                          gd.delete_file,
                          file_id="hoge")

    def test_retrieve_all_files(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(res, [])

        gd.upload_data("test1", [PATHS], "test1.txt")
        res = gd.retrieve_all_files("test1.txt", PATHS)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test1.txt")

    def test_retrieve_all_files_with_key(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test.txt")

        # None
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key=None,
                          paths=PATHS)

        # empty
        res = gd.retrieve_all_files(
            key="",
            paths=PATHS)
        self.assertEqual(res, [])

        # not match
        res = gd.retrieve_all_files(
            key="hoge",
            paths=PATHS)
        self.assertEqual(res, [])

        # Upper
        res = gd.retrieve_all_files(
            key="TEST.TXT",
            paths=PATHS)
        self.assertEqual(res, [])

        # contains
        res = gd.retrieve_all_files(
            key="t",
            paths=PATHS,
            contains=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test.txt")

    def test_retrieve_all_files_with_paths(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test.txt")

        # None
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=None)

        # empty
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths="")

        # [None]
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=[None])

        # [""]
        res = gd.retrieve_all_files(
            key="test.txt",
            paths=[""])
        self.assertEqual(res, [])

        res = gd.retrieve_all_files(
            key="test.txt",
            paths=[""],
            contains=True)
        self.assertEqual(res, [])

        # Upper
        res = gd.retrieve_all_files(
            key="test.txt",
            paths=["TEST"])
        self.assertEqual(res, [])

    def test_retrieve_all_files_with_parent_ids(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test.txt")

        # None
        res = gd.retrieve_all_files(
            key="test.txt",
            paths=PATHS,
            parent_ids=None)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test.txt")

        # empty
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=PATHS,
                          parent_ids="")

        # [""]
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=PATHS,
                          parent_ids=[""])

        # unknow
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=PATHS,
                          parent_ids=['unknow_parent_id'])

    def test_retrieve_all_files_with_contains(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test.txt")

        # None
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=PATHS,
                          contains=None)

        # empty
        self.assertRaises(Exception,
                          gd.retrieve_all_files,
                          key="test.txt",
                          paths=PATHS,
                          contains="")

        # True
        res = gd.retrieve_all_files(
            key="t",
            paths=PATHS,
            contains=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test.txt")

        # False
        res = gd.retrieve_all_files(
            key="t",
            paths=PATHS,
            contains=False)
        self.assertEqual(res, [])

        # zero
        res = gd.retrieve_all_files(
            key="t",
            paths=PATHS,
            contains=0)
        self.assertEqual(res, [])

    def test_retrieve_files_with_parent(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        res = gd.retrieve_files_with_parent("test1.txt")
        self.assertEqual(res, [])

        gd.upload_data("test1", [PATHS], "test1.txt")
        res = gd.retrieve_files_with_parent("test1.txt")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test1.txt")

    def test_retrieve_files_with_parent_with_key(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")

        # None
        self.assertRaises(Exception,
                          gd.retrieve_files_with_parent,
                          key=None)

        # empty
        res = gd.retrieve_files_with_parent(
            key="")
        self.assertEqual(res, [])

        # not match
        res = gd.retrieve_files_with_parent(
            key="hoge")
        self.assertEqual(res, [])

        # Upper
        res = gd.retrieve_files_with_parent(
            key="TEST1.TXT")
        self.assertEqual(res, [])

        # contains
        res = gd.retrieve_files_with_parent(
            key="t",
            contains=True)
        self.assertEqual(len(res), 2)
        res = gd.retrieve_files_with_parent(
            key="test1.tx",
            contains=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test1.txt")

    def test_retrieve_files_with_parent_with_parent_ids(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")

        # None
        res = gd.retrieve_files_with_parent(
            key="test1.txt",
            parent_ids=None)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "test1.txt")

        # empty
        self.assertRaises(Exception,
                          gd.retrieve_files_with_parent,
                          key="test1.txt",
                          parent_ids="")

        # [""]
        self.assertRaises(Exception,
                          gd.retrieve_files_with_parent,
                          key="test1.txt",
                          parent_ids=[""])

        # unknow
        self.assertRaises(Exception,
                          gd.retrieve_files_with_parent,
                          key="test1.txt",
                          parent_ids=['unknow_parent_id'])

    def test_retrieve_files_with_parent_with_contains(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1", [PATHS], "test1.txt")

        # None
        self.assertRaises(Exception,
                          gd.retrieve_files_with_parent,
                          key="test1.txt",
                          contains=None)

        # empty
        self.assertRaises(Exception,
                          gd.retrieve_files_with_parent,
                          key="test1.txt",
                          contains="")

        # True
        res = gd.retrieve_files_with_parent(
            key="t",
            contains=True)
        self.assertEqual(len(res), 2)

        # False
        res = gd.retrieve_files_with_parent(
            key="t",
            contains=False)
        self.assertEqual(res, [])

        # zero
        res = gd.retrieve_files_with_parent(
            key="t",
            contains=0)
        self.assertEqual(res, [])

    def test_add_parents_invalid_cases(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        # None file_id
        self.assertRaises(Exception,
                          gd.add_parents,
                          file_id=None)

        # empty file_id
        self.assertRaises(Exception,
                          gd.add_parents,
                          file_id="")

        # unknown file_id
        self.assertRaises(Exception,
                          gd.add_parents,
                          file_id="hoge")


        # None parent_id
        self.assertRaises(Exception,
                          gd.add_parents,
                          parent_id=None)

        # empty parent_id
        self.assertRaises(Exception,
                          gd.add_parents,
                          parent_id="")

        # unknown parent_id
        self.assertRaises(Exception,
                          gd.add_parents,
                          parent_id="hoge")

    def test_add_parents(self):
        gd = GoogleDrive(settings.CREDENTIALS_FILE)
        gd.upload_data("test1",[['test', 'test1_folder']], "test1.txt")
        gd.upload_data("test2",[['test', 'test2_folder']], "test2.txt")
        fid = gd.retrieve_all_files("test1.txt", ['test', 'test1_folder'])
        pid = gd.retrieve_all_files("test2_folder", ['test'])
        self.assertEqual([], gd.retrieve_all_files("test1.txt", ['test', 'test2_folder']))
        gd.add_parents(fid[0]['id'], pid[0]['id'])
        file_check = gd.retrieve_all_files("test1.txt", ['test', 'test2_folder'])
        self.assertEqual(fid[0]['id'], file_check[0]['id'])
