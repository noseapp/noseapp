# -*- coding: utf-8 -*-

"""
Base application for your test program.

You must implementation initialize method on base your application class.
Use add_options method for add option to command line interface.
Use noseapp-manage run command for running your application.
"""

import os
import sys
import logging
from argparse import ArgumentError

from optparse import OptionParser

from noseapp.core import extensions
from noseapp.core import TestProgram
from noseapp.plugins.base import AppPlugin
from noseapp.core.factory import ClassFactory
from noseapp.core import load_suites_from_path
from noseapp.core.collector import CollectSuite
from noseapp.app.config import Config as AppConfig
from noseapp.plugins.configure import AppConfigurePlugin
from noseapp.core.loader import load_from_dir as load_suites_from_dir


logger = logging.getLogger(__name__)


DEFAULT_PLUGINS = [
    AppConfigurePlugin(),
]


def prepare_argv(argv, plugins):
    """
    :type argv: list
    """
    argv = sys.argv + (argv or [])

    for arg in argv:
        if '--processes' in arg:
            raise ArgumentError(None, 'Option "--processes" is deprecated')
        if arg == '--ls':
            os.environ.setdefault('NOSE_NOCAPTURE', '1')

    argv.extend(('--with-{}'.format(p.name) for p in plugins))

    return argv


class NoseApp(object):
    """
    Base app class
    """

    config_class = AppConfig
    program_class = TestProgram
    class_factory = ClassFactory
    collector_class = CollectSuite

    def __init__(self, config=None, plugins=None, argv=None):
        """
        :type config: str
        :type plugins: list
        :type argv: list
        """
        # Initialization config storage
        self.config = self.config_class()

        if config:  # Parse config module. You can do it later.
            if os.path.isfile(config):
                self.config.from_py_file(config)
            else:
                self.config.from_module(config)

        # List suites. After register suite will be here.
        self._suites = []

        # Options parser. Will be set after test program initialization.
        self.__parser = None
        # Command line options. Will be set after test program initialization.
        self.__options = None

        # Init plugins. Saving support nose plugins and add supporting self plugins.
        add_plugins = []

        for plugin in (DEFAULT_PLUGINS + (plugins or [])):
            if isinstance(plugin, AppPlugin):
                add_plugins.append(plugin(self))
            else:
                add_plugins.append(plugin)

        # Program object initialization. Will be run later.
        self.__test_program = self.program_class(
            app=self,
            exit=True,
            argv=prepare_argv(argv, add_plugins),
            addplugins=add_plugins,
        )

    @property
    def parser(self):
        if self.__parser is None:
            raise RuntimeError(
                'Parser not found. Maybe you ignored noseapp.plugins.configure.AppConfigurePlugin?',
            )

        return self.__parser

    @parser.setter
    def parser(self, value):
        assert isinstance(value, OptionParser), \
            'parser is not instance of "optparse.OptionParser"'

        self.__parser = value

    @property
    def options(self):
        if self.__options is None:
            raise RuntimeError('Options not found. Working outside initialize callback.')

        return self.__options

    @options.setter
    def options(self, value):
        assert isinstance(value, self.config_class),\
            'options is not instance of "{}"'.format(self.config_class.__name__)

        self.__options = value

    def initialize(self):
        """
        Callback for initialize application
        """
        raise NotImplementedError(
            'Initialize method is not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

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

    def add_options(self):
        """
        Add options to command line interface.

        Usage ::

            def add_options(self):
                self.parser.add_option(
                    '--project-url',
                    dest='project_url',
                    default='http://my-site.com',
                    help='Project URL',
                )
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

        return extensions.set(name, cls, to_transport=True, args=args, kwargs=kwargs)

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

        return extensions.set(name, data, to_transport=False)

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

    def load_suites(self, path, recursive=True):
        """
        Auto load suites. Path can be package or simple dir.

        :param path: dir path
        :type path: str
        :param recursive: recursive load from path or load from simple dir
        :type recursive: bool
        """
        sys.path.append(path)

        if recursive:
            suites = load_suites_from_path(path)
        else:
            suites = load_suites_from_dir(path)

        self.register_suites(suites)

    def run(self):
        """
        Perform run suites
        """
        logger.debug('Run application')

        self.__test_program.perform()

    def __repr__(self):
        return '<NoseApp: {}>'.format(self.__class__.__name__)
