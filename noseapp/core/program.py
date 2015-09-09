# -*- coding: utf8 -*-

import sys

from noseapp.core.provider import FromNoseToApp
from nose.core import TestProgram as BaseTestProgram


class ProgramData(object):
    """
    Class is merging data of test program and application
    """

    def __init__(self, program, app, argv=None):
        # Init application is here
        FromNoseToApp(app).initialize(program.config.options)

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
    def config(self):
        return self.__program.config

    @property
    def suite_class(self):
        return self.__class_factory.suite_class

    @property
    def runner_class(self):
        return self.__class_factory.runner_class

    def before_run_callback(self):
        FromNoseToApp(self.__app).before()

    def after_run_callback(self):
        FromNoseToApp(self.__app).after()

    def build_suite(self):
        """
        Collect and build suites
        """
        from noseapp.core import collector
        from noseapp.core import extensions

        suites = collector.collect(
            self,
            collector_class=self.__app.collector_class,
        )

        extensions.clear()

        return self.suite_class(
            suites,
            config=self.config,
            context=self.__app.context,
        )


class TestProgram(BaseTestProgram):

    def __init__(self, *args, **kwargs):
        app = kwargs.pop('app')

        super(TestProgram, self).__init__(*args, **kwargs)

        self.testLoader = None  # We are not use that

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

        suites = self.data.build_suite()

        if not suites:
            raise RuntimeError('No suites for running')

        self.data.before_run_callback()

        result = self.testRunner.run(suites)
        self.success = result.wasSuccessful()

        self.data.after_run_callback()

        if self.exit:
            sys.exit(not self.success)

        return self.success
