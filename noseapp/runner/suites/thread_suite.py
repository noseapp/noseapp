# -*- coding: utf8 -*-

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from noseapp.runner.suites.base import BaseSuite


def test_wrapper(data):
    test, orig = data
    test(orig)


class ThreadSuite(BaseSuite):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    def _run(self, result, orig):
        size = self.config.options.thread_pool

        if size < 0:
            size = cpu_count() / 2

        pool = ThreadPool(int(round(size)) or 2)
        pool.imap(test_wrapper, ((t, orig) for t in self._tests))
        pool.close()
        pool.join()
