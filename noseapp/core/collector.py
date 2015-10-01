# -*- coding: utf-8 -*-

import re
import logging
from random import Random

from noseapp.core import loader
from noseapp.tools import output


logger = logging.getLogger(__name__)


CASE_COLLECT_STRATEGY = 'case'
BASIC_COLLECT_STRATEGY = 'basic'
SUITE_COLLECT_STRATEGY = 'suite'
METHOD_COLLECT_STRATEGY = 'method'

COLLECTOR_COMMAND_PATTERN = re.compile(r'^.*\.|^.*:')
COLLECT_CASE_COMMAND_PATTERN = re.compile(r'^.*\:')
COLLECT_METHOD_COMMAND_PATTERN = re.compile(r'^.*\:.*\..*')


def get_command(program_data):
    """
    Get command to collect of program data

    :type program_data: noseapp.core.program.ProgramData
    """
    if program_data.config.options.run_test:
        return program_data.config.options.run_test

    if len(program_data.argv) > 2:
        return program_data.argv[1]

    return None


def get_strategy(command):
    """
    Get strategy by command

    :param command: command to collect
    :type command: str or None
    """
    if command and COLLECTOR_COMMAND_PATTERN.search(command) is not None:

        if COLLECT_METHOD_COMMAND_PATTERN.search(command) is not None:
            return METHOD_COLLECT_STRATEGY

        if COLLECT_CASE_COMMAND_PATTERN.search(command) is not None:
            return CASE_COLLECT_STRATEGY

        return SUITE_COLLECT_STRATEGY

    return BASIC_COLLECT_STRATEGY


class CollectSuite(object):
    """
    Collect suite to run.
    """

    def __init__(self, program_data):
        """
        :type program_data: noseapp.core.program.ProgramData
        """
        if program_data.config.options.ls:
            output.tree(program_data.suites, show_docs=program_data.config.options.doc)

        self.__program_data = program_data
        self.__command = get_command(self.__program_data)
        self.__strategy = get_strategy(self.__command)

    @property
    def command(self):
        """
        Command to collect
        """
        return self.__command

    @property
    def strategy(self):
        """
        Strategy to collect
        """
        return self.__strategy

    @property
    def program_data(self):
        """
        :rtype: noseapp.core.program.ProgramData
        """
        return self.__program_data

    def collect_by_basic_strategy(self):
        """
        Basic collect without rules
        """
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

    def collect_by_suite_strategy(self):
        """
        Collect suite from command
        """
        suite = loader.load_suite_by_name(
            self.__command,
            self.__program_data.suites,
        )

        return [suite(self.__program_data)]

    def collect_by_case_strategy(self):
        """
        Collect case of suite from command
        """
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

    def collect_by_method_strategy(self):
        """
        Collect case method of suite from command
        """
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
    def collect(self):
        """
        Collect main
        """
        strategy_to_method = {
            CASE_COLLECT_STRATEGY: self.collect_by_case_strategy,
            BASIC_COLLECT_STRATEGY: self.collect_by_basic_strategy,
            SUITE_COLLECT_STRATEGY: self.collect_by_suite_strategy,
            METHOD_COLLECT_STRATEGY: self.collect_by_method_strategy,
        }

        logger.debug('Strategy for collect suites is "%s"', self.__strategy)

        return strategy_to_method[self.__strategy]


def collect(program_data, collector_class=CollectSuite):
    """
    Function is wrapper for calling to collector class
    """
    collector = collector_class(program_data)

    return program_data.suite_class(
        collector.collect(),
        config=program_data.config,
        context=program_data.context,
    )
