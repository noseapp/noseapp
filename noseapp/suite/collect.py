# -*- coding: utf-8 -*-

"""
Модуль собирает suite с указанным TestMethod, TestCase или Suite
"""

import re

from noseapp.runner.suites.base import BaseSuite


base_pattern = re.compile(r'^.*\.')

case_load_pattern = re.compile(r'^.*\:')
method_load_pattern = re.compile(r'^.*\..*\:.*\.')


CASE_LOAD_TYPE = 'case'
SUITE_LOAD_TYPE = 'suite'
METHOD_LOAD_TYPE = 'method'


class CollectError(BaseException):
    pass


class CollectResult(list):
    """
    Результат сборки
    """

    def __init__(self, suite):
        super(CollectResult, self).__init__([suite])


class CollectSuites(object):
    """
    Класс выполняет работу по сборке suite
    на соновании инсрукции sys.argv
    """

    def __init__(self, load_path, suites, test_loader, nose_config):
        if base_pattern.search(load_path) is not None:
            self._load_path = load_path
        else:
            self._load_path = None

        self._nose_config = nose_config
        self._test_loader = test_loader

        if self._load_path:
            self._mp = self.create_map(suites)

        self.result = None

    def _get_suite(self, name):
        """
        Возвращает suite по имени
        """
        try:
            return self._mp[name]
        except KeyError:
            raise CollectError(
                'Suite "{}" is not found'.format(self._load_path),
            )

    def _get_case(self, case_name, mp):
        """
        Возвращает case из карты mp
        """
        try:
            return mp[case_name]['cls']
        except KeyError:
            raise CollectError('TestCase "{}" is not found'.format(case_name))

    @property
    def load_type(self):
        # Порядок сравнения важен!!!
        if not self._load_path:
            return

        if method_load_pattern.search(self._load_path) is not None:
            return METHOD_LOAD_TYPE

        if case_load_pattern.search(self._load_path) is not None:
            return CASE_LOAD_TYPE

        return SUITE_LOAD_TYPE

    def empty(self):
        """
        Если результат путой, то True иначе False
        """
        return not bool(self.result)

    def create_map(self, suites):
        """
        Создает карту сопоставления имени suite к инстансу
        """
        mp = {}

        for suite in suites:
            mp[suite.name] = suite

        return mp

    def load_suite(self):
        """
        Загрузить только одн suite
        """
        suite = self._get_suite(self._load_path)
        self.result = CollectResult(
            suite(self._nose_config, self._test_loader),
        )

    def load_case(self):
        """
        Загрузить один TestCase класс
        """
        suite_name, case_name = self._load_path.split(':')
        app_suite = self._get_suite(suite_name)

        mp = app_suite.get_map()
        case = self._get_case(case_name, mp)

        suite = BaseSuite(config=self._nose_config)
        suite.addTests(
            self._test_loader.loadTestsFromTestCase(
                case.with_require(app_suite.require),
            ),
        )
        self.result = CollectResult(suite)

    def load_method(self):
        """
        Загрузить метод класса TestCase
        """
        suite_name, case_info = self._load_path.split(':')
        case_name, method_name = case_info.split('.')

        app_suite = self._get_suite(suite_name)
        mp = app_suite.get_map()
        case = self._get_case(case_name, mp)

        try:
            suite = BaseSuite(
                map(case.with_require(app_suite.require), [method_name]),
                config=self._nose_config,
            )
        except ValueError:
            raise CollectError(
                'Method "{}" of class "{}" is not found'.format(method_name, case_name)
            )

        self.result = CollectResult(suite)

    def make_result(self):
        """
        Выполнить загрузку suites
        """
        load_type = self.load_type

        if load_type is SUITE_LOAD_TYPE:
            self.load_suite()

        elif load_type is CASE_LOAD_TYPE:
            self.load_case()

        elif load_type is METHOD_LOAD_TYPE:
            self.load_method()
