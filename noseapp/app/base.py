# -*- coding: utf-8 -*-

"""
Application is entry point to your test program.
You can configure and expand your program from application.
"""

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
from noseapp.app.config import get_config_path_by_env
from noseapp.core.constants import CONFIG_CHECKOUT_ENV
from noseapp.plugins.configure import AppConfigurePlugin


logger = logging.getLogger(__name__)


DEFAULT_PLUGINS = [
    AppConfigurePlugin(),
]


class NoseApp(object):
    """
    Base application class

    Usage:

        >>> app = NoseApp('my_app')
        >>> app.load_suites('/path/to/suites')
        >>> app.run()

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
        :param name: application name.
        application name is prefix to suite name.
         namespace pattern: <application_name>.<suite_name>:<test_case_name>

        for example:

            >>> from noseapp import Suite

            >>> app = NoseApp('my_app')
            >>> suite = Suite('my_suite')
            >>> suite.name
            >>> 'my_suite'

            >>> app.register_suite(suite)
            >>> suite.name
            >>> 'my_app.my_suite'

        :type name: str

        :param argv: argv to sys.argv
        :type argv: list

        :param exit: do exit after run?
        :type exit: bool

        :param config: import path or absolute file path
        for example:
            * config='project.etc.config'
            * config='/home/user/project/etc/config.py'
        :type config: str

        :param plugins: plugins instances
        :type plugins: list or tuple

        :param context: inctance of AppContext.
         you can create own context instance to run.
        :type context: noseapp.app.context.AppContext

        :param suites_path: path to directory where contains suites
        :type suites_path: str

        :param is_sub_app: is application a sub application?
        :type is_sub_app: bool

        :param sub_apps: sub application instances. for master application only.
        :type sub_apps: list or tuple
        """
        if sub_apps and is_sub_app:
            raise RuntimeError(
                '"{}" can not be maser app. The application is sub app.'.format(self),
            )

        # Initialization config storage
        self.config = self.config_class.from_path(
            get_config_path_by_env(CONFIG_CHECKOUT_ENV, config),
        )

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

            # If we are having path to suites then make load suites
            if suites_path is not None:
                self.load_suites(suites_path)

    @classmethod
    def as_master_app(cls, name, *sub_apps, **kwargs):
        """
        Alternative constructor.
        Create application as master application.

        Example::

            sub_app = NoseApp.as_sub_app('my_sub_app')
            app = NoseApp.as_master_app('my_app', sub_app, config='etc.config')

            sub_app.load_suites('/path/to/suites')
            app.load_suites('/path/to/suites', merge_suites=True)
        """
        kwargs.update(is_sub_app=False)
        kwargs.setdefault('sub_apps', sub_apps)

        return cls(name, **kwargs)

    @classmethod
    def as_sub_app(cls, name, **kwargs):
        """
        Alternative constructor.
        Create application as sub application. See as_master_app.
        """
        kwargs.update(
            sub_apps=None,
            is_sub_app=True,
        )

        return cls(name, **kwargs)

    def setUpApp(self):
        """
        For setup extensions end prepare program.
        Will be called after creating instance.
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
        Do it something before run suites.
        Callback will be called before run application.
        """
        pass

    def tearDown(self):
        """
        Do it something after run suites.
        Callback will be called after run application
        """
        pass

    def addOptions(self, parser):
        """
        Add options to command line interface.

        Example::

            from optparse import OptionGroup


            class MyApp(NoseApp):

                def addOptions(parser):
                    group = OptionGroup(parser, 'My Application options')

                    group.add_option(
                        '--project-url',
                        dest='project_url',
                        default=None,
                        help='Web URL',
                    )

                    parser.add_option_group(group)

        :param parser: options parser
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
        Command line options. Will be available after create instance.

        :raises: RuntimeError
        """
        if self.__options is None:
            raise RuntimeError(
                'Options not found. Working outside app context.',
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
        Context of application instance

        :rtype: noseapp.app.context.AppContext
        """
        return self.__context

    @property
    def plugins(self):
        """
        Plugins storage of context

        :rtype: list
        """
        return self.__context.plugins

    @property
    def is_sub_app(self):
        """
        Flag to definition: is it sub application?

        :rtype: bool
        """
        return self.__is_sub_app

    @property
    def is_master_app(self):
        """
        Flag to definition: is it master application?

        :rtype: bool
        """
        return not self.__is_sub_app

    @property
    def suites(self):
        """
        Suites storage of context

        :rtype: list
        """
        return self.__context.suites

    @property
    def sub_apps(self):
        """
        Sub application storage

        :rtype: list
        """
        return self.__sub_apps

    @property
    def status(self):
        """
        Status of application.

        Example::

            >>> app = NoseApp.as_master_app('my_app')
            >>> app.status
            >>> 'master'

            >>> app = NoseApp.as_sub_app('my_app')
            >>> app.status
            >>> 'sub'
        """
        return 'sub' if self.__is_sub_app else 'master'

    def add_setup(self, func):
        """
        Add setup callback to context.

        Example::

            app = NoseApp('my_app')

            @app.add_setup
            def setup():
                # do something
                pass

            # or

            app.add_setup(lambda: None)

        """
        self.__context.add_setup(func)
        return func

    def add_teardown(self, func):
        """
        Add teardown callback to context.

        Example::

            app = NoseApp('my_app')

            @app.add_teardown
            def teardown():
                # do something
                pass

            # or

            app.add_teardown(lambda: None)
        """
        self.__context.add_teardown(func)
        return func

    @staticmethod
    def shared_extension(name=None, cls=None, args=None, kwargs=None):
        """
        Shared extension to Suite and TestCase instances.
        Use require param on noseapp.Suite class for connect.

        Example::

            import random

            app = NoseApp('my_app')
            app.shared_extension(name='random_int', cls=random.randint, args=(0, 100))

        :param name: extension name
        :type name: str

        :param cls: extension class or callable object
        :type cls: object, callable

        :param args: cls init args
        :type args: tuple

        :param kwargs: cls init kwargs
        :type kwargs: dict

        :raises: ValueError, AttributeError
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
        Shared data to Suite and TestCase instances.
        Data will be copied during installation.

        Example::

            data = {
                'a': 1,
                'b': 2,
                'c': 3,
            }
            app = NoseApp('my_app')
            add.shared_data('data', data)

        :param name: extension name
        :type name: str

        :param data: any object
        """
        logger.debug('Shared data "%s"', name)

        return extensions.set(name, data, to_transport=False)

    def register_suite(self, suite):
        """
        Add suite to application

        :type suite: noseapp.suite.base.Suite
        """
        logger.debug('Register suite "%s"', suite.name)

        suite.mount_to_app(self)

    def register_suites(self, suites):
        """
        App suite list to application

        :type suites: iter
        """
        for suite in suites:
            self.register_suite(suite)

    def load_suites(self, path, recursive=True, merge_suites=False):
        """
        Auto load suites. Path can be package or simple dir.

        :param path: path to suites dir
        :type path: str

        :param recursive: recursive load from path or load from simple dir
        :type recursive: bool

        :param merge_suites: merge suites from sub application
         to self context. for master application only.
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

    def show_tree(self, show_docs=False, doc_lines=1):
        """
        Show tree of suites.

        :param show_docs: print or not print docs
        :type show_docs: bool

        :param doc_lines: number lines of doc
        :type doc_lines: int
        """
        from noseapp.tools import output

        output.tree(self.suites, show_docs=show_docs, doc_lines=doc_lines, exit=False)

    def run(self):
        """
        To perform run suites.
        If was success after run and not exit param is False then return True.

        Make run from command line::

            noseapp-manage run project.app:create_app

        :rtype: bool
        :raises: RuntimeError
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
