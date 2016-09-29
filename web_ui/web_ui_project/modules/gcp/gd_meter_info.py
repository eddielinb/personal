# -*- coding: utf-8 -*-
import re
from datetime import datetime

from google_drive import GoogleDrive


class GDMeterInfo(GoogleDrive):
    __INPUT_DIRECTORY = u'入力'
    __OUTPUT_DIRECTORY = u'出力'
    __SUCCEEDED_DIRECTORY = u'成功'
    __FAILED_DIRECTORY = u'失敗'

    def __init__(self, credentials_file, paths=None):
        """
        Constructor
        :param credentials_file: A filename of credentials_file
        :param paths: A list of directory from root
                      [path, to, dir]
        :return:
        """
        super(GDMeterInfo, self).__init__(credentials_file)
        if paths is None:
            self._paths = []
        else:
            self._paths = paths

    def _validate_input_filename(self, fn):
        """
        Validate input filename
        :param fn: filename
        :return: True or False
        """
        try:
            if not re.match('[0-9]{8}_[0-9].csv', fn):
                raise Exception('Invalid filename: %s', fn)
            datetime(int(fn[0:4]), int(fn[4:6]), int(fn[6:8]))
        except:
            return False
        return True

    def get_all_input_csv_files(self):
        """
        Get all input csv files from Google Drive.
        The file must be under "入力" directory and filename must be "YYYYMMDD_N.csv".
        :return:
        """
        paths = self._paths + [self.__INPUT_DIRECTORY]
        files = self.retrieve_all_files('csv', paths, parent_ids=["root"], contains=True)
        res = []
        for f in files:
            if self._validate_input_filename(f['name']):
                res.append(f)
            else:
                self._logger.warning("Invalid input filename: %s", f['name'])

        return res

    def put_csv_data(self, filename, data, succeeded=True):
        if succeeded:
            paths = [self._paths + [self.__OUTPUT_DIRECTORY, self.__SUCCEEDED_DIRECTORY]]
        else:
            paths = [self._paths + [self.__OUTPUT_DIRECTORY, self.__FAILED_DIRECTORY]]

        self.upload_data(data, paths, filename, mime_type="text/csv", parent_id="root")


def main():
    import argparse
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from common.logger import setup_logger

    credentials = "./tests/unittest_credentials.json"
    paths = []

    # Samples
    #
    # Get a list of input files
    # $ python dg_meter_info.py list
    #
    # Download a csv file
    # $ python dg_meter_info.py get -fid 0B-y2EPc2m4U5UjlYc0VGT1BhZ0U
    #
    # Upload a succeeded csv file
    # $ python dg_meter_info.py put -f xxxxxx.csv -d data -m succeeded

    # args
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(help='sub-command help')

    # list
    sp_list = subparsers.add_parser('list', help='Get a list of input files')
    sp_list.set_defaults(cmd='list')
    sp_list.add_argument('-v', '--verbose',
                         action='store_true',
                         default=False,
                         help="Make the operation more talkative")

    # get
    sp_get = subparsers.add_parser('get', help='Download files')
    sp_get.set_defaults(cmd='get')
    sp_get.add_argument('-fid', '--file_id',
                        required=True,
                        help="File ID")
    sp_get.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help="Make the operation more talkative")

    # put
    sp_put = subparsers.add_parser('put', help='Upload file')
    sp_put.set_defaults(cmd='put')
    sp_put.add_argument('-f', '--filename',
                        required=True,
                        help="Filename")
    sp_put.add_argument('-d', '--data',
                        required=True,
                        help="CSV data")
    sp_put.add_argument('-m', '--mode',
                        choices=('succeeded', 'failed'),
                        help="Upload csv data to succeeded directory or failed directory")
    sp_put.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help="Make the operation more talkative")

    args = parser.parse_args()

    # logger
    setup_logger('GDMeterInfo', '/tmp/dg_meter_info.log', verbose=args.verbose)

    gd = GDMeterInfo(credentials, paths)
    if args.cmd == 'list':
        files = gd.get_all_input_csv_files()
        for f in files:
            print f['id'], f['name']

    if args.cmd == 'get':
        data = gd.download_file(args.file_id)
        print data.decode('sjis')

    if args.cmd == 'put':
        if args.mode == 'succeeded':
            gd.put_csv_data(args.filename, args.data, True)
        if args.mode == 'failed':
            gd.put_csv_data(args.filename, args.data, False)


if __name__ == '__main__':
    main()
