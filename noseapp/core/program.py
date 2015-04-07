# -*- coding: utf8 -*-

import sys

from nose.core import TestProgram as BaseTestProgram

from noseapp.core import extensions
from noseapp.core.factory import ClassFactory
from noseapp.core.collector import CollectSuite


class TestProgram(BaseTestProgram):

    class_factory = ClassFactory
    collector_class = CollectSuite

    def __init__(self, app, argv, *args, **kwargs):
        self._app = app
        self._argv = argv

        super(TestProgram, self).__init__(argv=argv, *args, **kwargs)

        self._app.config.init_nose_config(self.config)
        self._app.initialize()

    # disarm base class
    def createTests(self):
        pass

    def runTests(self):
        pass

    def perform(self):
        """
        Perform test program
        """
        class_factory = self.class_factory(self.config.options)
        collector = self.collector_class(
            self._argv,
            self._app.suites,
            self.testLoader,
            class_factory,
            self.config,
        )

        suites = collector.make_result()

        extensions.clear()
        del collector

        self.testRunner = class_factory.runner_class(
            stream=self.config.stream,
            verbosity=self.config.verbosity,
            config=self.config,
        )

        plug_runner = self.config.plugins.prepareTestRunner(self.testRunner)

        if plug_runner is not None:
            self.testRunner = plug_runner

        del class_factory

        self._app.before()

        result = self.testRunner.run(suites)
        self.success = result.wasSuccessful()

        self._app.after()

        if self.exit:
            sys.exit(not self.success)

        return self.success
