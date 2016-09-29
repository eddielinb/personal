#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta
import os
import logging


class Dumber:
    __metaclass__ = ABCMeta

    @abstractmethod
    def dump(self, path, data, **kwargs):
        pass


class ImCloudBase(object):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)


class Loader:
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, *path, **kwargs):
        pass

    @abstractmethod
    def list_files(self, path, **kwargs):
        pass


class LocalStorageService(Dumber, Loader):
    """
    Local storage loader and dumper implementation class.
    """
    def __init__(self, mode="b", overwrite=True):
        # TODO: validation mode
        if overwrite:
            self._overwrite = ''
        else:
            self._overwrite = "x"
        self._mode = mode

    def dump(self, path, data, **kwargs):
        with open(path, 'w%s%s' % (self._mode, self._overwrite)) as f:
            f.write(data)

    def load(self, *path, **kwargs):
        def read_all_data(p):
            with open(p, 'r%s' % self._mode) as f:
                return f.read()

        return map(read_all_data, path)

    def list_files(self, path):
        return [f for f in os.listdir(path) if os.path.isfile(f)]
