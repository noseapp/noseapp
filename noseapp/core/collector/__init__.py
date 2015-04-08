# -*- coding: utf-8 -*-

import re

from noseapp.core.collector import console
from noseapp.suite.bases.simple import BaseSuite


CASE_COLLECT_STRATEGY = 'case'
BASIC_COLLECT_STRATEGY = 'basic'
SUITE_COLLECT_STRATEGY = 'suite'
METHOD_COLLECT_STRATEGY = 'method'

COLLECTOR_COMMAND_PATTERN = re.compile(r'^.*\.|^.*:')
COLLECT_CASE_COMMAND_PATTERN = re.compile(r'^.*\:')
COLLECT_METHOD_COMMAND_PATTERN = re.compile(r'^.*\:.*\..*')


class CollectError(BaseException):
    pass


def get_collector_strategy(command):
    if command and COLLECTOR_COMMAND_PATTERN.search(command) is not None:

        if COLLECT_METHOD_COMMAND_PATTERN.search(command) is not None:
            return METHOD_COLLECT_STRATEGY

        if COLLECT_CASE_COMMAND_PATTERN.search(command) is not None:
            return CASE_COLLECT_STRATEGY

        return SUITE_COLLECT_STRATEGY

    return BASIC_COLLECT_STRATEGY


def get_suite_by_name(name, suites):
    for suite in suites:

        if suite.name == name:
            return suite

    else:
        raise CollectError(
            'Suite "{}" is not found'.format(name),
        )


def get_case_from_suite(case_name, suite):
    try:
        return suite.get_map()[case_name]['cls']
    except KeyError:
        raise CollectError('TestCase "{}" is not found'.format(case_name))


class CollectSuite(object):
    """
    Collect suite for test runner
    """

    def __init__(self, argv, suites, test_loader, class_factory, nose_config):
        if nose_config.options.ls:
            console.tree(suites, show_docs=nose_config.options.doc)

        self._suites = suites
        self._nose_config = nose_config
        self._test_loader = test_loader
        self._class_factory = class_factory

        if nose_config.options.run_test:
            self._command = nose_config.options.run_test
        elif len(argv) > 2:
            self._command = argv[1]
        else:
            self._command = None

    @property
    def command(self):
        return self._command

    @property
    def suites(self):
        return self._suites

    @property
    def collect(self):  # sugar of syntax :)
        strategy_to_method = {
            CASE_COLLECT_STRATEGY: self._collect_by_case_strategy,
            BASIC_COLLECT_STRATEGY: self._collect_by_basic_strategy,
            SUITE_COLLECT_STRATEGY: self._collect_by_suite_strategy,
            METHOD_COLLECT_STRATEGY: self._collect_by_method_strategy,
        }

        return strategy_to_method[get_collector_strategy(self._command)]

    def make_result(self):
        return self._test_loader.suiteClass(
            self.collect(),
        )

    def _collect_by_basic_strategy(self):
        return [
            suite(self._nose_config, self._test_loader, self._class_factory)
            for suite in self._suites
        ]

    def _collect_by_suite_strategy(self):
        suite = get_suite_by_name(self._command, self._suites)

        return [suite(self._nose_config, self._test_loader, self._class_factory)]

    def _collect_by_case_strategy(self):
        suite_name, case_name = self._command.split(':')

        app_suite = get_suite_by_name(suite_name, self._suites)
        app_suite.init_extensions()

        case = get_case_from_suite(case_name, app_suite)

        suite = BaseSuite(
            config=self._nose_config,
            handlers=app_suite.handlers,
        )
        suite.addTests(
            self._test_loader.loadTestsFromTestCase(case),
        )

        return [suite]

    def _collect_by_method_strategy(self):
        suite_name, case_info = self._command.split(':')
        case_name, method_name = case_info.split('.')

        app_suite = get_suite_by_name(suite_name, self._suites)
        app_suite.init_extensions()

        case = get_case_from_suite(case_name, app_suite)

        try:
            suite = BaseSuite(
                tests=map(case, [method_name]),
                config=self._nose_config,
                handlers=app_suite.handlers,
            )
        except ValueError:
            raise CollectError(
                'Method "{}" of class "{}" is not found'.format(method_name, case_name)
            )

        return [suite]
