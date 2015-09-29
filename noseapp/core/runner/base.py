# -*- coding: utf-8 -*-

import time
from contextlib import contextmanager

from nose.core import TextTestRunner as _TextTestRunner
from nose.result import TextTestResult as _TextTestResult


class TextTestResult(_TextTestResult):
    pass


@contextmanager
def setup_teardown(suites):
    suites.setUp()
    try:
        yield
    finally:
        suites.tearDown()


class RunPerformer(object):

    def __init__(self, runner):
        self.runner = runner

    def __call__(self, suites, result):
        """
        :type suites: noseapp.core.suite.base.BaseSuite
        :type result: noseapp.core.runner.base.TextTestResult
        """
        for suite in suites:
            suite(result)


class BaseTestRunner(_TextTestRunner):

    result_class = TextTestResult
    performer_class = RunPerformer

    def _makeResult(self):
        return self.result_class(
            self.stream,
            self.descriptions,
            self.verbosity,
            self.config,
        )

    def _makePerformer(self):
        return self.performer_class(self)

    def run(self, suites):
        wrapper = self.config.plugins.prepareTest(suites)
        if wrapper is not None:
            suites = wrapper

        wrapped = self.config.plugins.setOutputStream(self.stream)
        if wrapped is not None:
            self.stream = wrapped

        result = self._makeResult()
        performer = self._makePerformer()

        start = time.time()
        with setup_teardown(suites):
            performer(suites, result)
        stop = time.time()

        result.printErrors()
        result.printSummary(start, stop)

        self.config.plugins.finalize(result)

        return result


__all__ = (
    RunPerformer,
    TextTestResult,
    BaseTestRunner,
)
