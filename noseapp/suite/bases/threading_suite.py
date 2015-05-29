# -*- coding: utf8 -*-

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from noseapp.suite.bases.simple import RunSuite
from noseapp.suite.bases.simple import BaseSuite


class ThreadingRunSuite(RunSuite):

    def perform(self):
        size = self._suite.config.options.async_tests

        if size < 0:
            size = cpu_count() / 2

        pool = ThreadPool(int(round(size)) or 2)

        for test in self._suite.tests:
            if self._result.shouldStop:
                break

            pool.apply_async(self.run_test, args=(test,))

        pool.close()
        pool.join()


class ThreadSuite(BaseSuite):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    run_suite_class = ThreadingRunSuite
