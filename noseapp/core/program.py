# -*- coding: utf8 -*-

import sys

from nose.core import TestProgram as BaseTestProgram

from noseapp.core import extensions
from noseapp.core.collector import CollectSuite


def get_test_runner_class(options):
    """
    :return: nose.core.TextTestRunner
    """
    if options.app_processes:
        from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner
        return MultiprocessingTestRunner

    elif options.gevent_pool:
        from noseapp.runner.gevent_runner import GeventTestRunner
        return GeventTestRunner

    elif options.thread_pool:
        from noseapp.runner.threading_runner import ThreadingTestRunner
        return ThreadingTestRunner

    from noseapp.runner.base import BaseTestRunner
    return BaseTestRunner


class TestProgram(BaseTestProgram):

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
        collector = self.collector_class(
            self._argv, self._app.suites, self.testLoader, self.config,
        )
        suites = collector.make_result()

        extensions.clear()

        test_runner = get_test_runner_class(self.config.options)

        self.testRunner = test_runner(stream=self.config.stream,
                                      verbosity=self.config.verbosity,
                                      config=self.config)

        plug_runner = self.config.plugins.prepareTestRunner(self.testRunner)

        if plug_runner is not None:
            self.testRunner = plug_runner

        self._app.before()

        result = self.testRunner.run(suites)
        self.success = result.wasSuccessful()

        self._app.after()

        if self.exit:
            sys.exit(not self.success)

        return self.success
