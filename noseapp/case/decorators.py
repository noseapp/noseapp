# -*- coding: utf-8 -*-

from functools import wraps


def flows(*flows):
    """
    Decorator for parametrize test method
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            for flow in flows:
                f(self, flow, *args, **kwargs)
            return None
        return wrapped
    return wrapper
