# -*- coding: utf8 -*-

from multiprocessing import cpu_count

from gevent.pool import Pool

from noseapp.runner.base import measure_time
from noseapp.runner.base import BaseTestRunner


class GeventTestRunner(BaseTestRunner):
    """
    Run suites with gevent
    """

    def run(self, suites):
        wrapper = self.config.plugins.prepareTest(suites)
        if wrapper is not None:
            suites = wrapper

        wrapped = self.config.plugins.setOutputStream(self.stream)
        if wrapped is not None:
            self.stream = wrapped

        result = self._makeResult()

        size = self.config.options.gevent_pool
        if size < 0:
            size = cpu_count()

        pool = Pool(size)

        with measure_time(result):
            for suite in suites:
                pool.spawn(suite, result)
            pool.join()

        self.config.plugins.finalize(result)
        return result
