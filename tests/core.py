# -*- coding: utf8 -*-

from unittest import TestCase


class TestClearExtensions(TestCase):
    """
    Set extension, check get extension, call clear, check raise
    """

    def runTest(self):
        from noseapp.core import extensions

        extensions.set('test', dict(test='test'))
        self.assertEqual(extensions.get('test').get('test'), 'test')

        extensions.clear()
        self.assertRaises(extensions.ExtensionNotFound, extensions.get, 'test')


class TestClassFactory(TestCase):
    """
    Test ClassFactory usage
    """

    def runTest(self):
        from noseapp.runner.base import BaseTestRunner
        from noseapp.core.constants import RunStrategy
        from noseapp.suite.bases.simple import BaseSuite
        from noseapp.suite.bases.threading_suite import ThreadSuite
        from noseapp.runner.threading_runner import ThreadingTestRunner
        from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner

        from noseapp.core.factory import ClassFactory

        class MockOptions(object):
            def __init__(self, **kw):
                self.run_strategy = kw.pop('run_strategy', RunStrategy.SIMPLE)
                self.async_suites = kw.pop('async_suites', 0)
                self.async_tests = kw.pop('async_tests', 0)

        factory = ClassFactory(MockOptions())

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, BaseTestRunner)

        factory = ClassFactory(MockOptions(async_suites=2))

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)

        factory = ClassFactory(MockOptions(async_suites=2, async_tests=2))

        self.assertEqual(factory.suite_class, ThreadSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)

        factory = ClassFactory(
            MockOptions(run_strategy=RunStrategy.MULTIPROCESSING, async_suites=2),
        )

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)

        factory = ClassFactory(
            MockOptions(run_strategy=RunStrategy.MULTIPROCESSING, async_suites=2, async_tests=2),
        )

        self.assertEqual(factory.suite_class, ThreadSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)

        factory = ClassFactory(
            MockOptions(run_strategy=RunStrategy.THREADING, async_suites=2),
        )

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, ThreadingTestRunner)

        factory = ClassFactory(
            MockOptions(run_strategy=RunStrategy.THREADING, async_suites=2, async_tests=2),
        )

        self.assertEqual(factory.suite_class, ThreadSuite)
        self.assertEqual(factory.runner_class, ThreadingTestRunner)

        try:  # if gevent installed only
            from noseapp.suite.bases.gevent_suite import GeventSuite
            from noseapp.runner.gevent_runner import GeventTestRunner

            factory = ClassFactory(
                MockOptions(run_strategy=RunStrategy.GEVENT, async_suites=2),
            )

            self.assertEqual(factory.suite_class, BaseSuite)
            self.assertEqual(factory.runner_class, GeventTestRunner)

            factory = ClassFactory(
                MockOptions(run_strategy=RunStrategy.GEVENT, async_suites=2, async_tests=2),
            )

            self.assertEqual(factory.suite_class, GeventSuite)
            self.assertEqual(factory.runner_class, GeventTestRunner)
        except ImportError:
            pass
