# -*- coding: utf8 -*-

from multiprocessing import cpu_count

from gevent import hub
from gevent.pool import Pool

from noseapp.runner.suites.base import BaseSuite


def test_wrapper(data):
    """
    Обертка над тестом и результатом.
    Необходима для того чтобы замапить result и test.
    """
    test, orig = data
    test(orig)
    hub.sleep()  # передаем управление на hub


class GeventSuite(BaseSuite):
    """
    Suite которая запускает тесты в Pool gevent-а
    """

    def _run(self, result, orig):
        size = self.config.options.gevent_greanlets

        if size < 0:
            size = cpu_count() - 1

        pool = Pool(int(round(size)) or 2)
        pool.imap(test_wrapper, ((t, orig) for t in self._tests))
        pool.join()
