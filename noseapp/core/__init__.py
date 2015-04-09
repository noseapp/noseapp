# -*- coding: utf8 -*-

from noseapp.core.program import TestProgram
from noseapp.core.collector import CollectSuite
from noseapp.core.loader import load_suites_from_path


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
    CollectSuite,
    ExtensionInstaller,
    load_suites_from_path,
)
