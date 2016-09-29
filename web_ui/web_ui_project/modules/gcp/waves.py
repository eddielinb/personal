# -*- coding: utf-8 -*-
import os
import sys
import gzip
import msgpack
import cStringIO as StringIO
from datetime import datetime
from threading import Thread
from Queue import Queue

from google_drive import GoogleDrive
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.validator import mac_is_valid
from common.validator import timestamp_is_valid
from common.utils import call_with_retry


class Waves(GoogleDrive):
    """
    Waves format
    {
        'data_type': 7,
        'version': 1,
        'mac': '1234567890abcdef,
        'time_zone': 'Asia/Tokyo',
        'timestamps': [...],
        'rssi': [...],
        'data': [
            ...
        ],
        'voltages': [...],
        'logs': {
            ...
        }
    }
    """
    def __init__(self, credentials_file, parent_id, compress_level=4):
        self._parent_id = parent_id
        self._compress_level = compress_level
        super(Waves, self).__init__(credentials_file)

    def _pack_and_compress(self, data):
        """
        Pack and compress the data
        :param data: A dict of waves format
        :return: Packed and compressed data
        """
        fobj = StringIO.StringIO()
        gzipobj = gzip.GzipFile(fileobj=fobj, mode="wb", compresslevel=self._compress_level)
        gzipobj.write(msgpack.dumps(data))
        gzipobj.close()

        fobj.seek(0, 0)
        res = fobj.read()
        fobj.close()

        return res

    def _decompress_and_unpack(self, data):
        """
        Decompress and unpack the data
        :param data: Packed and compressed data
        :return: A dict of waves format
        """
        gzipobj = gzip.GzipFile(fileobj=StringIO.StringIO(data))
        data = gzipobj.read()
        gzipobj.close()
        return msgpack.loads(data)

    def _get_filename(self, mac, dt):
        """
        Return a filename
        :param mac: MAC address
        :param dt: Datetime object
        :return: Filename
        """
        return "%s_%s.gz" % (dt.strftime("%Y%m%d%H"), mac.upper())

    def upload_waves(self, data, mac, ts, overwrite=True):
        """
        Upload packed and compressed waveforms to Google Drive
        :param data: A dict of waves format
        :param mac: MAC address
        :param ts: UNIX timestamp
        :param overwrite: Bool
        :return:
        """
        # validation
        if not isinstance(data, dict):
            raise Exception("Invalid data: %s" % data)
        mac_is_valid(mac)
        timestamp_is_valid(ts)

        dt = datetime.utcfromtimestamp(ts)
        fn = self._get_filename(mac, dt)
        compressed_data = self._pack_and_compress(data)

        # store the data under the parent_id without hierarchy
        self.upload_data(compressed_data, [], fn,
                         parent_id=self._parent_id, overwrite=overwrite)
        self._logger.info("stored:%s:%s:%s", mac, ts, len(compressed_data))

    def download_waves_parallel(self, mac, sts, ets, hourly=False):
        """
        Download from Google Drive in parallel,
        return a dict that contains waves data from sts to ets
        :param mac: MAC address
        :param sts:  UNIX start timestamp
        :param ets:  UNITX end timestamp
        :param hourly:  Do not truncate or append, return each hour separately
        :return: dict of unpacked waveforms
        """
        unpacked = {}
        # create queues to communicate with thread worker
        queue_task = Queue()
        queue_return = Queue()

        for number in range(8):
            worker = DownloadWorker(queue_task, queue_return, mac,
                                    self.credentials_file, self._parent_id)
            worker.daemon = True
            worker.start()

        file_sts = sts // 3600 * 3600
        file_ets = (ets-1) // 3600 * 3600  # ets=3600n should not get next file
        for ts in range(file_sts, file_ets + 3600, 3600):
            queue_task.put(ts)
            self._logger.info('Queueing timestamp %s', ts)
        queue_task.join()

        packed = queue_return.get()
        if packed is Exception:
            raise packed

        for queue_count in range(file_sts + 3600, file_ets + 3600, 3600):
            new_packed = queue_return.get()
            if new_packed is Exception:
                raise new_packed
            packed.update(new_packed)

        if hourly:
            waves_data = packed
        else:
            waves_data = self._merge_truncate(packed, mac,
                                              sts, ets,
                                              file_sts, file_ets)
        return waves_data

    def _merge_truncate(self, packed, mac, sts, ets, file_sts, file_ets):
        str_list = ["timestamps", "rssi", "voltages"]
        str_list_data = ["root_powers", "waves"]

        for ts in range(file_sts, file_ets + 3600, 3600):
            if ts == file_sts:
                unpacked = packed[ts]
                unpacked = self.wave_format_check(unpacked, mac, ts)
            else:
                temp = packed[ts]
                temp = self.wave_format_check(temp, mac, ts)
                for str_element in str_list:
                    unpacked[str_element].extend(temp[str_element])

                if len(unpacked["data"]) > len(temp["data"]):
                    for pending_channel in range(len(temp["data"]), len(unpacked["data"])):
                       temp["data"].append({"channel": pending_channel + 1})
                       temp["data"][pending_channel]["root_powers"] = [None] * 3600
                       temp["data"][pending_channel]["waves"] = [None] * 3600
                elif len(unpacked["data"]) < len(temp["data"]):
                    pending_length = len(unpacked["voltages"])
                    for pending_channel in range(len(unpacked["data"]), len(temp["data"])):
                        unpacked["data"].append({"channel": pending_channel + 1})
                        unpacked["data"][pending_channel]["root_powers"] = [None] * pending_length
                        unpacked["data"][pending_channel]["waves"] = [None] * pending_length
                for str_element in str_list_data:
                    for channel in range(len(unpacked["data"])):
                        unpacked["data"][channel][str_element].extend(temp["data"][channel][str_element])
                unpacked["logs"].update(temp["logs"])
        for str_element in str_list:
            unpacked[str_element] = unpacked[str_element][(sts-file_sts):(ets-file_sts)]
        for str_element in str_list_data:
            for channel in range(len(unpacked["data"])):
                unpacked["data"][channel][str_element] = unpacked["data"][channel][str_element][(sts-file_sts):(ets-file_sts)]
        for ts_second in range(file_sts, sts) + range(ets, file_ets + 3600):
            if ts_second in unpacked["logs"].keys():
                del unpacked["logs"][ts_second]

        return unpacked

    def download_waves(self, mac, ts):
        """
        Download from Google Drive and decompress, unpack waveforms
        :param mac: MAC address
        :param ts: UNIX timestamp
        :return:
        """
        dt = datetime.utcfromtimestamp(ts)
        fn = self._get_filename(mac, dt)

        if self._parent_id:
            fids = self.retrieve_all_files(fn, [], parent_ids=[self._parent_id])
        else:
            fids = self.retrieve_all_files(fn, [], parent_ids=[])
        unpacked = None
        if fids:
            data = self.download_file(fids[0]['id'])
            unpacked = self._decompress_and_unpack(data)
            self._logger.info("downloaded:%s:%s", mac, ts)

        return unpacked

    def wave_format_check(self, waves, mac, ts):
        if waves is None:
            waves = {
            'data_type': 7,
            'version': 1,
            'mac': mac,
            'time_zone': 'Asia/Tokyo',
            'timestamps': range(ts, ts + 3600),
            'data': [],
            'logs': {}
            }
        if "rssi" not in waves:
            waves["rssi"] = [None] * 3600
        if "voltages" not in waves:
            waves["voltages"] = [None] * 3600
        if not waves["data"]:
            waves["data"] = [None] * 4
            for count in range(4):
                waves["data"][count] = {"channel" : count + 1}
                waves["data"][count]["root_powers"] = [None] * 3600
                waves["data"][count]["waves"] = [None] * 3600
        return waves

