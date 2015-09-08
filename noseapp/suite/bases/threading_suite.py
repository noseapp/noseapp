# -*- coding: utf8 -*-

import logging
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

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
        size = cpu_count() / 2

    if self_pool:
        pool = pool or ThreadPool(int(round(size)) or 2)

    for test in suite.tests:
        if result.shouldStop:
            break

        if isinstance(test, BaseSuite):
            test.run(result, pool=pool)
            continue

        pool.apply_async(run_test, args=(suite, test, orig))

    if self_pool:
        pool.close()
        pool.join()


class ThreadSuite(BaseSuite):
    """
    Run tests with multiprocessing.pool.ThreadPool
    """

    perform_chain = perform_chain
