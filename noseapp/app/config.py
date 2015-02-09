# -*- coding: utf-8 -*-

import os
import imp
from importlib import import_module

from noseapp.datastructures import ModifyDict


def _load(obj):
    """
    Загружает конфигурацию из объекта
    """
    for atr in dir(obj):
        if not atr.startswith('_'):
            yield (atr, getattr(obj, atr))


class ConfigError(BaseException):
    pass


class Config(ModifyDict):
    """
    Класс отвечает за хранение и
    формирование конфигурации приложения
    """

    def init_nose_config(self, nose_config):
        """
        Инициализирует nose конфигурацию
        """
        self['nose'] = ModifyDict(
            _load(nose_config.options),
        )

    def from_module(self, module):
        """
        Спарсить конфигурацию из модуля
        """
        try:
            obj = import_module(module)
        except ImportError:
            raise ImportError('Config {} not found'.format(module))

        self.update(_load(obj))

        return self

    def from_py_file(self, file_path):
        """
        Загружает конфигурацию из python файла

        :param file_path: путь до файла
        """
        if not os.path.isfile(file_path):
            raise ConfigError('config file does not exist "{}"'.format(file_path))

        elif not file_path.endswith('.py'):
            raise ConfigError('config file is not python file')

        module = imp.new_module(file_path.rstrip('.py'))
        module.__file__ = file_path

        try:
            execfile(file_path, module.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load file "{}"'.format(e.strerror)
            raise

        self.update(_load(module))

        return self
