# -*- coding: utf-8 -*-
import os
import sys
import io
import httplib2
import time
from datetime import datetime
from threading import Thread
from Queue import Queue
import copy

from apiclient import discovery
from apiclient import http
from oauth2client import file

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.base_io import ImCloudBase
from common.utils import call_with_retry


class GoogleDrive(ImCloudBase):
    def __init__(self, credentials_file):
        super(GoogleDrive, self).__init__()
        self.credentials_file = credentials_file
        credentials = self.get_credentials(credentials_file)
        self.credentials = credentials
        http_req = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http_req)

    def get_credentials(self, credentials_file):
        store = file.Storage(credentials_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            raise(Exception('not found credential file : ' + credentials_file))
        return credentials

    def _get_parent_ids(self, service, paths, parent_id):
        """
        Get parent folder ID
        :param service:
        :param paths: A list of path
        :param parent_id:
        :return: A list of parent_id
        """
        pids = []
        for path in paths:
            pid = parent_id
            for directory in path:
                search_query = "'%s' in parents and name='%s' and mimeType='application/vnd.google-apps.folder'" % (
                    pid, directory)
                list_results = service.files().list(
                    pageSize=1,
                    fields="nextPageToken, files(id)",
                    q=search_query).execute()
                items = list_results.get('files', [])
                if not items:
                    # create folder
                    folder_metadata = {
                        'name': directory,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [pid]
                    }
                    creted_folder = service.files().create(
                        body=folder_metadata, fields='id').execute()
                    pid = creted_folder['id']
                else:
                    pid = items[0]['id']
            pids.append(pid)

        if not paths:
            pids.append(parent_id)

        return pids

    def add_parents(self,file_id, parent_id):
        """
        Add parents for a file
        :param service:
        :param file_id:  File ID
        :param parent_id: List of new parent file ID
        :return: A list of parent File ID
        """
        file = self.service.files().update(fileId=file_id,
                                           addParents=parent_id,
                                           fields='id, parents').execute()
        self._logger.info("Total number of parents now is %d", len(file['parents']))
        return file['parents']

    def upload_data(self, data, to_paths, to_filename, mime_type="text/csv", parent_id='root',
                    max_retry=10, retry_interval=10, overwrite=True):
        """
        Upload data in memory.
        :param data:
        :param to_paths: A list of path
                         [[path, to, dir], [path, to, dir], ...]
        :param to_filename: Filename
        :param mime_type:
        :param parent_id: Parent folder ID
        :param max_retry: Max number of retry
        :param retry_interval: Interval second between retries
        :param overwrite: Bool
        :return:
        """
        # validations
        if not data:
            raise Exception("Invalid data: %s" % data)
        if not isinstance(to_paths, list):
            raise Exception("Invalid to_paths: %s" % to_paths)
        if not to_filename:
            raise Exception("filename not found: %s" % to_filename)

        # media
        if isinstance(data, io.BytesIO):
            fh = data
        else:
            fh = io.BytesIO(data)
        media = http.MediaIoBaseUpload(fh, mimetype=mime_type,
                                       chunksize=1024*1024, resumable=True)

        return call_with_retry(
            self._upload,
            (media, to_paths, to_filename, mime_type, parent_id, overwrite),
            max_retry,
            retry_interval
        )

    def upload_file(self, from_filename, to_paths, to_filename, mime_type="text/csv", parent_id='root',
                    max_retry=10, retry_interval=10, overwrite=True):
        """
        Upload a file.
        :param from_filename:
        :param to_paths: A list of directory
                         [[path, to, dir], [path, to, dir], ...]
        :param to_filename: Filename
        :param mime_type:
        :param parent_id: Parent folder ID
        :param max_retry: Max number of retry
        :param retry_interval: Interval second between retries
        :param overwrite: Bool
        :return:
        """
        # validations
        if not from_filename:
            raise Exception("Invalid from_filename: %s" % from_filename)
        if not isinstance(to_paths, list):
            raise Exception("Invalid to_paths: %s" % to_paths)
        if not to_filename:
            raise Exception("filename not found: %s" % to_filename)

        # media
        media = http.MediaFileUpload(from_filename, mimetype=mime_type,
                                     chunksize=1024*1024, resumable=True)

        return call_with_retry(
            self._upload,
            (media, to_paths, to_filename, mime_type, parent_id, overwrite),
            max_retry,
            retry_interval
        )

    def _upload(self, media, to_paths, to_filename, mime_type, parent_id, overwrite=True):
        """
        Upload data to Google Drive.
        If a directory is not found, the directory will be created in Google Drive.
        :param media: MediaBaseUpload object
        :param to_paths: A list of directory
                         [[path, to, dir], [path, to, dir], ...]
        :param to_filename: Filename
        :param mime_type:
        :param parent_id: Parent folder ID
        :param overwrite: Bool
        :return:
        """
        # parent id
        parent_ids = self._get_parent_ids(self.service, to_paths, parent_id)
        self._logger.info("Parent IDs: %s", parent_ids)

        uploaded = False
        if overwrite:
            fids = self.retrieve_all_files(to_filename, [], parent_ids)
            self._logger.info("FIDs: %s", fids)
            if fids:
                file_metadata = {
                    'modifiedTime': datetime.utcnow().isoformat() + 'Z'
                }
                self.service.files().update(fileId=fids[0]['id'],
                                            body=file_metadata,
                                            fields='id, modifiedTime', media_body=media).execute()
                self._logger.info("Completed to update: %s, %s", to_paths, to_filename)
                uploaded = True

        if not uploaded:
            file_metadata = {
                'name': to_filename,
                'mimeType': mime_type,
                'parents': parent_ids
            }
            self.service.files().create(body=file_metadata,
                                        fields='id', media_body=media).execute()
            self._logger.info("Completed to upload: %s, %s", to_paths, to_filename)

    def download_file(self, file_id):
        """
        Download a file whose ID is fild_id
        :param file_id: File ID
        :return: Downloaded bytes
        """
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = http.MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            self._logger.info("Download %d%%" % int(status.progress() * 100))

        return fh.getvalue()

    def download_list_of_files(self, file_id):
        """
        Download a list of files whose IDs is file_id
        :param file_id: a list of File ID
        :return: Dictionary of downloaded files
        """
        returns = {}
        # Create a queue to communicate with the worker threads
        queue = Queue()
        queue_data = Queue()
        # Create 4 worker threads
        for numbers in xrange(8):
            worker = DownloadWorker(queue, queue_data, self.credentials_file)
            worker.daemon = True
            worker.start()
            #response = queue.get()
            #returns.append(response)

        for file in file_id:
            queue.put(file)
            self._logger.info('Queueing %s' % file)
        queue.join()
        for file in file_id:
            temp = queue_data.get()
            returns[temp.keys()[0]] = temp.values()[0]
        return returns


    def delete_file(self, file_id):
        """
        Delet a file whose ID is fild_id
        :param file_id: File ID
        :return:
        """
        self.service.files().delete(fileId=file_id).execute()

    def retrieve_all_files(self, key, paths, parent_ids=None, contains=False):
        """
        Retrieve all file information
        :param key: Key
        :param paths: A list of directory
                      [path, to, dir]
        :param parent_ids: A list of parent_id
        :param contains: Boolean
        :return:
        """
        # Cannot set [] as default value because list is mutable.
        if parent_ids is None:
            parent_ids = []

        # validations
        if key is None:
            raise Exception("Invalid Key: %s" % key)
        if not isinstance(paths, list):
            raise Exception("Invalid paths: %s" % paths)
        if not isinstance(parent_ids, list):
            raise Exception("Invalid parent_ids: %s" % parent_ids)

        for path in paths:
            res = self.retrieve_files_with_parent(path, parent_ids)
            if res:
                parent_ids = [r.get('id') for r in res]
            else:
                return []

        return self.retrieve_files_with_parent(key, parent_ids, contains)

    def retrieve_files_with_parent(self, key, parent_ids=None, contains=False):
        """
        Retrieve files under parent
        :param key: Key
        :param parent_ids: A list of parent_id
        :param contains: Boolean
        :return: A list of file
        """
        # Cannot set [] as default value because list is mutable.
        if parent_ids is None:
            parent_ids = []

        # validation
        if key is None:
            raise Exception("Inalid Key: %s" % key)
        if not isinstance(parent_ids, list):
            raise Exception("Invalid parent_ids: %s" % parent_ids)
        if contains not in [True, False]:
            raise Exception("Invalid contains: %s" % contains)

        result = []
        page_token = None
        while True:
            if contains:
                query = "name contains '%s'" % key
            else:
                query = "name='%s'" % key
            if parent_ids:
                query += " and ("
                for parent_id in parent_ids:
                    query += "'%s' in parents or " % parent_id
                query = query[:-4] + ")"
            self._logger.info(query)
            response = self.service.files().list(q=query,
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id, name)',
                                                 pageToken=page_token).execute()
            result.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return result


