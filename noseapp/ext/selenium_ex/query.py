# -*- coding: utf-8 -*-

"""
Модуль предоставляет удобный API для
поиска эелеменов в HTML документе
"""

import logging

from selenium.common.exceptions import NoSuchElementException

from noseapp.utils.common import waiting_for
from noseapp.utils.common import TimeoutException


logger = logging.getLogger(__name__)


QUERY_PATTERN = '{}[{}="{}"]'

REPLACE_ATTRIBUTES = {
    '_id': 'id',
    '_class': 'class',
}

REPLACE_TAGS = {
    'link': 'a',
}

DEFAULT_SLEEP = 0.01
DEFAULT_WAIT_TIMEOUT = 30


class QueryError(BaseException):
    """
    Ошибки при выполнении запросов
    """
    pass


def _execute(driver, query, get_all):
    """
    Выполняет запрос

    :param driver: экземпляр класса WebDriver
    :param query: строка запроса
    :param get_all: флаг указывающий на то, нужно вернуть множество или только один
    """
    logger.debug('CSS query: {} Get all: {}'.format(query, 'Yes' if get_all else 'No'))

    if get_all:
        return driver.find_elements_by_css_selector(query)
    try:
        return driver.find_element_by_css_selector(query)
    except NoSuchElementException as e:
        e.message += u'QueryProcessor(From: {}, Query: {})'.format(repr(driver), query)
        raise


def _replace_attribute(atr_name):
    """
    Заменяет название атрибута из словаря сопоставлений.
    Это необходимо т.к. некоторые имена зарезервированы
    в питоне и их нужно заменить.

    :param atr_name: имя атрибута
    """
    return REPLACE_ATTRIBUTES.get(atr_name, atr_name)


def _replace_tag(tag_name):
    """
    Заменяет название тега из словаря сопоставлений

    :param tag_name: название тега
    """
    return REPLACE_TAGS.get(tag_name, tag_name)


def _handler(driver, tag):
    """
    Обраотчик запросов к браузеру

    :param driver: экземпляр класса WebDriver
    :param tag: имя html тега
    """

    def handle(**kwargs):
        """
        :param kwargs: атрибут тега и значение
        """
        if not 0 < len(kwargs) < 2:
            raise QueryError('tag attribute must be one')

        tag_atr = kwargs.keys()[0]
        teg_atr_val = kwargs[tag_atr]

        query = QUERY_PATTERN.format(
            _replace_tag(tag), _replace_attribute(tag_atr), teg_atr_val,
        )

        return QueryResult(driver, query)

    return handle


class QueryResult(object):
    """
    Объект отвечает за формирование результата запроса
    """

    def __init__(self, driver, query):
        self._driver = driver
        self._query = query

    @property
    def exist(self):
        """
        Проверить наличие елемента на странице
        """
        try:
            el = self.first()
            if el:
                return True
            return False
        except NoSuchElementException:
            return False

    @property
    def exist_with_wait(self):
        """
        Проверить наличие елемента на странице
        с предварительным ожиданем появления
        """
        try:
            return self.wait()
        except TimeoutException:
            return False

    def wait(self, timeout=DEFAULT_WAIT_TIMEOUT, sleep=DEFAULT_SLEEP):
        """
        Ожидать появления элемента
        """
        return waiting_for(lambda: self.exist, timeout=timeout, sleep=sleep)

    def get(self, index):
        """
        Возврашщает по индексу
        """
        return _execute(self._driver, self._query, True)[index]

    def first(self):
        """
        Получить первый найденный
        """
        return _execute(self._driver, self._query, False)

    def first_with_wait(self):
        """
        Получить первый с предварительным ожиданием
        """
        try:
            self.wait()
        except TimeoutException:
            pass

        return _execute(self._driver, self._query, False)

    def all(self):
        """
        Получить все найденные
        """
        return _execute(self._driver, self._query, True)

    def all_with_wait(self):
        """
        Получить все с предварительным ожиданием первого
        """
        try:
            self.wait()
        except TimeoutException:
            pass

        return _execute(self._driver, self._query, True)


class QueryProcessor(object):
    """
    Класс реализует удобный интерфейс для
    выполнения запросов к инстансу класса
    WebDriver.

    Пример:

        driver = WebDriver()
        query = QueryProcessor(driver)

        search_wrapper = query.div(id='search').first()
        search_field = query(search_wrapper).input(_class='search').first()
        search_field.send_keys(*'Hello World!')
    """

    def __init__(self, driver):
        self._driver = driver

    def __getattr__(self, item):
        return _handler(self._driver, item)

    def __call__(self, element):
        """
        При вызове экземпляра создаем новый инстанс

        :param element: ожидается, что тут будет объект WebElement, хотя может быть и браузер
        """
        return self.__class__(element)

    def page_text(self):
        """
        Возвращает текст страницы
        """
        return self._driver.find_element_by_tag_name('body').text
