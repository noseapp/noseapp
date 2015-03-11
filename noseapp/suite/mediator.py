# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger(__name__)


def get_suite_class(options):
    if not options.app_processes and options.gevent_greanlets:
        from noseapp.suite.bases.gevent_suite import GeventSuite
        return GeventSuite

    elif options.app_processes and options.thread_pool:
        from noseapp.suite.bases.threading_suite import ThreadSuite
        return ThreadSuite

    from noseapp.suite.bases.simple import BaseSuite
    return BaseSuite


class TestCaseMediator(object):
    """
    Mediator class between noseapp.suite.Suite, TestLoader, TestSuite,
    TestCase. Provides between TestCase->TestLoader->TestSuite.
    """

    def __init__(self, require):
        self._test_cases = []
        self._require = require

    @property
    def test_cases(self):
        return self._test_cases

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

    def create_suite(self, nose_config, test_loader):
        """
        Create suite instance
        """
        suite_class = get_suite_class(nose_config.options)
        suite = suite_class(config=nose_config)

        for case in self._test_cases:
            suite.addTests(
                test_loader.loadTestsFromTestCase(
                    case.with_require(self._require),
                ),
            )

        return suite

    def add_test_case(self, test_case):
        self._test_cases.append(test_case)
