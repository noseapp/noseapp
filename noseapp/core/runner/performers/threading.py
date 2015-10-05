# -*- coding: utf8 -*-

from __future__ import absolute_import

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from noseapp.core.runner.base import RunPerformer


class ThreadingRunPerformer(RunPerformer):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    def __call__(self, suites, result):
        size = self.runner.config.options.async_suites

        if size <= 0:
            size = cpu_count()

        pool = ThreadPool(size)

        for suite in suites:
            pool.apply_async(suite, args=(result,))

        pool.close()
        pool.join()
