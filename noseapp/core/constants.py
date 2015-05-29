# -*- coding: utf-8 -*-


class RunStrategy(object):
    """
    Strategy for run tests
    """

    SIMPLE = 'simple'
    GEVENT = 'gevent'
    THREADING = 'threading'
    MULTIPROCESSING = 'multiprocessing'

    ALL = (
        SIMPLE,
        GEVENT,
        THREADING,
        MULTIPROCESSING,
    )
