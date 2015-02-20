# -*- coding: utf-8 -*-

import re

from noseapp.runner.suites.base import BaseSuite
from noseapp.utils.collector import exec_suite_info


base_pattern = re.compile(r'^.*\.|^.*:')

case_load_pattern = re.compile(r'^.*\:')
method_load_pattern = re.compile(r'^.*\:.*\..*')


CASE_COLLECT_STRATEGY = 'case'
SUITE_COLLECT_STRATEGY = 'suite'
METHOD_COLLECT_STRATEGY = 'method'


class CollectError(BaseException):
    pass


class CollectResult(list):

    def __init__(self, suite):
        super(CollectResult, self).__init__([suite])


def get_collect_strategy(load_path):
    if not load_path:
        return

    if method_load_pattern.search(load_path) is not None:
        return METHOD_COLLECT_STRATEGY

    if case_load_pattern.search(load_path) is not None:
        return CASE_COLLECT_STRATEGY

    return SUITE_COLLECT_STRATEGY


def create_map(suites):
    mp = {}

    for suite in suites:
        mp[suite.name] = suite

    return mp


def get_suite_from_map(name, mp):
    try:
        return mp[name]
    except KeyError:
        raise CollectError(
            'Suite "{}" is not found'.format(name),
        )


def get_case_from_suite(case_name, suite):
    try:
        return suite.get_map()[case_name]['cls']
    except KeyError:
        raise CollectError('TestCase "{}" is not found'.format(case_name))


class CollectSuites(object):
    """
    Collect suite for test runner
    """

    def __init__(self, argv, suites, test_loader, nose_config):
        if nose_config.options.ls:
            exec_suite_info(suites, show_docs=nose_config.options.doc)

        load_path = argv[1] if len(argv) > 2 else ''

        self._result = None
        self._suites = suites

        if load_path and base_pattern.search(load_path) is not None:
            self._strategy = get_collect_strategy(load_path)
            self._load_path = load_path
            self._mp = create_map(suites)
        else:
            self._strategy = None
            self._load_path = None
            self._mp = None

        self._nose_config = nose_config
        self._test_loader = test_loader

    def _by_suite_strategy(self):
        suite = get_suite_from_map(self._load_path, self._mp)

        self._result = CollectResult(
            suite(self._nose_config, self._test_loader),
        )

    def _by_case_strategy(self):
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

    def _by_method_strategy(self):
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
        if self._strategy is SUITE_COLLECT_STRATEGY:
            self._by_suite_strategy()

        elif self._strategy is CASE_COLLECT_STRATEGY:
            self._by_case_strategy()

        elif self._strategy is METHOD_COLLECT_STRATEGY:
            self._by_method_strategy()

        if self._result:
            return self._test_loader.suiteClass(self._result)

        return self._test_loader.suiteClass(
            [
                suite(self._nose_config, self._test_loader)
                for suite in self._suites
            ],
        )
