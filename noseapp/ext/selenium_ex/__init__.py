# -*- coding: utf-8 -*-

from noseapp.ext.selenium_ex import drivers
from noseapp.ext.selenium_ex.base import SeleniumEx
from noseapp.ext.selenium_ex.query import QueryProcessor
from noseapp.ext.selenium_ex.page_object import PageObject
from noseapp.ext.selenium_ex.page_object import PageRouter
from noseapp.ext.selenium_ex.page_object import page_object_property


__all__ = (
    SeleniumEx,
    PageObject,
    PageRouter,
    QueryProcessor,
    page_object_property,
)


_BASE_CONFIG = {  # скелет конфигурации
    'REMOTE_WEBDRIVER': {
        'options': {},  # опции которые будут переданы в инициализатор класса
        'capabilities': {  # указанные здесь параметры будут переписаны в capabilities
            drivers.IE: {},
            drivers.OPERA: {},
            drivers.CHROME: {},
            drivers.FIREFOX: {},
            drivers.PHANTOMJS: {},
        },
    },

    # указанные ниже параметры будут переданны в инициализатор класса WebDriver

    'IE_WEBDRIVER': {},

    'CHROME_WEBDRIVER': {},

    'FIREFOX_WEBDRIVER': {},

    'PHANTOMJS_WEBDRIVER': {},

    'OPERA_WEBDRIVER': {},
}


def make_config():
    """
    Создать скелет конфигурации
    """
    return Config(_BASE_CONFIG)


class Config(dict):

    def remote_configure(self, options=None, capabilities=None):
        """
        Сконфигурировать remote web driver

        :param options: опции которые будут переданы в инициализатор класса
        :param capabilities: словарь для обновления capabilities браузеров
        """
        self['REMOTE_WEBDRIVER']['options'].update(options or {})
        self['REMOTE_WEBDRIVER']['capabilities'].update(capabilities or {})

    def ie_configure(self, **options):
        """
        Сконфигурировать ie driver

        :param options: опции которые будут переданы в инициализатор класса
        """
        self['IE_WEBDRIVER'].update(options)

    def chrome_configure(self, **options):
        """
        Сконфигурировать chrome driver

        :param options: опции которые будут переданы в инициализатор класса
        """
        self['CHROME_WEBDRIVER'].update(options)

    def firefox_configure(self, **options):
        """
        Сконфигурировать firefox driver

        :param options: опции которые будут переданы в инициализатор класса
        """
        self['FIREFOX_WEBDRIVER'].update(options)

    def phantomjs_configure(self, **options):
        """
        Сконфигурировать phantomjs driver

        :param options: опции которые будут переданы в инициализатор класса
        """
        self['PHANTOMJS_WEBDRIVER'].update(options)

    def opera_configure(self, **options):
        """
        Сконфигурировать opera driver

        :param options: опции которые будут переданы в инициализатор класса
        """
        self['OPERA_WEBDRIVER'].update(options)
