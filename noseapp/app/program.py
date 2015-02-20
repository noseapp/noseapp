# -*- coding: utf8 -*-

import sys

from nose.core import TestProgram as BaseTestProgram

from noseapp.app import extensions
from noseapp.suite.collector import CollectSuites


BASIC_STRATEGY = 'basic'
GEVENT_STRATERY = 'gevent'
THREADS_STRATEGY = 'threads'
MULTIPROCESSING_STRATEGY = 'multiprocessing'


def _get_strategy(options):
    if options.app_processes:
        return MULTIPROCESSING_STRATEGY
    elif options.gevent_pool:
        return GEVENT_STRATERY
    elif options.thread_pool:
        return THREADS_STRATEGY
    else:
        return BASIC_STRATEGY


def get_test_runner_class(options):
    """
    :return: nose.core.TextTestRunner
    """
    strategy = _get_strategy(options)

    if strategy == BASIC_STRATEGY:
        from noseapp.runner.base import BaseTestRunner
        return BaseTestRunner
    elif strategy == MULTIPROCESSING_STRATEGY:
        from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner
        return MultiprocessingTestRunner
    elif strategy == GEVENT_STRATERY:
        from noseapp.runner.gevent_runner import GeventTestRunner
        return GeventTestRunner
    elif strategy == THREADS_STRATEGY:
        from noseapp.runner.threads_runner import ThreadsTestRunner
        return ThreadsTestRunner


class TestProgram(BaseTestProgram):

    collector_class = CollectSuites

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