class DownloadWorker(Thread):
    def __init__(self, queue_task, queue_return, mac, credentials_file, parent_id):
        Thread.__init__(self)
        self.queue_task = queue_task
        self.queue_return = queue_return
        self.mac = mac
        self.credentials_file = (credentials_file)
        self._parent_id = parent_id

    def run(self):
        """
        """
        ts = self.queue_task.get()
        try:
            data = call_with_retry(Waves(self.credentials_file, self._parent_id).download_waves,
                                   (self.mac, int(ts)), max_retry=10, retry_interval=10)
        except Exception as e:
            data = e
        finally:
            self.queue_return.put({ts: data})
            self.queue_task.task_done()


def main():
    import argparse

    from common.logger import setup_logger
    from common.utils import StopWatch

    # Samples
    #
    # Download waves
    # $ python waves.py download -m mac_address -t timestamp -p parent_id -c credentials_file
    #

    # args
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(help='sub-command help')

    # downlaod
    sp = subparsers.add_parser('download', help='download waves')
    sp.set_defaults(cmd='download')
    sp.add_argument('-m', '--mac_address',
                    required=True,
                    help="MAC address")
    sp.add_argument('-t', '--timestamp',
                    required=True,
                    help="Timestamp")
    sp.add_argument('-p', '--parent_id',
                    required=False,
                    default="root",
                    help="Parent ID")
    sp.add_argument('-c', '--credentials',
                    required=False,
                    default="credentials.json",
                    help="Credentials File")
    sp.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Make the operation more talkative")
    args = parser.parse_args()

    # logger
    setup_logger('Waves', '/tmp/waves.log', verbose=args.verbose)
    _sw = StopWatch()

    waves = Waves(args.credentials, args.parent_id)
    if args.cmd == 'download':
        _sw.start()
        res = waves.download_waves(args.mac_address,
                                   int(args.timestamp))
        _sw.stop()

        print "Elapsed sec: %s", _sw.elapsed_sec
        print res.keys()

if __name__ == '__main__':
    main()
