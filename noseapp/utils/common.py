# -*- coding: utf-8 -*-

import time


class TimeoutException(BaseException):
    pass


def waiting_for(func, timeout=30, sleep=0.5, args=None, kwargs=None):
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

        raise TimeoutException(mess)
