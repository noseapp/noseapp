# -*- coding: utf-8 -*-

from functools import wraps


def parametrize(*params):
    """
    Позволяет параметризировать тест кейс

    :param params: параметры которые нужно передать в тест кейс
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for param in params:
                f(param, *args, **kwargs)
            return None
        return wrapped
    return wrapper
