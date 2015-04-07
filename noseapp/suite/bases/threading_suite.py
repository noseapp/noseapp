# -*- coding: utf8 -*-

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from noseapp.suite.bases.simple import BaseSuite


class ThreadSuite(BaseSuite):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    def _run_suite_handler(self, result, orig):
        size = self.config.options.thread_pool

        if size < 0:
            size = cpu_count() / 2

        pool = ThreadPool(int(round(size)) or 2)

        for test in self._tests:
            if result.shouldStop:
                    break

            pool.apply_async(self._run_test_handler, args=(test, orig))

        pool.close()
        pool.join()
