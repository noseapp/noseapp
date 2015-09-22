# -*- coding: utf-8 -*-

import os
import imp
import logging
from importlib import import_module

from noseapp.datastructures import ModifyDict


logger = logging.getLogger(__name__)


def load(obj):
    for atr in dir(obj):
        if not atr.startswith('_'):
            yield (atr, getattr(obj, atr))


class ConfigError(BaseException):
    pass


class Config(ModifyDict):
    """
    App config storage
    """

    @classmethod
    def from_path(cls, path=None):
        """
        Create instance and try to parse config by path

        :param path: import path or file path
        :type path: str

        :rtype: Config
        """
        config = cls()

        def is_import_path(path):
            is_dot_in_path = '.' in path
            is_py_ex = path.endswith('.py')

            return is_dot_in_path and not is_py_ex

        if path:
            if is_import_path(path):
                config.from_module(path)
            else:
                config.from_py_file(path)

        return config

    def from_module(self, module):
        """
        Init configuration from python module

        :param module: import path
        :type module: str
        """
        logger.debug('Init config from module "%s"', module)

        try:
            obj = import_module(module)
        except ImportError:
            raise ImportError('Config {} not found'.format(module))

        self.update(load(obj))

        return self

    def from_py_file(self, file_path):
        """
        Init configuration from py file

        :param file_path: absolute file path
        :type file_path: str
        """
        logger.debug('Init config from py file "%s"', file_path)

        if not os.path.isfile(file_path):
            raise ConfigError('config file does not exist at path "{}"'.format(file_path))

        elif not file_path.endswith('.py'):
            raise ConfigError('config file is not python file')

        module = imp.new_module(file_path.rstrip('.py'))
        module.__file__ = file_path

        try:
            execfile(file_path, module.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load file "{}"'.format(e.strerror)
            raise

        self.update(load(module))

        return self
