# -*- coding: utf-8 -*-

from functools import wraps


def flows(*flows):
    """
    Decorator for parametrize test method.

    Usage::

        from noseapp import Suite
        from noseapp import TestCase
        from noseapp.datastructures import Context

        suite = Suite(__name__)

        @suite.register
        class MyTestCase(TestCase):
            @flows(
                Context(integer=1, string='hello'),
                Context(integer=2, string='world'),
            )
            def test(self, ctx):
                ctx.integer
                ctx.string
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            for flow in flows:
                f(self, flow, *args, **kwargs)
        return wrapped
    return wrapper
