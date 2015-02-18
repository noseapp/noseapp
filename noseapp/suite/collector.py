# -*- coding: utf-8 -*-

import re

from noseapp.runner.suites.base import BaseSuite


base_pattern = re.compile(r'^.*\.|^.*:')

case_load_pattern = re.compile(r'^.*\:')
method_load_pattern = re.compile(r'^.*\:.*\..*')


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


def get_load_type(load_path):
    """
    Возвращает тип по которому определяется,
    какую стратегию загрузки выбрать

    :param load_path: строка с путем для загрузки
    """
    if not load_path:
        return

    if method_load_pattern.search(load_path) is not None:
        return METHOD_LOAD_TYPE

    if case_load_pattern.search(load_path) is not None:
        return CASE_LOAD_TYPE

    return SUITE_LOAD_TYPE


def create_map(suites):
    """
    Создает карту сопоставления имени suite к инстансу
    """
    mp = {}

    for suite in suites:
        mp[suite.name] = suite

    return mp


def get_suite_from_map(name, mp):
    """
    Возвращает suite по имени
    """
    try:
        return mp[name]
    except KeyError:
        raise CollectError(
            'Suite "{}" is not found'.format(name),
        )


def get_case_from_suite(case_name, suite):
    """
    Возвращает case из suite
    """
    try:
        return suite.get_map()[case_name]['cls']
    except KeyError:
        raise CollectError('TestCase "{}" is not found'.format(case_name))


class CollectSuites(object):
    """
    Класс выполняет работу по сборке suite
    """

    def __init__(self, load_path, suites, test_loader, nose_config):
        self._result = None
        self._suites = suites

        if base_pattern.search(load_path) is not None:
            self._load_type = get_load_type(load_path)
            self._load_path = load_path
            self._mp = create_map(suites)
        else:
            self._load_type = None
            self._load_path = None
            self._mp = None

        self._nose_config = nose_config
        self._test_loader = test_loader

    def _with_suite(self):
        """
        Собрать с указанной suite
        """
        suite = get_suite_from_map(self._load_path, self._mp)

        self._result = CollectResult(
            suite(self._nose_config, self._test_loader),
        )

    def _with_case(self):
        """
        Собрать с указанным TestCase классом
        """
        suite_name, case_name = self._load_path.split(':')
        app_suite = get_suite_from_map(suite_name, self._mp)

        case = get_case_from_suite(case_name, app_suite)

        suite = BaseSuite(config=self._nose_config)
        suite.addTests(
            self._test_loader.loadTestsFromTestCase(
                case.with_require(app_suite.require),
            ),
        )

        self._result = CollectResult(suite)

    def _with_method(self):
        """
        Собрать с указанным методом класса TestCase
        """
        suite_name, case_info = self._load_path.split(':')
        case_name, method_name = case_info.split('.')

        app_suite = get_suite_from_map(suite_name, self._mp)

        case = get_case_from_suite(case_name, app_suite)

        try:
            suite = BaseSuite(
                map(case.with_require(app_suite.require), [method_name]),
                config=self._nose_config,
            )
        except ValueError:
            raise CollectError(
                'Method "{}" of class "{}" is not found'.format(method_name, case_name)
            )

        self._result = CollectResult(suite)

    def make_result(self):
        """
        Выполнить сборку
        """
        if self._load_type is SUITE_LOAD_TYPE:
            self._with_suite()

        elif self._load_type is CASE_LOAD_TYPE:
            self._with_case()

        elif self._load_type is METHOD_LOAD_TYPE:
            self._with_method()

        if self._result:
            return self._test_loader.suiteClass(self._result)

        return self._test_loader.suiteClass(
            [
                suite(self._nose_config, self._test_loader)
                for suite in self._suites
            ],
        )
