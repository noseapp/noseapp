# -*- coding: utf-8 -*-

from noseapp.app import extensions
from unittest import TestCase as BaseTestCase


class TestCase(BaseTestCase):
    """
    Базовый класс для всех TestCase
    """

    @classmethod
    def with_require(cls, require=None):
        """
        Инициализирует необходимые extensions

        :param require: спискок extensions
        """
        if require and hasattr(require, '__iter__'):
            for ext_name in require:
                setattr(cls, ext_name, extensions.get(ext_name, require))

        return cls
