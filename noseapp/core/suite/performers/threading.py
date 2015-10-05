# -*- coding: utf8 -*-

from __future__ import absolute_import

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from noseapp.core.suite.base import BaseSuite
from noseapp.core.suite.base import SuitePerformer


class ThreadSuitePerformer(SuitePerformer):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    def __call__(self, pool=None):
        self_pool = not bool(pool)
        size = self.suite.config.options.async_tests

        if size <= 0:
            size = cpu_count() / 2

        pool = pool or ThreadPool(int(round(size)) or 2)

        for test in self.suite.tests:
            if self.result.shouldStop:
                break

            if isinstance(test, BaseSuite):
                test.run(self.result, pool=pool)
                continue

            pool.apply_async(self.run_one_test, args=(test, ))

        if self_pool:
            pool.close()
            pool.join()
