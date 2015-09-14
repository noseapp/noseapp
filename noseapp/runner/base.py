# -*- coding: utf-8 -*-

import time
from contextlib import contextmanager

from nose import SkipTest
from nose.core import TextTestRunner as _TextTestRunner


@contextmanager
def measure_time(result):
    start = time.time()
    yield
    stop = time.time()

    result.printErrors()
    result.printSummary(start, stop)


class BaseTestRunner(_TextTestRunner):
    pass

    # def _makeResult(self):
    #     result = super(BaseTestRunner, self)._makeResult()
    #
    #     if SkipTest not in result.errorClasses:
    #         result.errorClasses[SkipTest] = (result.skipped, 'skipped', False)
    #
    #     return result


__all__ = (
    measure_time,
    BaseTestRunner,
)
