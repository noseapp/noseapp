# -*- coding: utf8 -*-

from multiprocessing import cpu_count

from gevent import hub
from gevent.pool import Pool

from noseapp.runner.suites.base import BaseSuite


def test_wrapper(data):
    test, orig = data
    test(orig)
    hub.sleep()


class GeventSuite(BaseSuite):
    """
    Run tests with gevent pool
    """

    def _run(self, result, orig):
        size = self.config.options.gevent_greanlets

        if size < 0:
            size = cpu_count() - 1

        pool = Pool(int(round(size)) or 2)
        pool.imap(test_wrapper, ((t, orig) for t in self._tests))
        pool.join()
