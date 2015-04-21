# -*- coding: utf-8 -*-

from functools import wraps


class TestCaseMediator(object):
    """
    Mediator class between noseapp.suite.Suite, TestLoader, TestSuite,
    TestCase. Provides between TestCase->TestLoader->TestSuite.
    """

    def __init__(self, require):
        self._test_cases = []
        self._require = require
        self._handlers = []

    @property
    def require(self):
        return self._require

    @property
    def test_cases(self):
        return self._test_cases

    @property
    def handlers(self):
        return self._handlers

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

        :return: dict
        """
        mp = {}

        for case in self._test_cases:
            mp[case.__name__] = {
                'cls': case,
                'tests': dict(
                    (atr, getattr(case, atr))
                    for atr in dir(case)
                    if atr.startswith('test')
                    or
                    atr.startswith('runTest'),
                ),
            }

        return mp

    def create_suite(self, program_data):
        """
        Create suite instance
        """
        suite = program_data.suite_class(
            config=program_data.config,
            handlers=self._handlers,
        )

        for case in self._test_cases:
            suite.addTests(
                program_data.test_loader.loadTestsFromTestCase(
                    case.setup_extensions(self._require),
                ),
            )

        return suite

    def add_test_case(self, test_case):
        """
        Remember test case class
        """
        self._test_cases.append(test_case)

    def add_handler(self, f):
        """
        Add run test handler
        """
        self._handlers.append(f)
        return wraps(f)
