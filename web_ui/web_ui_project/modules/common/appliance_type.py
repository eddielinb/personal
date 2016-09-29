#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import ujson as json

from base_io import ImCloudBase


class ApplianceType(ImCloudBase):
    cdir = os.path.abspath(os.path.dirname(__file__))
    APPLIANCE_TYPE_FILE = os.path.join(cdir, "files/appliance_type.json")

    @classmethod
    def _read_appliance_type(cls):
        """
        Read an appliance type file
        :return: A dict of appliance type
            {
                1: {
                    "name": "Air Cleaner",
                    "type": 1
                },
                2: {
                    "name": "Air Conditioner",
                    "type": 1
                }
                ...
            }
        """
        fp = open(cls.APPLIANCE_TYPE_FILE, 'r')
        data = json.loads(fp.read())
        fp.close()
        return {int(k): v for k, v in data.items()}

    @classmethod
    def get_all_appliance_types(cls):
        """

        :return: A dict of appliance type
            {
                1: {
                    "name": "Air Cleaner",
                    "type": 1
                },
                2: {
                    "name": "Air Conditioner",
                    "type": 1
                }
                ...
            }
        """
        return cls._read_appliance_type()