class DownloadWorker(Thread):
    def __init__(self, queue, queue_data, credentials_file):
        Thread.__init__(self)
        self.queue = queue
        self.queue_data = queue_data
        self.credentials_file = (credentials_file)

    def run(self):
        """
        """
        while True:
            file_id = self.queue.get()
            try:
                data = call_with_retry(GoogleDrive(self.credentials_file).download_file,
                                       file_id=file_id, max_retry=10, retry_interval=10)
                #data = GoogleDrive(self.credentials_file).download_file(file_id=file_id)
            except:
                data = None
            finally:
                data = {file_id: data}
                self.queue_data.put(data)
                self.queue.task_done()




def main():
    import argparse

    from common.logger import setup_logger
    credentials = "tests/unittest_credentials.json"

    # Samples
    #
    # Upload a sample.txt to the below
    #    Test/parent1/sample.txt
    #    Test/parent2/sample.txt
    # $ python google_drive.py put -ff sample.txt -tp "Test/parent1, Test/parent2" -tf sample.txt -m text/plain
    #
    # Retrieve the fileID of sample.txt
    # $ python google_drive.py list -fn sample.txt -p Test/parent1
    #
    # Download sample.txt
    # $ python google_drive.py get -fid 0B-y2EPc2m4U5UjlYc0VGT1BhZ0U
    #

    # args
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(help='sub-command help')

    # put
    sp_put = subparsers.add_parser('put', help='Upload file')
    sp_put.set_defaults(cmd='put')
    sp_put.add_argument('-ff', '--from_filename',
                        required=True,
                        help="From filename")
    sp_put.add_argument('-tp', '--to_paths',
                        required=True,
                        help="Comma-Separated Paths to directory")
    sp_put.add_argument('-tf', '--to_filename',
                        required=True,
                        help="To filename")
    sp_put.add_argument('-m', '--mime_type',
                        required=False,
                        default="text/csv",
                        help="MIME type")
    sp_put.add_argument('-p', '--parent_id',
                        required=False,
                        default="root",
                        help="Parent folder ID")
    sp_put.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help="Make the operation more talkative")

    # update
    sp_update = subparsers.add_parser('update', help='Update file')
    sp_update.set_defaults(cmd='update')
    sp_update.add_argument('-ff', '--from_filename',
                           required=True,
                           help="From filename")
    sp_update.add_argument('-tp', '--to_paths',
                           required=True,
                           help="Comma-Separated Paths to directory")
    sp_update.add_argument('-tf', '--to_filename',
                           required=True,
                           help="To filename")
    sp_update.add_argument('-m', '--mime_type',
                           required=False,
                           default="text/csv",
                           help="MIME type")
    sp_update.add_argument('-p', '--parent_id',
                           required=False,
                           default="root",
                           help="Parent folder ID")
    sp_update.add_argument('-v', '--verbose',
                           action='store_true',
                           default=False,
                           help="Make the operation more talkative")

    # list
    sp_list = subparsers.add_parser('list', help='Get all file information')
    sp_list.set_defaults(cmd='list')
    sp_list.add_argument('-k', '--key',
                         required=False,
                         default=None,
                         help="Keyword")
    sp_list.add_argument('-fn', '--filename',
                         required=False,
                         default=None,
                         help="Filename")
    sp_list.add_argument('-p', '--paths',
                         required=False,
                         default=None,
                         help="Paths")
    sp_list.add_argument('-v', '--verbose',
                         action='store_true',
                         default=False,
                         help="Make the operation more talkative")

    # get
    sp_get = subparsers.add_parser('get', help='Download files')
    sp_get.set_defaults(cmd='get')
    sp_get.add_argument('-fid', '--file_id',
                        required=True,
                        nargs='+',
                        help="File ID")
    sp_get.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help="Make the operation more talkative")

    # add parent
    sp_get = subparsers.add_parser('addParent', help='Add parents to file')
    sp_get.set_defaults(cmd='addParent')
    sp_get.add_argument('-fid', '--file_id',
                        required=True,
                        help="File ID and parent ID")
    sp_get.add_argument('-pid', '--parent_id',
                        required=True,
                        help="File ID and parent ID")
    sp_get.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help="Make the operation more talkative")

    args = parser.parse_args()

    # logger
    setup_logger('GoogleDrive', '/tmp/google_drive.log', verbose=args.verbose)

    gdrive = GoogleDrive(credentials)
    if args.cmd == 'put':
        paths = args.to_paths.split(',')
        to_paths = [path.strip().split('/') for path in paths]

        gdrive.upload_file(args.from_filename,
                           to_paths,
                           args.to_filename,
                           mime_type=args.mime_type,
                           parent_id=args.parent_id,
                           overwrite=False)

    if args.cmd == 'update':
        paths = args.to_paths.split(',')
        to_paths = [path.strip().split('/') for path in paths]

        gdrive.upload_file(args.from_filename,
                           to_paths,
                           args.to_filename,
                           mime_type=args.mime_type,
                           parent_id=args.parent_id)

    if args.cmd == 'list':
        if args.paths is None:
            paths = []
        else:
            paths = args.paths.split('/')

        if args.key is None:
            if args.filename is None:
                print "Please input key or filename."
                exit(1)
            res = gdrive.retrieve_all_files(args.filename, paths, [], False)
        else:
            res = gdrive.retrieve_all_files(args.key, paths, [], True)

        if res:
            print "%d Files were found." % len(res)
            for r in res:
                print r.get('name'), r.get('id')
        else:
            print "Files were not found."

    if args.cmd == 'get':
        #bd = gdrive.download_file(args.file_id)
        bd = gdrive.download_list_of_files(args.file_id)
        print "Length: %s" % len(bd)
        # print bytes

    if args.cmd =='addParent':
        pids = gdrive.add_parents(args.file_id, args.parent_id)
        print "Parents ID: %s" % pids

if __name__ == '__main__':
    main()
