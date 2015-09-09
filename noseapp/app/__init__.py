# -*- coding: utf-8 -*-

"""
Base application for your test program.

You must implementation initialize method on base your application class.
If you want add option to command line so use add_options method on base your application class.
When you have wish to run application, use noseapp-manage run command for that.
"""

import os
import sys
import logging
from argparse import ArgumentError

from noseapp.core import loader
from noseapp.core import extensions
from noseapp.core import TestProgram
from noseapp.plugins.base import AppPlugin
from noseapp.core.factory import ClassFactory
from noseapp.core.collector import CollectSuite
from noseapp.app.config import Config as AppConfig
from noseapp.plugins.configure import AppConfigurePlugin


logger = logging.getLogger(__name__)


DEFAULT_PLUGINS = [
    AppConfigurePlugin(),
]

APP_CONFIG = os.getenv('NOSEAPP_CONFIG', None)


def _prepare_argv(argv, plugins):
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

    def __init__(self,
                 argv=None,
                 exit=True,
                 config=None,
                 plugins=None,
                 context=None,
                 sub_apps=None,
                 is_sub_app=False):
        """
        :type argv: list
        :type exit: bool
        :type config: str
        :type plugins: list
        :type context: object
        :type is_sub_app: bool
        :type sub_apps: list or tuple
        """
        if sub_apps and is_sub_app:
            raise RuntimeError(
                '"{}" can not be maser app. it is sub app.'.format(self),
            )

        # Initialization config storage
        self.config = self.config_class.from_path(APP_CONFIG or config)

        # If app is sub app that's True else False
        self.__is_sub_app = is_sub_app

        # List suites. Suite will be here after register.
        self.__suites = []

        # Sub application list
        self.__sub_apps = list(sub_apps or [])

        # Command line options. Will be set after test program initialization.
        self.__options = None

        # Context will be inject to nose suite
        self.__context = context

        # Plugins of the application only.
        # Saved support nose plugins and add supported self plugins.
        self.__plugins = list(plugins or [])

        if not self.__is_sub_app:
            for sub_app in self.sub_apps:
                self.__suites.extend(sub_app.suites)
                self.__plugins.extend(sub_app.plugins)

            add_plugins = []

            for plugin in (DEFAULT_PLUGINS + (self.__plugins or [])):
                if isinstance(plugin, AppPlugin):
                    plugin.init_app(self)
                    add_plugins.append(plugin)
                else:
                    add_plugins.append(plugin)

            # Program object initialization. Will be run later.
            self.__test_program = self.program_class(
                app=self,
                exit=exit,
                addplugins=add_plugins,
                argv=_prepare_argv(argv, add_plugins),
            )

    @classmethod
    def as_master_app(cls, *sub_apps, **kwargs):
        """
        Create application as master application
        """
        kwargs.update(is_sub_app=False)
        kwargs.setdefault('sub_apps', sub_apps)

        return cls(**kwargs)

    @classmethod
    def as_sub_app(cls, **kwargs):
        """
        Create application as sub application
        """
        kwargs.update(is_sub_app=True)
        kwargs.update('sub_apps', None)

        return cls(**kwargs)

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

    def add_options(self, parser):
        """
        Add options to command line interface

        :type parser: optparse.OptionParser
        """
        pass

    @property
    def options(self):
        if self.__options is None:
            raise RuntimeError(
                'Options not found. Working outside initialize callback.',
            )

        return self.__options

    @options.setter
    def options(self, value):
        assert isinstance(value, self.config_class),\
            'options is not instance of "{}"'.format(self.config_class.__name__)

        self.__options = value

    @property
    def context(self):
        return self.__context

    @property
    def plugins(self):
        return self.__plugins

    @property
    def is_sub_app(self):
        return self.__is_sub_app

    @property
    def suites(self):
        return self.__suites

    @property
    def sub_apps(self):
        return self.__sub_apps

    @staticmethod
    def shared_extension(name=None, cls=None, args=None, kwargs=None):
        """
        Shared extension to TestCase classes.
        Use require param in noseapp.suite.Suite class for connect.

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

        :param name: this is property name of case class
        :type name: str
        :param data: any object
        """
        logger.debug('Shared data "%s"', name)

        return extensions.set(name, data, to_transport=False)

    def register_suite(self, suite):
        """
        Add suite in application

        :type suite: noseapp.suite.base.Suite
        """
        logger.debug('Register suite "%s"', suite.name)

        self.__suites.append(suite)

    def register_suites(self, suites):
        """
        App suite list in application

        :type suites: list, tuple
        """
        for suite in suites:
            self.register_suite(suite)

    def load_suites(self, path, recursive=True):
        """
        Auto load suites. Path can be package or simple dir.

        :param path: dir path
        :type path: str
        :param recursive: recursive load from path or load from simple dir
        :type recursive: bool
        """
        if path not in sys.path:
            sys.path.append(path)

        if recursive:
            suites = loader.load_suites_from_path(path)
        else:
            suites = loader.load_suites_from_dir(path)

        self.register_suites(suites)

    def run(self):
        """
        Perform run suites
        """
        logger.debug('Run application')

        if self.__is_sub_app:
            raise RuntimeError('Application can not be run. App is sub application.')
        else:
            self.__test_program.perform()

    def __repr__(self):
        return '<NoseApp: {}>'.format(self.__class__.__name__)
