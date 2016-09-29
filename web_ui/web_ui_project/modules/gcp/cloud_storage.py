import os
import sys
import logging
import io
import time
import msgpack as packer
import msgpack_numpy as m
m.patch()
from apiclient import discovery
from googleapiclient.http import MediaIoBaseDownload, MediaInMemoryUpload, MediaFileUpload
from googleapiclient.errors import HttpError

from gcp_utils import authenticate
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.base_io import ImCloudBase
from common.exceptions import ImCloudError

CLOUD_STORAGE_SCOPES = ['https://www.googleapis.com/auth/devstorage.read_write']


class CloudStorageError(ImCloudError):
    pass


class CloudStorage(ImCloudBase):
    def __init__(self,
                 project_id,
                 http=None,
                 packer=packer):
        """
        base class of cloud storage.
        :param project_id: google cloud platform's project id
        :type project_id: str
        :param http: http client module(optional)
        :return:
        """
        super(CloudStorage, self).__init__()

        credentials, http = authenticate(CLOUD_STORAGE_SCOPES, http)
        self._client = discovery.build('storage', 'v1', http=http, credentials=credentials)
        self._project_id = project_id
        self._packer = packer

    def bucket_info(self, bucket):
        resp = self._client.buckets().get(bucket=bucket).execute()
        self._logger.debug("%s, %s", type(resp), resp)
        return resp

    def list(self, bucket, max_results=50):
        """
        list contents under the bucket.
        see: https://cloud.google.com/storage/docs/json_api/v1/objects/list
        :param bucket: target bucket name.
        :return: {"items": [{...}]
        """
        try:
            field_to_return = 'nextPageToken, items(name, size, contentType, metadata(my-key))'
            req = self._client.objects().list(bucket=bucket,
                                              fields=field_to_return,
                                              maxResults=max_results)
            while req is not None:
                resp = req.execute()
                req = self._client.objects().list_next(req, resp)
            self._logger.debug("%s, %s", type(resp), resp)
            return resp
        except HttpError as e:
            self._logger.warning("%s", e, exc_info=True)
            raise CloudStorageError("Cloud Storage Error: %s" % e.message)

    def range_get(self, bucket, object_name, start, end):
        """
        call get API with range parameter.
        made from google's MediaIoBaseDownload class.
        :param bucket: bucket name
        :param object_name: object name
        :param start: starting bytes
        :param end: ending bytes.
        :return:
        """
        try:
            # get meta data
            metadata = self._client.objects().get(
                    bucket=bucket,
                    object=object_name,
                    fields='bucket, name, metadata(type)').execute()
            self._logger.debug("metadata: %s", metadata)

            req = self._client.objects().get_media(
                    bucket=bucket,
                    object=object_name)
            fh = io.BytesIO()

            progress = 0
            total_size = end - start + 1
            done = False
            uri = req.uri
            while not done:
                if end <= start + progress:
                    self._logger.error(
                            "content range is not correct. %s-%s",
                            start + progress, end)
                    break

                headers = {
                    'range': 'bytes=%d-%d' % (start + progress, end)
                }
                http = req.http
                for retry_num in range(2):
                    if retry_num > 0:
                        time.sleep(self._rand() * 2**retry_num)
                        self._logger.warning(
                            'Retry #%d for media download: GET %s, following status: %d',
                            retry_num, self._uri, resp.status)
                    resp, content = http.request(uri, headers=headers)
                    if resp.status < 500:
                        break

                if resp.status in [200, 206]:
                    if 'content-location' in resp and resp['content-location'] != uri:
                        uri = resp['content-location']
                    progress += len(content)
                    fh.write(content)

                    if progress == total_size:
                        done = True
                    self._logger.info("Downloading: %d%%", int(float(progress) / float(total_size) * 100))
                else:
                    raise HttpError(resp, content, uri=self._uri)

            tpe = metadata.get('metadata', {}).get('type', 'memory')
            if tpe == 'memory':
                result = packer.loads(fh.getvalue())
            elif tpe == 'file':
                result = fh.getvalue()
            else:
                result = fh.getvalue()
            self._logger.debug("%s, %s", type(result), result)
            return result
        except HttpError as e:
            self._logger.warning("%s", e, exc_info=True)
            raise CloudStorageError("Cloud Storage Error: %s" % e.message)

    def get(self, bucket, object_name):
        """
        call get api.
        see: https://cloud.google.com/storage/docs/json_api/v1/objects/get
        :param bucket: bucket name
        :param object_name: saved object name
        :return:
        """
        try:
            # get meta data
            metadata = self._client.objects().get(
                    bucket=bucket,
                    object=object_name,
                    fields='bucket, name, metadata(type)').execute()
            self._logger.debug("metadata: %s", metadata)

            req = self._client.objects().get_media(
                    bucket=bucket,
                    object=object_name)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req, chunksize=1024*1024)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    self._logger.info("Downloading: %d%%", int(status.progress() * 100))
            tpe = metadata.get('metadata', {}).get('type', 'memory')
            if tpe == 'memory':
                result = packer.loads(fh.getvalue())
            elif tpe == 'file':
                result = fh.getvalue()
            else:
                result = fh.getvalue()
            self._logger.debug("%s, %s", type(result), result)
            return result
        except HttpError as e:
            self._logger.warning("%s", e, exc_info=True)
            raise CloudStorageError("Cloud Storage Error: %s" % e.message)

    def insert(self, bucket, object_name, media_body, mimetype='application/octet_stream'):
        """
        call insert api.
        see: https://cloud.google.com/storage/docs/json_api/v1/objects/insert
        :param bucket:
        :param object_name:
        :param media_body:
        :param mimetype:
        :return:
        """
        try:
            body_type = media_body.get('type', None)
            if body_type == 'memory':
                media = MediaInMemoryUpload(
                        packer.dumps(media_body.get('data')),
                        mimetype=mimetype)
            elif body_type == 'file':
                media = MediaFileUpload(
                        media_body.get('path'),
                        mimetype=mimetype)
            else:
                raise CloudStorageError("input parameter is not valid. %s" % media_body)

            result = self._client.objects().insert(
                    bucket=bucket,
                    name=object_name,
                    body={'metadata': {'type': body_type}},
                    media_body=media).execute()
            self._logger.debug("%s", result)
            return result
        except HttpError as e:
            # api call error
            self._logger.warning("%s", e, exc_info=True)
            raise CloudStorageError("Cloud Storage Error: %s" % e.message)
        except IOError as e:
            # target file does not exist
            self._logger.warning("%s", e.message)
            return None

    def delete(self, bucket, object_name):
        """
        call detete api.
        see: https://cloud.google.com/storage/docs/json_api/v1/objects/delete
        :param bucket:
        :param object_name:
        :return:
        """
        try:
            result = self._client.objects().delete(
                    bucket=bucket,
                    object=object_name).execute()
            self._logger.debug("%s", result)
            return result
        except HttpError as e:
            self._logger.warning("%s", e)
            raise CloudStorageError("Cloud Storage Error: %s" % e.message)


