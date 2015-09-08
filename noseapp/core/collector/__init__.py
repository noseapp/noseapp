# -*- coding: utf-8 -*-

import re
import logging
from random import Random

from noseapp.core import loader
from noseapp.core.collector import console


logger = logging.getLogger(__name__)


CASE_COLLECT_STRATEGY = 'case'
BASIC_COLLECT_STRATEGY = 'basic'
SUITE_COLLECT_STRATEGY = 'suite'
METHOD_COLLECT_STRATEGY = 'method'

COLLECTOR_COMMAND_PATTERN = re.compile(r'^.*\.|^.*:')
COLLECT_CASE_COMMAND_PATTERN = re.compile(r'^.*\:')
COLLECT_METHOD_COMMAND_PATTERN = re.compile(r'^.*\:.*\..*')


def get_command(program_data):
    if program_data.config.options.run_test:
        return program_data.config.options.run_test

    if len(program_data.argv) > 2:
        return program_data.argv[1]

    return None


def get_strategy(command):
    if command and COLLECTOR_COMMAND_PATTERN.search(command) is not None:

        if COLLECT_METHOD_COMMAND_PATTERN.search(command) is not None:
            return METHOD_COLLECT_STRATEGY

        if COLLECT_CASE_COMMAND_PATTERN.search(command) is not None:
            return CASE_COLLECT_STRATEGY

        return SUITE_COLLECT_STRATEGY

    return BASIC_COLLECT_STRATEGY


class CollectSuite(object):
    """
    Collect suite for test runner
    """

    def __init__(self, program_data):
        if program_data.config.options.ls:
            console.tree(program_data.suites, show_docs=program_data.config.options.doc)

        self.__program_data = program_data
        self.__command = get_command(self.__program_data)
        self.__strategy = get_strategy(self.__command)

    def __collect_by_basic_strategy__(self):
        kwargs = {}

        if self.__program_data.config.options.random:
            random = Random(
                self.__program_data.config.options.random_seed,
            )
            random.shuffle(self.__program_data.suites)

            kwargs.update(shuffle=random.shuffle)

        return [
            suite(
                self.__program_data,
                **kwargs
            )
            for suite in self.__program_data.suites
        ]

    def __collect_by_suite_strategy__(self):
        suite = loader.load_suite_by_name(
            self.__command,
            self.__program_data.suites,
        )

        return [suite(self.__program_data)]

    def __collect_by_case_strategy__(self):
        suite_name, case_name = self.__command.split(':')
        suite = loader.load_suite_by_name(
            suite_name,
            self.__program_data.suites,
        )

        return [
            suite(
                self.__program_data,
                case_name=case_name,
            ),
        ]

    def __collect_by_method_strategy__(self):
        suite_name, case_info = self.__command.split(':')
        case_name, method_name = case_info.split('.')
        suite = loader.load_suite_by_name(
            suite_name,
            self.__program_data.suites,
        )

        return [
            suite(
                self.__program_data,
                case_name=case_name,
                method_name=method_name,
            ),
        ]

    @property
    def command(self):
        return self.__command

    @property
    def strategy(self):
        return self.__strategy

    @property
    def program_data(self):
        return self.__program_data

    @property
    def collect(self):
        strategy_to_method = {
            CASE_COLLECT_STRATEGY: self.__collect_by_case_strategy__,
            BASIC_COLLECT_STRATEGY: self.__collect_by_basic_strategy__,
            SUITE_COLLECT_STRATEGY: self.__collect_by_suite_strategy__,
            METHOD_COLLECT_STRATEGY: self.__collect_by_method_strategy__,
        }

        logger.debug('Strategy for collect suites is "%s"', self.__strategy)

        return strategy_to_method[self.__strategy]


def collect(program_data, collector_class=CollectSuite):
    """
    Function is wrapper for calling to collector class
    """
    collector = collector_class(program_data)
    return collector.collect()
