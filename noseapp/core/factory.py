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
        from noseapp.core.suite.base import BaseSuite

        self.__current_suite_class = BaseSuite

        performer_class = BaseSuite.performer_class

        try:
            if self.__options.run_strategy == RunStrategy.GEVENT and self.__options.async_tests:
                from noseapp.core.suite.performers.gevent import GeventSuitePerformer
                performer_class = GeventSuitePerformer

            elif self.__options.run_strategy in (RunStrategy.MULTIPROCESSING, RunStrategy.THREADING)\
                    and self.__options.async_tests:
                from noseapp.core.suite.performers.threading import ThreadSuitePerformer
                performer_class = ThreadSuitePerformer

            else:
                if self.__options.async_tests:
                    from noseapp.core.suite.performers.threading import ThreadSuitePerformer
                    performer_class = ThreadSuitePerformer

        except AttributeError:
            pass

        self.__current_suite_class.performer_class = performer_class

        logger.debug(
            'Current suite performer class is "%s"',
            performer_class.__name__,
        )

        return self.__current_suite_class

    def create_runner_class(self):
        """
        Create test runner class
        """
        from noseapp.core.runner.base import BaseTestRunner

        self.__current_runner_class = BaseTestRunner

        performer_class = BaseTestRunner.performer_class

        try:
            if self.__options.run_strategy == RunStrategy.MULTIPROCESSING\
                    or (self.__options.run_strategy == RunStrategy.SIMPLE and self.__options.async_suites):
                from noseapp.core.runner.performers.multiprocessing import MPRunPerformer
                performer_class = MPRunPerformer

            elif self.__options.run_strategy == RunStrategy.GEVENT:
                from noseapp.core.runner.performers.gevent import GeventRunPerformer
                performer_class = GeventRunPerformer

            elif self.__options.run_strategy == RunStrategy.THREADING:
                from noseapp.core.runner.performers.threading import ThreadingRunPerformer
                performer_class = ThreadingRunPerformer

        except AttributeError:
            pass

        self.__current_runner_class.performer_class = performer_class

        logger.debug('Current run performer class is "%s"', performer_class.__name__)

        return self.__current_runner_class
