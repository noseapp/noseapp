# -*- coding: utf-8 -*-

import time

from noseapp.exc import CrashError


def crash(message):
    raise CrashError(message)


class TimeoutException(BaseException):
    pass


def waiting_for(func, timeout=30, sleep=0.5, stopped=False, args=None, kwargs=None):
    """
    :param func: callback function
    :param timeout: number of seconds for timeout
    :param sleep: number of second for sleep after call function
    :param args, kwargs: callback arguments
    """
    args = args or tuple()
    kwargs = kwargs or {}

    t_start = time.time()

    while time.time() <= t_start + timeout:
        result = func(*args, **kwargs)

        if result:
            return result

        time.sleep(sleep)
    else:
        mess = 'Timeout {timeout} exceeded.'.format(timeout=timeout)

        if stopped:
            crash(mess)

        raise TimeoutException(mess)
