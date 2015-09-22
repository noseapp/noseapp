# -*- coding: utf-8 -*-

"""
Application is entry point to your test program.
You can configure and expand your program from application.
"""

import os
import sys
import logging
from contextlib import contextmanager

from noseapp.core import loader
from noseapp.core import extensions
from noseapp.core import TestProgram
from noseapp.app.context import AppContext
from noseapp.app.context import app_callback
from noseapp.app.context import merge_context
from noseapp.core.factory import ClassFactory
from noseapp.core.collector import CollectSuite
from noseapp.app.config import Config as AppConfig
from noseapp.core.constants import CONFIG_CHECKOUT_ENV
from noseapp.plugins.configure import AppConfigurePlugin


logger = logging.getLogger(__name__)


DEFAULT_PLUGINS = [
    AppConfigurePlugin(),
]

APP_CONFIG = os.getenv(CONFIG_CHECKOUT_ENV, None)


class NoseApp(object):
    """
    Base application class

    Simple example:
        app = NoseApp('my_app')
        app.load_suites('/path/to/suites')
        app.run()

    Application can be master and sub application:

        sub_app = NoseApp.as_sub_app('sub')
        master_app = NoseApp.as_master_app('master', sub_app)

        sub_app.load_suites('/path/to/suites')
        master_app.load_suites('/path/to/suites', merge_suites=True)

        master_app.run()
    """

    config_class = AppConfig
    program_class = TestProgram
    class_factory = ClassFactory
    collector_class = CollectSuite

    def __init__(self,
                 name,
                 argv=None,
                 exit=True,
                 config=None,
                 plugins=None,
                 context=None,
                 sub_apps=None,
                 suites_path=None,
                 is_sub_app=False):
        """
        :type name: str
        :type argv: list
        :type exit: bool
        :type config: str
        :type plugins: list or tuple
        :type context: noseapp.app.context.AppContext
        :type is_sub_app: bool
        :type sub_apps: list or tuple
        """
        if sub_apps and is_sub_app:
            raise RuntimeError(
                '"{}" can not be maser app. The application is sub app.'.format(self),
            )

        # Initialization config storage
        self.config = self.config_class.from_path(APP_CONFIG or config)

        # Application name. Must be str only.
        self.__name = name

        # Command line options. Will be set after test program initialization.
        self.__options = None

        # If app is sub app that's True else False
        self.__is_sub_app = is_sub_app

        # Sub application list
        self.__sub_apps = list(sub_apps or [])

        # Context will be inject to nose suite
        self.__context = context or AppContext()

        # Add callbacks to context
        self.__context.add_setup(lambda: self.setUp())
        self.__context.add_teardown(lambda: self.tearDown())

        # Saved support nose plugins and add supported self plugins.
        self.__context.plugins.extend(list(plugins or []))

        if self.is_master_app:
            # Default plugins for master app only
            self.__context.plugins.extend(DEFAULT_PLUGINS)
            # Merge context of sub applications
            merge_context(self,
                          merge_setup=True,
                          merge_suites=True,
                          merge_plugins=True,
                          merge_teardown=True)
            # Program object initialization. Will be run later.
            self.__test_program = self.program_class(self, argv=argv, exit=exit)

            # If we are having path to suites dir then make load suites
            if suites_path is not None:
                self.load_suites(suites_path)

    @classmethod
    def as_master_app(cls, name, *sub_apps, **kwargs):
        """
        Create application as master application
        """
        kwargs.update(is_sub_app=False)
        kwargs.setdefault('sub_apps', sub_apps)

        return cls(name, **kwargs)

    @classmethod
    def as_sub_app(cls, name, **kwargs):
        """
        Create application as sub application
        """
        kwargs.update(
            sub_apps=None,
            is_sub_app=True,
        )

        return cls(name, **kwargs)

    def setUpApp(self):
        """
        Callback for initialize application.
        Will be call after initialize instance.
        """
        pass

    def tearDownApp(self):
        """
        Callback for destruct application.
        Will be called after exit from test program.
        """
        pass

    def setUp(self):
        """
        Callback will be called before run application
        """
        pass

    def tearDown(self):
        """
        Callback will be called after run application
        """
        pass

    def addOptions(self, parser):
        """
        Add options to command line interface

        :type parser: optparse.OptionParser
        """
        pass

    @property
    def name(self):
        """
        Application name
        """
        return self.__name

    @property
    def options(self):
        """
        Command line options
        """
        if self.__options is None:
            raise RuntimeError(
                'Options not found. Working outside initialize callback.',
            )

        return self.__options

    @options.setter
    def options(self, options):
        assert isinstance(options, self.config_class),\
            'options is not instance of "{}"'.format(self.config_class.__name__)

        if self.is_master_app:
            for sub_app in self.__sub_apps:
                sub_app.options = options

        self.__options = options

    @property
    def context(self):
        """
        Application context instance

        :rtype: noseapp.app.context.AppContext
        """
        return self.__context

    @property
    def plugins(self):
        """
        Plugins list
        """
        return self.__context.plugins

    @property
    def is_sub_app(self):
        """
        Flag to definition: that's sub application?
        """
        return self.__is_sub_app

    @property
    def is_master_app(self):
        """
        Flag to definition: that's master application?
        """
        return not self.__is_sub_app

    @property
    def suites(self):
        """
        Suites list
        """
        return self.__context.suites

    @property
    def sub_apps(self):
        """
        Sub application list
        """
        return self.__sub_apps

    @property
    def status(self):
        """
        Status of application
        """
        return 'sub' if self.__is_sub_app else 'master'

    def add_before(self, func):
        """
        Add callback to setup
        """
        self.__context.add_setup(func)
        return func

    def add_after(self, func):
        """
        Add callback to teardown
        """
        self.__context.add_teardown(func)
        return func

    @staticmethod
    def shared_extension(name=None, cls=None, args=None, kwargs=None):
        """
        Shared extension to Suites and TestCases.
        Use require param on noseapp.suite.Suite class for connect.

        :param name: extension name
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

    def register_suite(self, suite, add_prefix=True):
        """
        Add suite in application

        :type suite: noseapp.suite.base.Suite
        """
        logger.debug('Register suite "%s"', suite.name)

        suite.mount_to_app(self)

    def register_suites(self, suites):
        """
        App suite list in application

        :type suites: iter
        """
        for suite in suites:
            self.register_suite(suite)

    def load_suites(self, path, recursive=True, merge_suites=False):
        """
        Auto load suites. Path can be package or simple dir.

        :param path: dir path
        :type path: str

        :param recursive: recursive load from path or load from simple dir
        :type recursive: bool

        :param merge_suites: merge suites from sub application
         to self context. For master application only.
        :type merge_suites: bool
        """
        if path not in sys.path:
            sys.path.append(path)

        if recursive:
            suites = loader.load_suites_from_path(path)
        else:
            suites = loader.load_suites_from_dir(path)

        self.register_suites(suites)

        if merge_suites:
            merge_context(self, merge_suites=True)

    def run(self):
        """
        To perform run suites
        """
        logger.debug('Run application %s', repr(self))

        if self.__is_sub_app:
            raise RuntimeError(
                'Application {} can not be run. Application is sub application.'.format(self),
            )

        @contextmanager
        def teardown_app():
            try:
                yield
            finally:
                app_callback(self, 'tearDownApp')

        with teardown_app():
            success = self.__test_program.run()

        return success

    def __repr__(self):
        return '<NoseApp({}): {}>'.format(
            self.status, self.__name,
        )
