# -*- coding: utf-8 -*-


# Config can be set from environment:
#
# export NOSEAPP_CONFIG='etc.base'
# export NOSEAPP_CONFIG='/home/user/project/etc/base.py'
CONFIG_CHECKOUT_ENV = 'NOSEAPP_CONFIG'


class RunStrategy(object):
    """
    Strategy to run tests
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
