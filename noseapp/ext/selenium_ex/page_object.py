# -*- coding: utf-8 -*-

import re
from copy import copy
from functools import wraps

from noseapp.ext.selenium_ex import QueryProcessor
from selenium.common.exceptions import NoSuchElementException


def page_object_property(f):
    """
    Декоратор. Ожидается, что метод который
    станет свойством будет возвращать объект
    принимающий на вход инстанс WebDriver или WebElement
    """
    @wraps(f)
    def wrapper(self):
        return f(self)(self._driver)
    return property(wrapper)


class PageObject(object):
    """
    Базовый PageObject класс
    """

    def __init__(self, driver):
        self._driver = driver
        self._query = QueryProcessor(driver)

    def __call__(self):
        """
        При вызове объекта отдать его копию
        """
        return copy(self)

    @property
    def text(self):
        """
        Возвращает текст страницы
        """
        try:
            return self._query.page_text()
        except NoSuchElementException:
            return None

    def wait_complete(self):
        """
        Ожидается, что в этом методе будет описан
        сценарий ожидания загрузки страницы
        """
        pass


class PageIsNotFound(BaseException):
    pass


class PageRouter(object):
    """
    Класс реализует связь между PageObject
    и путем по которому находится страница
    """

    __rules = {}

    def __init__(self, driver, base_path=None):
        self._driver = driver
        self._base_path = base_path

    @classmethod
    def add_rule(cls, rule, page_cls):
        """
        Добавить новое правило

        :param rule: правило в виде строки. поддерживаются
         регулярные выражения без ^ и $
        :param page_cls: класс-наследник PageObject
        """
        if not issubclass(page_cls, PageObject):
            raise ValueError('page is not PageObject subclass')

        cls.__rules[re.compile(r'^{}$'.format(rule))] = page_cls

    def get(self, path, wait=True):
        """
        Получить страницу по пути

        :type path: str
        """
        for rule in self.__rules:
            if rule.search(path) is not None:
                page_cls = self.__rules[rule]
                page = page_cls(self._driver)
                break
        else:
            raise PageIsNotFound(path)

        if self._base_path is not None:
            self._driver.get('{}{}'.format(self._base_path, path))

            if wait:
                page.wait_complete()

        return page
