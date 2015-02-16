# -*- coding: utf-8 -*-


class Config(dict):
    """
    Предполагается, что этот словарь
    будет хранить базовую конфигурацию
    """

    def configure(self, **params):
        self.update(params)

    def dns_configure(self, **params):
        """
        Конфигурирует параметры для строки dns
        """
        self['dns_params'].update(params)
