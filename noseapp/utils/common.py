# -*- coding: utf-8 -*-

import time


WAITING_FOR_SLEEP = 0.5
WAITING_FOR_TIMEOUT = 30


class TimeoutException(BaseException):
    pass


def waiting_for(func, timeout=None, sleep=None, args=None, kwargs=None):
    """
    :param func: callback function
    :param timeout: number of seconds for timeout
    :param sleep: number of second for sleep after call function
    :param args, kwargs: callback arguments
    """
    args = args or tuple()
    kwargs = kwargs or {}

    sleep = sleep or WAITING_FOR_SLEEP
    timeout = timeout or WAITING_FOR_TIMEOUT

    t_start = time.time()

    while time.time() <= t_start + timeout:
        result = func(*args, **kwargs)

        if result:
            return result

        time.sleep(sleep)
    else:
        mess = 'Timeout {timeout} exceeded.'.format(timeout=timeout)

        raise TimeoutException(mess)
