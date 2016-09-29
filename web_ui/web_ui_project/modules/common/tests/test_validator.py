import unittest
import time

from validator import *

_meter_id = "1234567812345678"
_timestamp = int(time.time())


class ValidatorTest(unittest.TestCase):
    # ------------------------------------------------------
    # validate_mac_address
    # ------------------------------------------------------
    def test_validate_mac_address(self):
        mac_is_valid(_meter_id)

    def test_validate_mac_address_with_mac_address(self):
        illegal_macs = [
            # None
            None
            # empty
            , ""
            # short
            , "0" * 15
            # long
            , "0" * 17
            # invalid
            , "000000000000000G"
            # int
            , 1111111111111111
            # zero
            , 0
            # -1
            , -1
            # float
            , 1.0
        ]
        for mac in illegal_macs:
            self.assertRaises(InvalidParameterError, mac_is_valid, mac)
        # valid
        self.assertTrue(mac_is_valid("0" * 16))

    # ------------------------------------------------------
    # validate_timestamp
    # ------------------------------------------------------
    def test_validate_timestamp(self):
        valid_timestamps = [
            _timestamp
            # max
            , 2 ** 32 - 1
            # zero
            , 0
        ]
        for ts in valid_timestamps:
            self.assertTrue(timestamp_is_valid, ts)

    def test_validate_timestamp_with_timestamp(self):
        illegal_timestamps = [
            # None
            None
            # empty
            , ""
            # large
            , 2 ** 32
            # -1
            , -1
            # float
            , float(_timestamp)
            # char
            , "%s" % _timestamp
        ]
        for ts in illegal_timestamps:
            self.assertRaises(InvalidParameterError,
                              timestamp_is_valid,
                              ts)
