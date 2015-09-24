# -*- coding: utf8 -*-

import os
import sys
from argparse import ArgumentError

from nose.proxy import ResultProxyFactory
from nose.core import TestProgram as BaseTestProgram

from noseapp.core import collector
from noseapp.core import extensions
from noseapp.app.context import app_callback


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


class ProgramData(object):
    """
    Class is merging data of test program and application
    """

    def __init__(self, program, app, argv=None):
        from noseapp.app import config

        # Push options from parser to application
        app.options = app.config_class(
            config.load(program.config.options),
        )
        # Init application is here
        app_callback(app, 'setUpApp')

        self.__argv = argv or sys.argv
        self.__class_factory = app.class_factory(program.config.options)

        self.__app = app
        self.__program = program

        self.__result_proxy_factory = ResultProxyFactory(
            config=self.__program.config,
        )

    @property
    def argv(self):
        return self.__argv

    @property
    def suites(self):
        return self.__app.suites

    @property
    def config(self):
        return self.__program.config

    @property
    def context(self):
        return self.__app.context

    @property
    def suite_class(self):
        return self.__class_factory.suite_class

    @property
    def runner_class(self):
        return self.__class_factory.runner_class

    @property
    def result_proxy_factory(self):
        return self.__result_proxy_factory

    def build_suite(self):
        """
        Collect and build suites
        """
        with extensions.installation():
            suites = collector.collect(
                self,
                collector_class=self.__app.collector_class,
            )

        return suites


class TestProgram(BaseTestProgram):

    def __init__(self, app, argv=None, exit=True):
        argv = prepare_argv(argv, app.plugins)

        super(TestProgram, self).__init__(
            argv=argv,
            exit=exit,
            addplugins=app.plugins,
        )

        self.testLoader = None  # We are not using that
        self.data = ProgramData(self, app, argv=argv)

    # disarm base class
    def createTests(self):
        pass

    def runTests(self):
        pass

    def run(self):
        """
        Perform test program
        """
        self.testRunner = self.data.runner_class(
            stream=self.config.stream,
            verbosity=self.config.verbosity,
            config=self.config,
        )

        plug_runner = self.config.plugins.prepareTestRunner(self.testRunner)

        if plug_runner is not None:
            self.testRunner = plug_runner

        suites = self.data.build_suite()

        if not suites:
            raise RuntimeError('No suites for running')

        result = self.testRunner.run(suites)
        self.success = result.wasSuccessful()

        if self.exit:
            sys.exit(not self.success)

        return self.success
