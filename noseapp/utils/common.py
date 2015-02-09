# -*- coding: utf-8 -*-

import time

from noseapp.exc import CrashError


def crash(message):
    """
    Возбуждает исключение CrashError останавливая прогон

    :param message: сообщение
    """
    raise CrashError(message)


class TimeoutException(BaseException):
    pass


def waiting_for(func, timeout=30, sleep=0.5, stopped=False, args=None, kwargs=None):
    """
    Функция ожидания положительного ответа от callback

    :param func: функция callback
    :param timeout: время ожидания в секундах
    :param sleep: сколько спать на каждой итерации
    :param args, kwargs: аргументы которые нужно передать в callback
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
