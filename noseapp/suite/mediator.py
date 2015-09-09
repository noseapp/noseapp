# -*- coding: utf-8 -*-

from functools import wraps

from noseapp.core import loader


class SuiteMediator(object):
    """
    Mediator class between noseapp.suite.base.Suite and nose.suite.ContextSuite
    """

    def __init__(self, context):
        """
        :type require: list
        :type context: noseapp.suite.context.SuiteContext
        """
        self.__context = context

    @property
    def context(self):
        return self.__context

    @property
    def test_cases(self):
        return self.__context.test_cases

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

        for case in self.__context.test_cases:
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
        self.__context.add_test_case(test_case)

    def add_handler(self, f):
        """
        Add run test handler
        """
        self.__context.add_handler(f)
        return wraps(f)

    def add_setup(self, f):
        """
        Add setup suite callback
        """
        self.__context.add_setup(f)
        return wraps(f)

    def add_teardown(self, f):
        """
        Add teardown callback
        """
        self.__context.add_teardown(f)
        return wraps(f)

    def create_suite(self,
                     program_data,
                     shuffle=None,
                     case_name=None,
                     method_name=None):
        """
        Create suite instance
        """
        if callable(shuffle):
            shuffle(self.__context.test_cases)

        def make_suites():
            suites = []

            if case_name:
                case = loader.load_case_from_suite(case_name, self)
                tests = loader.load_tests_from_test_case(
                    case.setup_extensions(self.__context.require),
                    method_name=method_name,
                )

                suites.append(
                    program_data.suite_class(
                        tests,
                        context=case,
                        config=program_data.config,
                        handlers=self.__context.handlers,
                    ),
                )
            else:
                for case in self.__context.test_cases:
                    tests = loader.load_tests_from_test_case(
                        case.setup_extensions(self.__context.require),
                    )

                    suites.append(
                        program_data.suite_class(
                            tests,
                            context=case,
                            config=program_data.config,
                            handlers=self.__context.handlers,
                        ),
                    )

            return suites

        return program_data.suite_class(
            make_suites(),
            context=self.__context,
            config=program_data.config,
        )
