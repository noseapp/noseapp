# -*- coding: utf-8 -*-

import time
from contextlib import contextmanager

from nose.core import TextTestRunner as BaseTestRunner


@contextmanager
def measure_time(result):
    start = time.time()
    yield
    stop = time.time()

    result.printErrors()
    result.printSummary(start, stop)


__all__ = (
    BaseTestRunner,
)
