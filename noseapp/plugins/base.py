# -*- coding: utf-8 -*-

from nose.plugins import Plugin as BasePlugin


class AppPlugin(BasePlugin):
    """
    Базовый класс для плагинов.
    Прокидываем инстанс app в плагин, чтобы можно
    было что-нибудь с ним сделать изнутри.
    """

    def __call__(self, app):
        self.app = app
        return self
