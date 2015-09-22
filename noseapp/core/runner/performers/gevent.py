# -*- coding: utf-8 -*-

from __future__ import absolute_import

from multiprocessing import cpu_count

from gevent.pool import Pool

from noseapp.core.runner.base import RunPerformer


class GeventRunPerformer(RunPerformer):
    """
    Run suites with gevent
    """

    def __call__(self, suites, result):
        size = self.runner.config.options.async_suites

        if size < 0:
            size = cpu_count()

        pool = Pool(size)

        for suite in suites:
            pool.spawn(suite, result)

        pool.join()
