# -*- coding: utf8 -*-

import logging
from multiprocessing import cpu_count

from gevent.pool import Pool

from noseapp.suite.bases.simple import run_test
from noseapp.suite.bases.simple import BaseSuite


logger = logging.getLogger(__name__)


def perform_chain(suite, result, orig, pool=None):
    self_pool = not bool(pool)
    size = suite.config.options.async_tests

    logger.debug(
        'Perform chain of {}. Pool: {}, Max size: {}'.format(
            suite, pool, size,
        ),
    )

    if size < 0:
        size = cpu_count() - 1

    if self_pool:
        pool = Pool(int(round(size)) or 2)

    for test in suite.tests:
        if result.shouldStop:
            break

        if isinstance(test, BaseSuite):
            test.run(result, pool=pool)
            continue

        pool.spawn(run_test, suite, test, orig)

    if self_pool:
        pool.join()


class GeventSuite(BaseSuite):
    """
    Run tests with gevent pool
    """

    perform_chain = perform_chain
