# -*- coding: utf8 -*-

from __future__ import absolute_import

from multiprocessing import cpu_count

from gevent.pool import Pool

from noseapp.core.suite.base import BaseSuite
from noseapp.core.suite.base import SuitePerformer


class GeventSuitePerformer(SuitePerformer):
    """
    Run tests with gevent pool
    """

    def __call__(self, pool=None):
        self_pool = not bool(pool)
        size = self.suite.config.options.async_tests

        if size <= 0:
            size = cpu_count() / 2

        pool = pool or Pool(int(round(size)) or 2)

        for test in self.suite.tests:
            if self.result.shouldStop:
                break

            if isinstance(test, BaseSuite):
                test.run(self.result, pool=pool)
                continue

            pool.spawn(self.run_one_test, test)

        if self_pool:
            pool.join()
