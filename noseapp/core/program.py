# -*- coding: utf8 -*-

import sys

from nose.core import TestProgram as BaseTestProgram

from noseapp.app import config
from noseapp.core import extensions


class ProgramData(object):
    """
    Merging data of test program and application
    """

    def __init__(self, program, app, argv=None):
        # Push options from parser to application
        app.options = app.config_class(
            config.load(program.config.options),
        )

        # Initialize application
        app.initialize()

        self.__argv = argv or sys.argv
        self.__class_factory = app.class_factory(program.config.options)

        self.__app = app
        self.__program = program

    @property
    def argv(self):
        return self.__argv

    @property
    def suites(self):
        return self.__app.suites

    @property
    def test_loader(self):
        return self.__program.testLoader

    @property
    def config(self):
        return self.__program.config

    @property
    def suite_class(self):
        return self.__class_factory.suite_class

    @property
    def runner_class(self):
        return self.__class_factory.runner_class

    def before_run_callback(self):
        self.__app.before()

    def after_run_callback(self):
        self.__app.after()

    def build_suites(self):
        """
        Collect and build suites
        """
        collector = self.__app.collector_class(self)
        suites = collector.make_result()
        extensions.clear()
        return suites


class TestProgram(BaseTestProgram):

    def __init__(self, *args, **kwargs):
        app = kwargs.pop('app')

        super(TestProgram, self).__init__(*args, **kwargs)

        self.data = ProgramData(
            self, app,
            argv=kwargs.get('argv', None),
        )

    # disarm base class
    def createTests(self):
        pass

    def runTests(self):
        pass

    def perform(self):
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

        self.data.before_run_callback()

        result = self.testRunner.run(self.data.build_suites())
        self.success = result.wasSuccessful()

        self.data.after_run_callback()

        if self.exit:
            sys.exit(not self.success)

        return self.success
