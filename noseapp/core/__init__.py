# -*- coding: utf8 -*-

"""
Core of framework.

If you write modules of core and they're using other modules
of library that make using import inside functions or methods.
"""

from .program import TestProgram


class ExtensionInstaller(object):
    """
    Container for extension.
    Lazy creating instance.
    """

    def __init__(self, cls, args, kwargs):
        self.name = cls.name

        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.cls(*self.args, **self.kwargs)


__all__ = (
    TestProgram,
    ExtensionInstaller,
)
