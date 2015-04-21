# -*- coding: utf-8 -*-

from noseapp.runner.base import BaseTestRunner
from noseapp.suite.bases.simple import BaseSuite


class ClassFactory(object):
    """
    Factory for creation classes
    """

    def __init__(self, options):
        """
        :param options: nose config options
        """
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
            if not self._options.app_processes and self._options.gevent_greenlets:
                from noseapp.suite.bases.gevent_suite import GeventSuite
                self._current_suite_class = GeventSuite

            elif self._options.app_processes and self._options.thread_pool:
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
            if self._options.app_processes:
                from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner
                self._current_runner_class = MultiprocessingTestRunner

            elif self._options.gevent_pool:
                from noseapp.runner.gevent_runner import GeventTestRunner
                self._current_runner_class = GeventTestRunner

            elif self._options.thread_pool:
                from noseapp.runner.threading_runner import ThreadingTestRunner
                self._current_runner_class = ThreadingTestRunner

            else:
                self._current_runner_class = BaseTestRunner
        except AttributeError:
            self._current_runner_class = BaseTestRunner

        return self._current_runner_class
