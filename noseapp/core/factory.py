# -*- coding: utf-8 -*-

import logging

from noseapp.core.constants import RunStrategy


logger = logging.getLogger(__name__)


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

        self.__options = options

        self.__current_suite_class = None
        self.__current_runner_class = None

    @property
    def options(self):
        return self.__options

    @property
    def suite_class(self):
        if not self.__current_suite_class:
            return self.create_suite_class()

        return self.__current_suite_class

    @property
    def runner_class(self):
        if not self.__current_runner_class:
            return self.create_runner_class()

        return self.__current_runner_class

    def create_suite_class(self):
        """
        Create class for building suite
        """
        from noseapp.suite.bases.simple import BaseSuite

        try:
            if self.__options.run_strategy == RunStrategy.GEVENT and self.__options.async_tests:
                from noseapp.suite.bases.gevent_suite import GeventSuite
                self.__current_suite_class = GeventSuite

            elif self.__options.run_strategy in (RunStrategy.MULTIPROCESSING, RunStrategy.THREADING)\
                    and self.__options.async_tests:
                from noseapp.suite.bases.threading_suite import ThreadSuite
                self.__current_suite_class = ThreadSuite

            else:
                if self.__options.async_tests:
                    from noseapp.suite.bases.threading_suite import ThreadSuite
                    self.__current_suite_class = ThreadSuite
                else:
                    self.__current_suite_class = BaseSuite
        except AttributeError:
            self.__current_suite_class = BaseSuite

        logger.debug('Current suite class is "%s"', self.__current_suite_class.__name__)

        return self.__current_suite_class

    def create_runner_class(self):
        """
        Create test runner class
        """
        from noseapp.runner.base import BaseTestRunner

        try:
            if self.__options.run_strategy == RunStrategy.MULTIPROCESSING\
                    or (self.__options.run_strategy == RunStrategy.SIMPLE and self.__options.async_suites):
                from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner
                self.__current_runner_class = MultiprocessingTestRunner

            elif self.__options.run_strategy == RunStrategy.GEVENT:
                from noseapp.runner.gevent_runner import GeventTestRunner
                self.__current_runner_class = GeventTestRunner

            elif self.__options.run_strategy == RunStrategy.THREADING:
                from noseapp.runner.threading_runner import ThreadingTestRunner
                self.__current_runner_class = ThreadingTestRunner

            else:
                self.__current_runner_class = BaseTestRunner
        except AttributeError:
            self.__current_runner_class = BaseTestRunner

        logger.debug('Current runner class is "%s"', self.__current_runner_class.__name__)

        return self.__current_runner_class
