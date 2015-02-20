# -*- coding: utf-8 -*-

from noseapp.app import extensions
from unittest import TestCase as BaseTestCase


class TestCase(BaseTestCase):
    """
    Base case class
    """

    @classmethod
    def with_require(cls, require=None):
        """
        Init require extensions

        :param require: extensions list
        :type require: list or tuple
        """
        if require and hasattr(require, '__iter__'):
            for ext_name in require:
                setattr(cls, ext_name, extensions.get(ext_name, require))

        return cls
