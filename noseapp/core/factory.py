# -*- coding: utf-8 -*-

from noseapp.runner.base import BaseTestRunner
from noseapp.core.constants import RunStrategy
from noseapp.suite.bases.simple import BaseSuite


class ClassFactory(object):
    """
    Factory for creation classes
    """

    def __init__(self, options):
        """
        :param options: nose config options
        """
        if options.run_strategy not in RunStrategy.ALL:
            raise ValueError(
                'Incorrect run strategy: "{}"'.format(options.run_strategy),
            )

        self._options = options

        self._current_suite_class = None
        self._current_runner_class = None

    @property
    def suite_class(self):
        if not self._current_suite_class:
            return self.create_suite_class()

        return self._current_suite_class

    @property
    def runner_class(self):
        if not self._current_runner_class:
            return self.create_runner_class()

        return self._current_runner_class

    def create_suite_class(self):
        """
        Create class for building suite
        """
        try:
            if self._options.run_strategy == RunStrategy.GEVENT and self._options.async_tests:
                from noseapp.suite.bases.gevent_suite import GeventSuite
                self._current_suite_class = GeventSuite

            elif self._options.run_strategy in (RunStrategy.MULTIPROCESSING, RunStrategy.THREADING)\
                    and self._options.async_tests:
                from noseapp.suite.bases.threading_suite import ThreadSuite
                self._current_suite_class = ThreadSuite

            else:
                if self._options.async_tests:
                    from noseapp.suite.bases.threading_suite import ThreadSuite
                    self._current_suite_class = ThreadSuite
                else:
                    self._current_suite_class = BaseSuite
        except AttributeError:
            self._current_suite_class = BaseSuite

        return self._current_suite_class

    def create_runner_class(self):
        """
        Create test runner class
        """
        try:
            if self._options.run_strategy == RunStrategy.MULTIPROCESSING\
                    or (self._options.run_strategy == RunStrategy.SIMPLE and self._options.async_suites):
                from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner
                self._current_runner_class = MultiprocessingTestRunner

            elif self._options.run_strategy == RunStrategy.GEVENT:
                from noseapp.runner.gevent_runner import GeventTestRunner
                self._current_runner_class = GeventTestRunner

            elif self._options.run_strategy == RunStrategy.THREADING:
                from noseapp.runner.threading_runner import ThreadingTestRunner
                self._current_runner_class = ThreadingTestRunner

            else:
                self._current_runner_class = BaseTestRunner
        except AttributeError:
            self._current_runner_class = BaseTestRunner

        return self._current_runner_class
