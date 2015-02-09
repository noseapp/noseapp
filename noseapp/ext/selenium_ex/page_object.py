# -*- coding: utf-8 -*-

from noseapp.ext.selenium_ex import QueryProcessor
from noseapp.ext.selenium_ex.tools import Container


def page_object_property(cls):
    """
    Привязать любой класс к объекту PageObject
    который принимает на вход driver
    """
    return Container(cls)


class PageObject(object):
    """
    Базовый PageObject класс
    """

    def __init__(self, driver):
        self._driver = driver
        self._query = QueryProcessor(driver)

        for atr in dir(self):
            val = getattr(self, atr, None)
            if isinstance(val, Container):
                setattr(self, atr, val(driver))
