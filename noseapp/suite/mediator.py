# -*- coding: utf-8 -*-

from functools import wraps

from noseapp.core import loader


class SuiteMediator(object):
    """
    Mediator class between noseapp.suite.base.Suite and nose.suite.ContextSuite
    """

    def __init__(self, require):
        self.__require = require

        self.__setup = []
        self.__teardown = []
        self.__handlers = []
        self.__test_cases = []

    @property
    def require(self):
        return self.__require

    @property
    def handlers(self):
        return self.__handlers

    @property
    def test_cases(self):
        return self.__test_cases

    def create_map(self):
        """
        {
            'class name': {
                'cls': 'link to class object',
                'tests': {
                    'method name': 'link to class method',
                },
            },
        }

        :rtype: dict
        """
        mp = {}

        for case in self.__test_cases:
            mp[case.__name__] = {
                'cls': case,
                'tests': dict(
                    (atr, getattr(case, atr))
                    for atr in dir(case)
                    if atr.startswith(loader.TEST_NAME_PREFIX)
                    or
                    atr == loader.DEFAULT_TEST_NAME,
                ),
            }

        return mp

    def add_test_case(self, test_case):
        """
        Remember test case class
        """
        self.__test_cases.append(test_case)

    def add_handler(self, f):
        """
        Add run test handler
        """
        self.__handlers.append(f)
        return wraps(f)

    def add_setup(self, f):
        """
        Add setup suite callback
        """
        self.__setup.append(f)
        return wraps(f)

    def add_teardown(self, f):
        """
        Add teardown callback
        """
        self.__teardown.append(f)
        return wraps(f)

    def setup(self):
        """
        Callback for nose context
        """
        for callback in self.__setup:
            callback()

    def teardown(self):
        """
        Callback for nose context
        """
        for callback in self.__teardown:
            callback()

    def create_suite(self,
                     program_data,
                     shuffle=None,
                     case_name=None,
                     method_name=None):
        """
        Create suite instance
        """
        if callable(shuffle):
            shuffle(self.__test_cases)

        def make_suites():
            suites = []

            if case_name:
                case = loader.load_case_from_suite(case_name, self)
                tests = loader.load_tests_from_test_case(
                    case.setup_extensions(self.__require),
                    method_name=method_name,
                )

                suites.append(
                    program_data.suite_class(
                        tests,
                        context=case,
                        handlers=self.__handlers,
                        config=program_data.config,
                    ),
                )
            else:
                for case in self.__test_cases:
                    tests = loader.load_tests_from_test_case(
                        case.setup_extensions(self.__require),
                    )

                    suites.append(
                        program_data.suite_class(
                            tests,
                            context=case,
                            handlers=self.__handlers,
                            config=program_data.config,
                        ),
                    )

            return suites

        return program_data.suite_class(
            make_suites(),
            context=self,
            config=program_data.config,
        )
