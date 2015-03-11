# -*- coding: utf-8 -*-

import os
import sys
import logging
from argparse import ArgumentError

from noseapp.core import extensions
from noseapp.core import TestProgram
from noseapp.core import load_suites_from_path
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
    :type argv: list
    """
    argv = DEFAULT_ARGV + (argv or [])

    for arg in argv:
        if '--processes' in arg:
            raise ArgumentError(None, 'Option "--processes" is deprecated')
        if arg == '--ls':
            os.environ.setdefault('NOSE_NOCAPTURE', '1')

    return argv


class NoseApp(object):
    """
    Base app class
    """

    config_class = AppConfig
    program_class = TestProgram

    def __init__(self, config=None, plugins=None, argv=None):
        """
        :type config: str
        :type plugins: list
        :type argv: list
        """
        self.config = self.config_class()

        if config:
            if os.path.isfile(config):
                self.config.from_py_file(config)
            else:
                self.config.from_module(config)

        self._suites = []

        self.__test_program = self.program_class(
            app=self,
            exit=True,
            argv=prepare_argv(argv),
            addplugins=[p(self) for p in (DEFAULT_PLUGINS + (plugins or []))],
        )

    def initialize(self):
        """
        Callback for initialize application
        """
        raise NotImplementedError

    def before(self):
        """
        Call before run suites
        """
        pass

    def after(self):
        """
        Call after run suites
        """
        pass

    @staticmethod
    def shared_extension(name=None, cls=None, args=None, kwargs=None):
        """
        Shared extension to TestCase classes. Use require param in noseapp.Suite class.

        :param name: extension name. this is property name in case class.
        :type name: str
        :param cls: extension class
        :param args, kwargs: class init arguments
        :type args: tuple
        :type kwargs: dict
        """
        if cls is None:
            raise ValueError('cls param is required')

        if name is None and not hasattr(cls, 'name'):
            raise AttributeError(
                '"{}" does not have "name" attribute'.format(cls.__name__),
            )
        elif name is None:
            name = cls.name

        logger.debug('Shared extension "%s"', name)

        return extensions.set(name, cls, in_context=True, args=args, kwargs=kwargs)

    @staticmethod
    def shared_data(name, data):
        """
        Shared extension to TestCase classes.
        Data will be copied during installation.

        :param name: this is property name in case class
        :type name: str
        :param data: any object
        """
        logger.debug('Shared data "%s"', name)

        return extensions.set(name, data, in_context=False)

    @property
    def suites(self):
        return self._suites

    def register_suite(self, suite):
        """
        Add suite in application

        :type suite: app.suite.Suite
        """
        logger.debug('Register suite "%s"', suite.name)

        self._suites.append(suite)

    def register_suites(self, suite):
        """
        App suite list in application

        :type suite: list, tuple
        """
        for s in suite:
            self.register_suite(s)

    def load_suites(self, path):
        """
        Auto load suites. Path can be package or simple dir.

        :param path: dir path
        :type path: str
        """
        sys.path.append(path)
        suites = load_suites_from_path(path)
        self.register_suites(suites)

    def run(self):
        """
        Perform run suites
        """
        logger.debug('Run application')

        self.__test_program.perform()

    def __repr__(self):
        return '<NoseApp: {}>'.format(self.__class__.__name__)
