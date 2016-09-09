import os
import json
import time
import pycurl
import StringIO
# logging
import logging

from core import SignalHandler
from core import protocol_errors
from core import mac_is_valid
from struct import pack

class ProtocolEmulator():

    def __init__(self):
        self.server = {
            'ip': "127.0.0.1",
            'port': "8000"
        }
        self.logger = logging.getLogger(__name__)
        self._mac_upload = "0000000000000002"
        self._access_key = None
        self._manufacturer = "droogmic corp."
        self._model_number = "3"
        self._data_version = "0xFF"
        self._url = "{ip}:{port}".format(**self.server)

    def start(self):
        print
        self._activate() #1
        self._activate() #2
        self._activate() #3
        self._activate() #4
        self._info()     #5
        self._activate() #6
        self._info()     #7
        self._activate() #8
        self._info()     #9
        self._info()     #10
       # self._info()     #error message checking
        self._data()     #11
        self._activate() #12
        self._info()     #13
        self._data()     #14
        self._activate() #15
        self._info()     #16
        self._data()     #17
        self._data()     #18
        self._data()     #19
        self._data()     #21
        print("Done Emulation")

    def _activate(self):
        print "activate"
        url = "{ip}:{port}/meter/activate/".format(**self.server)
        self.logger.info("Send an activation request(%s)..." % url)

        sign = "boo"

        headparams = []
        auth = "imAuth %s:%s" % (self._mac_upload, sign)
        headparams.append(str('%s:%s' % ("Authorization", auth)))
        code, body = self._send_https_post_request(url,
                                                   headparams,
                                                   '',
                                                   timeout=30)

        try:
            body = json.loads(body)
            # print body
            if code == 200:
                self._access_key = body['access_key']
                return body['access_key']
            else:
                self.logger.error("%s: %s" % (body['code'], body['message']))
                if body['code'] == protocol_errors['SignatureDoesNotMatch']['code']:
                    print("self.adjust_time()")
                return None
        except ValueError as e:
            print("json.load {}".format(e))
        return None

    def _info(self):
        print "uploading info"
        # url.
        url = "{ip}:{port}/meter/info/".format(**self.server)
        self.logger.info("Send a Lavender info(%s)..." % url)

        # header.
        headparams = []
        auth = "imAuth %s:%s" % (self._mac_upload, self._access_key)
        headparams.append(str('%s:%s' % ("Authorization", auth)))

        # data.
        self._booted_at = int(time.time())
        data = {"fw_version": 1,
                "booted_at": int(time.time()) - 10}
        if self._manufacturer:
            data["manufacturer"] = self._manufacturer
            data["model_number"] = self._model_number

        data = 'data=' + json.dumps(data)

        # post.
        code, body = self._send_https_post_request(url, headparams, data)

        try:
            body = json.loads(body)
            if code == 200:
                if self._data_version == 0x04 or self._data_version == 0xFF:
                    self.logger.info("Response for info:")
                    self.logger.info("    i_channels: '%s'" % body["i_channels"])
                    self.logger.info("    v_channels: '%s'" % body["v_channels"])
                    self._upload_i_channels = body["i_channels"].split(",")
                    self._upload_v_channels = body["v_channels"].split(",")
                return True
            else:
                if body['code'] == protocol_errors['InvalidAccessKey']['code']:
                    self.logger.error("%s: %s" % (
                        body['code'], body['message']))
                    return False

                if body['code'] == protocol_errors['BadRequest']['code']:
                    self.adjust_time()
                    return False

                if body['code'] == protocol_errors['ConnectionError']['code']:
                    return False

                self.logger.error("%s: %s" % (body['code'], body['message']))
                raise Exception("Upload Info: Unknown Error")
        except ValueError as e:
            print("json.load {}".format(e))
        return None

    def _data(self):
        print "uploading_data"
        # url.
        url = "{}/meter/data/".format(self._url)
        self.logger.info("Send a upload data(%s)..." % url)

        # data.
        data = 1
        data = pack('>b', data)
        # header
        auth = "imAuth %s:%s" % (self._mac_upload, self._access_key)
        headparams = []
        headparams.append('%s:%s' % ("Authorization", auth))
        headparams.append('%s:%s' % ("Content-Type", "application/octet-stream"))

        # post
        try:
            _cur = time.time()
            code, body = self._send_https_post_request(url, headparams,
                                                       data, False)
            self.logger.info("RequestLog:%s:%s:%s" %
                             (self._mac_upload,
                              code,
                              time.time() - _cur))
        except Exception as e:
            raise
            self.logger.error("UploadData:%s:%s:%s" % (
                self._mac_upload, e, self.logger.exception(e)))
            return True

        if code == 200:
            # check server response.
            self.logger.info("RequestLog:%s" % body)
            body = json.loads(body)
            if body["request"] == "fw_update":
                if self._download_firmware(body["fw_version"],
                                           body["domain"],
                                           body["checksum"]):
                    self._fw_version = body["fw_version"]
                else:
                    return False
            elif body["request"] == "reboot":
                self.adjust_time()
                self._info()
            elif body["request"] == "interval_change":
                self._upload_interval = int(body["interval"])
                self.logger.info("upload_interval is now %s" % body["interval"])
            elif body["request"] == "loglevel_change":
                self.logger.info("loglevel is now %s" % body["loglevel"])

            return True
        else:
            try:
                body = json.loads(body)
            except Exception as e:
                self.logger.exception(e)
                raise Exception("Upload Data: json format error")

            if body['code'] == protocol_errors['InvalidAccessKey']['code']:
                self.logger.error("%s: %s" % (body['code'], body['message']))
                return False

            if body['code'] == protocol_errors['BadRequest']['code']:
                return False

            if body['code'] == protocol_errors['ConnectionError']['code']:
                return False

            self.logger.error("%s: %s" % (body['code'], body['message']))
            raise Exception("Upload Data: Unknown Error")

    def adjust_time(self):
        self.logger.info("Adjust time: start...")
        url = "http://%s" % self._url
        code, body = self._send_http_head_request(url, [])
        self.logger.info("Adjust time: %s" % code)

    def _send_https_post_request(self, url, headparams, data,
                                 multipart=False, timeout=20):

        """Sends HTTPS POST request.
        Args:
            url: URL
            headparams: Header parameters
            data: Data

        Return:
            [HTTP response code, body]
        """
        pc = pycurl.Curl()
        # pc.setopt(pycurl.VERBOSE, 1)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.HTTPHEADER, headparams)
        if multipart:
            pc.setopt(pycurl.HTTPPOST, data)
        else:
            pc.setopt(pycurl.POSTFIELDS, data)
        pc.setopt(pycurl.TIMEOUT, timeout)

        # 0 means do not check the server's cert.
        pc.setopt(pycurl.SSL_VERIFYPEER, 0)
        # 0 means succeeds regardless of what the CN in the certificate is
        pc.setopt(pycurl.SSL_VERIFYHOST, 0)

        response = StringIO.StringIO()
        pc.setopt(pycurl.WRITEFUNCTION, response.write)
        pc.perform()

        return pc.getinfo(pc.HTTP_CODE), response.getvalue()

    def _send_http_head_request(self, url, headparams, timeout=5):
        """
        Sends HTTP HEAD request.

        :param url: URL
        :param headparams: Header parameters
        :param timeout: Timeout
        :return: [HTTP response code, body]
        """
        # remove Expect: 100-continue from HTTP header.
        headparams.append("Expect:")
        pc = pycurl.Curl()
        # pc.setopt(pycurl.VERBOSE, 1)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.NOBODY, 1)
        pc.setopt(pycurl.TIMEOUT, timeout)
        pc.setopt(pycurl.HTTPHEADER, headparams)

        response = StringIO.StringIO()
        pc.setopt(pycurl.WRITEFUNCTION, response.write)
        pc.setopt(pycurl.HEADERFUNCTION, response.write)
        pc.perform()

        return pc.getinfo(pc.HTTP_CODE), response.getvalue()


def main():
    PE = ProtocolEmulator()
    PE.start()

if __name__ == '__main__':  # pragma: no cover
    main()
