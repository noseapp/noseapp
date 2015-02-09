# -*- coding: utf-8 -*-

from noseapp.suite.mediator import TestCaseMediator


class Suite(object):
    """
    Suite для групп TestCase
    """

    mediator_class = TestCaseMediator

    def __init__(self, name, require=None):
        """
        :param name: имя suite
        :param require: необходимые расширениия
        """
        self._name = name
        self._require = require
        self._mediator = self.mediator_class(require=require)

    @property
    def name(self):
        return self._name

    @property
    def require(self):
        return self._require

    def register(self, cls):
        """
        Регистрирует класс TestCase в текущей suite

        :type cls: unittest.TestCase
        """
        self._mediator.add_test_case(cls)
        return cls

    def get_map(self):
        """
        Возвращает карту для поиска
        TestCase классов и тест методов
        """
        return self._mediator.create_map()

    def __call__(self, nose_config, test_loader):
        """
        При вызове экземпляра возвращает иснстанс объекта ContextSuite
        в котором собраны все тесты из TestCase классов

        :param nose_config: конфиг nose
        :param test_loader: инстанс TestLoader
        """
        return self._mediator.create_suite(nose_config, test_loader)

    def __repr__(self):
        return '<Suite {}>'.format(self._name)
