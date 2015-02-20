# -*- coding: utf-8 -*-

import time
from contextlib import contextmanager


@contextmanager
def measure_time(result):
    start = time.time()
    yield
    stop = time.time()

    result.printErrors()
    result.printSummary(start, stop)
