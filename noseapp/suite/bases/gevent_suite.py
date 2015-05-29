# -*- coding: utf8 -*-

from multiprocessing import cpu_count

from gevent.pool import Pool

from noseapp.suite.bases.simple import RunSuite
from noseapp.suite.bases.simple import BaseSuite


class GeventRunSuite(RunSuite):

    def perform(self):
        size = self._suite.config.options.async_tests

        if size < 0:
            size = cpu_count() - 1

        pool = Pool(int(round(size)) or 2)

        for test in self._suite.tests:
            if self._result.shouldStop:
                break

            pool.spawn(self.run_test, test)

        pool.join()


class GeventSuite(BaseSuite):
    """
    Run tests with gevent pool
    """

    run_suite_class = GeventRunSuite
