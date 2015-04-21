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
        from noseapp.suite.bases.simple import BaseSuite
        from noseapp.suite.bases.threading_suite import ThreadSuite
        from noseapp.runner.threading_runner import ThreadingTestRunner
        from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner

        from noseapp.core.factory import ClassFactory

        class MockOptions(object):
            def __init__(self, **kw):
                self.thread_pool = kw.pop('thread_pool', 0)
                self.app_processes = kw.pop('app_processes', 0)
                self.gevent_greenlets = kw.pop('gevent_greenlets', 0)
                self.gevent_pool = kw.pop('gevent_pool', 0)

        factory = ClassFactory(MockOptions())

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, BaseTestRunner)

        factory = ClassFactory(MockOptions(app_processes=2))

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)

        factory = ClassFactory(MockOptions(thread_pool=2))

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, ThreadingTestRunner)

        factory = ClassFactory(MockOptions(app_processes=2, thread_pool=2))

        self.assertEqual(factory.suite_class, ThreadSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)

        factory = ClassFactory(MockOptions(app_processes=2, gevent_greenlets=2))

        self.assertEqual(factory.suite_class, BaseSuite)
        self.assertEqual(factory.runner_class, MultiprocessingTestRunner)
