# -*- coding: utf-8 -*-

"""
A powerful, extensible and easy to use framework for test development

By Trifonov Mikhail

For support, use the https://github.com/noseapp/noseapp/issues tracker
"""

from noseapp.app.base import NoseApp

from noseapp.suite.base import Suite

from noseapp.case import step
from noseapp.case import TestCase
from noseapp.case import ScreenPlayCase

from noseapp.plugins import AppPlugin


__all__ = (
    step,
    Suite,
    NoseApp,
    TestCase,
    AppPlugin,
    ScreenPlayCase,
)
