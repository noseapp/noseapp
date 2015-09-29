# -*- coding: utf-8 -*-

import os
import imp
import logging
from importlib import import_module

from noseapp.datastructures import ModifyDict


logger = logging.getLogger(__name__)


def get_config_path_by_env(env_name, default=None, base_path=None):
    """
    To set config by env name.

    >>> config_path = get_config_path_by_env('MY_CONFIG', 'base', base_path='project.etc.')

    :param env_name: environment name
    :type env_name: str

    :param base_path: base path
    :type base_path: str

    :param default: default value
    :type default: str

    :rtype: str
    """
    config_path = os.getenv(env_name, default)

    if base_path and config_path:
        config_path = '{}{}'.format(base_path, config_path)

    return config_path


def load(obj):
    """
    Load attributes from object

    :param obj: object to load

    :return: generator
    """
    for atr in dir(obj):
        if not atr.startswith('_'):
            yield (atr, getattr(obj, atr))


class ConfigError(BaseException):
    pass


class Config(ModifyDict):
    """
    App config storage

    Usage:

        >>> config = Config()
        >>> config.from_module('etc.base')
        >>> # or config.from_py_file('/home/user/project/etc/base.py')
        >>> config.DEBUG
        >>> False
        >>> ...
    """

    @classmethod
    def from_path(cls, path=None):
        """
        Alternative constructor.
        Create instance and try to parse config by path.

        Example:

            >>> config = Config.from_path('etc.base')

        :param path: import path or file path
        :type path: str, None

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
            elif path.endswith('.py'):
                config.from_py_file(path)

        return config

    def from_module(self, module):
        """
        Init configuration from python module

        :param module: import path
        :type module: str

        :raises: ImportError
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

        :raises: ConfigError, IOError
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
