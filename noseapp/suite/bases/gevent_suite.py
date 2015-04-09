# -*- coding: utf8 -*-

from multiprocessing import cpu_count

from gevent.pool import Pool

from noseapp.suite.bases.simple import BaseSuite


class GeventSuite(BaseSuite):
    """
    Run tests with gevent pool
    """

    def _run_suite_handler(self, result, orig):
        size = self.config.options.gevent_greenlets

        if size < 0:
            size = cpu_count() - 1

        pool = Pool(int(round(size)) or 2)

        for test in self._tests:
            if result.shouldStop:
                    break

            pool.spawn(self._run_test_handler, test, orig)

        pool.join()
