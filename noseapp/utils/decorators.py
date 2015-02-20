# -*- coding: utf-8 -*-

from functools import wraps


def parametrize(*params):
    """
    Decorator for parametrize test case method
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for param in params:
                f(param, *args, **kwargs)
            return None
        return wrapped
    return wrapper