class Bucket(ImCloudBase):
    def __init__(self, bucket, project_id):
        """
        create Cloud Storage bucket object.
        :param bucket: name of bucket in Google Cloud Storage
        :type bucket: str
        :param project_id: target project ID
        :type project_id: str
        :return:
        """
        super(Bucket, self).__init__()

        self._cs = CloudStorage(project_id=project_id)
        self._bucket = bucket

    def list(self, retry_count=0):
        """
        get file list stored in Cloud Storage.
        this function retry third times if necessary.
        :param retry_count: number of retrying(internal parameter)
        :return: contained object list.
                 [{'name': path in cloud storage,
                   'size': file size,
                   'contentType': content type,
                   'metadata': (optional)
        """
        try:
            return self._cs.list(self._bucket).get('items', [])
        except CloudStorageError as e:
            if retry_count < 3:
                time.sleep(retry_count)
                return self.list(retry_count+1)
            self._logger.warning("list failure. %s", e.message)
            return []

    def range_get(self, object_name, start_bytes, end_bytes, retry_count=0):
        try:
            return self._cs.range_get(self._bucket, object_name, start_bytes, end_bytes)
        except CloudStorageError as e:
            if retry_count < 3:
                time.sleep(retry_count)
                return self.range_get(object_name, start_bytes, end_bytes, retry_count+1)
            self._logger.warning("range_get failure. %s", e.message)
            raise

    def get(self, object_name, retry_count=0):
        """
        get data from cloud storage.
        :param object_name: target object name
        :param retry_count: count of retrying
        :return:
        """
        try:
            return self._cs.get(self._bucket, object_name)
        except CloudStorageError as e:
            if retry_count < 3:
                time.sleep(retry_count)
                return self.get(object_name, retry_count+1)
            self._logger.warning("get failure. %s", e.message)
            raise

    def put_data(self, object_name, data, retry_count=0):
        """
        put binary data to cloud storage.
        :param object_name: storing path in cloud storage
        :param data: the data
        :param retry_count: count of retrying
        :return:
        """
        try:
            return self._cs.insert(self._bucket,
                                   object_name,
                                   {"type": "memory",
                                    "data": data})
        except CloudStorageError as e:
            if retry_count < 3:
                time.sleep(retry_count)
                return self.put_data(object_name, data, retry_count+1)
            self._logger.warning("put_data failure. %s", e.message)
            raise

    def put_file(self, object_name, path, retry_count=0):
        """
        put file object to cloud storage.
        :param object_name: storing path in cloud storage
        :param path: local file path
        :param retry_count: count of retrying
        :return:
        """
        try:
            return self._cs.insert(self._bucket,
                                   object_name,
                                   {"type": "file",
                                    "path": path})
        except CloudStorageError as e:
            if retry_count < 3:
                time.sleep(retry_count)
                return self.put_file(object_name, path, retry_count+1)
            self._logger.warning("put_file failure. %s", e.message)
            raise

    def delete(self, object_name):
        """
        delete object from cloud storage.
        :param object_name: target object name
        :return:
        """
        try:
            return self._cs.delete(self._bucket, object_name)
        except Exception as e:
            self._logger.warning("delete failure. %s", e.message)
            return None


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(name)s:%(process)d:%(levelname)s:%(message)s:%(filename)s:%(lineno)d'

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    bk = Bucket('imcloud-vm')
    list_results = bk.list()
    print "%s, %s" % (type(list_results), list_results)

    bk = Bucket('imcloud-storage-test')
    result = bk.put_data('test1', 'test')
    print result
    result = bk.get('test1')
    print result

    result = bk.put_data('test/test1', {'test': 1})
    print result
    result = bk.get('test/test1')
    print result

    result = bk.put_file('test/test2', '/vagrant/nohup.out')
    print result
    result = bk.get('test/test2')
    result = bk.range_get('test/test2', 100, 150)
    print result
    result = bk.delete('test/test2')
    print result
    result = bk.put_file('test/test2', '/vagrant/nohup.out1')
    result = bk.delete('test/test2')
    print result
    result = bk.delete('test/')
