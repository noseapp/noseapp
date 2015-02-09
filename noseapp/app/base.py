# -*- coding: utf-8 -*-

import os
import sys
import logging
from argparse import ArgumentError

from noseapp.app import extensions
from noseapp.suite.loader import AutoLoad
from noseapp.app.program import TestProgram
from noseapp.app.config import Config as AppConfig
from noseapp.plugins.configure import AppConfigurePlugin


logger = logging.getLogger(__name__)


DEFAULT_PLUGINS = [
    AppConfigurePlugin(),
]

DEFAULT_ARGV = sys.argv + [
    '--with-app-configure',
]


def prepare_argv(argv):
    """
    Подготавливает аргументы командной
    строки перед инициализацией в TestProgram
    """
    argv = DEFAULT_ARGV + (argv or [])

    for arg in argv:
        if '--processes' in arg:  # не поддерживаем параллельный запуск через nose plugin
            raise ArgumentError(None, 'Option "--processes" is deprecated')
        if arg == '--ls':  # если нужно показать дерево suites,
            # то без дефолта NOSE_NOCAPTURE это будет невозможно
            os.environ.setdefault('NOSE_NOCAPTURE', '1')

    return argv


class NoseApp(object):
    """
    Базовый класс приложения
    """

    config_class = AppConfig
    program_class = TestProgram

    def __init__(self, config=None, plugins=None, argv=None):
        """
        :param config: установка конфигурации (строка для импорта или путь до файла)
        :param plugins: плагины котрые необходимо передать в nose.app.program.TestProgram
        :param argv: аргументы командной строки
        """
        self.config = self.config_class()

        if config:
            if os.path.isfile(config):
                self.config.from_py_file(config)
            else:
                self.config.from_module(config)

        self._suite = []

        self.__test_program = self.program_class(
            app=self,
            argv=prepare_argv(argv),
            addplugins=[p(self) for p in (DEFAULT_PLUGINS + (plugins or []))],
        )

    def initialize(self):
        """
        Инициализатор вашего приложения
        """
        logger.warning(
            'initialize method of class {} is not implemented'.format(self.__class__.__name__),
        )

    def before(self):
        """
        Callback вызывается перед прогоном
        """
        pass

    def after(self):
        """
        Callback вызывается после прогона
        """
        pass

    def shared_extension(self, name=None, cls=None, args=None, kwargs=None):
        """
        Расшарить расширение. Расшинение можно будет подключить
        с помощью параметра require в noseapp.suite.Suite

        :param name: имя расшинения
        :param cls: класс который нужно расшарить
        :param args, kwargs: аргументы которые нужно передать классу при инициализации
        """
        if cls is None:
            raise ValueError('cls param is required')

        if name is None and not hasattr(cls, 'name'):
            raise AttributeError(
                '"{}" does not have "name" attribute'.format(cls.__name__),
            )
        elif name is None:
            name = cls.name

        return extensions.set(name, cls, in_context=True, args=args, kwargs=kwargs)

    def shared_data(self, name, data):
        """
        Расшарить данные. Данные будут расшарены между TestCase.
        Важно понимать, что изменения сделанные в одном TestCase никогда
        не будут видны в другом.

        :param name: имя(ключ расширения)
        :param data: объект с данными
        """
        return extensions.set(name, data, in_context=False)

    def register_suite(self, suite):
        """
        Регистрирует suite в приложении

        :type suite: app.suite.Suite
        """
        self._suite.append(suite)

    def register_suites(self, suite):
        """
        Регистрирует список suite

        :type suite: list, tuple
        """
        for s in suite:
            self.register_suite(s)

    def load_suites(self, path):
        """
        Загружает suites по указанному пути

        :param path: путь до дирректории
        """
        loader = AutoLoad(path)
        self.register_suites(
            loader.get_result(),
        )

    def run(self):
        """
        Запускает приложение
        """
        self.__test_program.perform()

    def __repr__(self):
        return '<NoseApp: {}>'.format(self.__class__.__name__)
