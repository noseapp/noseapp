# -*- coding: utf-8 -*-

import os
from unittest import TestCase

from noseapp import Suite
from noseapp.core import extensions
from noseapp.app import NoseApp as _NoseApp


class NoseApp(_NoseApp):

    def initialize(self):
        pass


class TestDefaultClasses(TestCase):
    """
    Test default classes in NoseApp class property
    """

    def runTest(self):
        from noseapp.core import TestProgram
        from noseapp.app.config import Config
        from noseapp.core.factory import ClassFactory
        from noseapp.core.collector import CollectSuite

        self.assertEqual(NoseApp.config_class, Config)
        self.assertEqual(NoseApp.program_class, TestProgram)
        self.assertEqual(NoseApp.class_factory, ClassFactory)
        self.assertEqual(NoseApp.collector_class, CollectSuite)


class TestInitializeCallback(TestCase):
    """
    Test call initialize callback
    """

    def create_fake_app(self):

        class FakeApp(NoseApp):

            def initialize(self):
                self.initialize_data = 1

        return FakeApp()

    def runTest(self):
        fake_app = self.create_fake_app()
        self.assertEqual(fake_app.initialize_data, 1)


class TestBeforeAfterCallback(TestCase):
    """
    Test call before and after callbacks
    """

    def create_fake_app(self):

        class FakeApp(NoseApp):

            def before(self):
                self.before_data = 1

            def after(self):
                self.after_data = 2

        return FakeApp()

    @staticmethod
    def mock_test_runner():
        import noseapp.core.program

        def get_test_runner_class(options):

            class FakeResult(object):

                def wasSuccessful(self):
                    return True

            class FakeTestRunner(object):

                def __init__(self, *args, **kwargs):
                    pass

                def run(self, suites):
                    return FakeResult()

            return FakeTestRunner

        noseapp.core.program.get_test_runner_class = get_test_runner_class

    def runTest(self):
        self.mock_test_runner()

        fake_app = self.create_fake_app()

        try:
            fake_app.run()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

        self.assertEqual(fake_app.before_data, 1)
        self.assertEqual(fake_app.after_data, 2)


class TestRegisterOneSuite(TestCase):
    """
    Register one suite in application
    """

    def runTest(self):
        suite = Suite(__name__)
        app = NoseApp()

        app.register_suite(suite)

        self.assertEqual(len(app.suites), 1)
        self.assertIsInstance(app.suites[0], Suite)


class TestRegisterListSuites(TestCase):
    """
    Register list suites in application
    """

    def runTest(self):
        suites = [Suite(__name__) for _ in xrange(10)]
        app = NoseApp()

        app.register_suites(suites)

        self.assertEqual(len(app.suites), 10)

        for suite in app.suites:
            self.assertIsInstance(suite, Suite)


class TestLoadSuites(TestCase):
    """
    Test auto load suites
    """

    def runTest(self):
        dir_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'fake_suites',
            ),
        )
        app = NoseApp()

        app.load_suites(dir_path)

        self.assertEqual(len(app.suites), 4)

        for suite in app.suites:
            self.assertIsInstance(suite, Suite)


class TestSharedExtension(TestCase):
    """
    Test shared extension in application
    """

    @staticmethod
    def get_fake_ex():

        class ExampleExtension(object):
            name = 'example'

            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        return ExampleExtension

    def test_shared_by_name(self):
        ex = self.get_fake_ex()
        app = NoseApp()

        app.shared_extension(name='test', cls=ex)

        self.assertIsInstance(extensions.get('test'), ex)

    def test_shared_by_class_name(self):
        ex = self.get_fake_ex()
        app = NoseApp()

        app.shared_extension(cls=ex)

        self.assertIsInstance(extensions.get(ex.name), ex)

    def test_shared_with_args_kwargs(self):
        ex = self.get_fake_ex()
        app = NoseApp()

        app.shared_extension(cls=ex, args=(1, 2), kwargs={'test': 'test'})

        get_ex = extensions.get(ex.name)

        self.assertIsInstance(get_ex, ex)
        self.assertEqual(len(get_ex.args), 2)
        self.assertEqual(get_ex.kwargs.get('test'), 'test')

    def test_shared_data(self):
        data = {'test': 'test'}

        app = NoseApp()
        app.shared_data('test_data', data)

        get_data = extensions.get('test_data')

        self.assertEqual(get_data.get('test'), 'test')

        get_data['test'] = 1

        self.assertEqual(data.get('test'), 'test')

    def test_raises(self):
        from noseapp.core.extensions import ExtensionNotFound

        ex = self.get_fake_ex()
        app = NoseApp()

        delattr(ex, 'name')

        self.assertRaises(AttributeError, app.shared_extension, cls=ex)
        self.assertRaises(ExtensionNotFound, extensions.get, 'no_ex')


class TestInitConfig(TestCase):
    """
    Test init app configuration
    """

    def test_config_from_module(self):
        from noseapp.core.program import TestProgram

        app = NoseApp()
        app.config.from_module('noseapp.core.program')

        self.assertEqual(app.config.TestProgram, TestProgram)

    def test_config_from_py_file(self):
        path = os.path.abspath(
            os.path.join(
              os.path.dirname(__file__),
              'fake_suites',
              'one.py',
            ),
        )
        app = NoseApp()
        app.config.from_py_file(path)

        self.assertIsInstance(app.config.suite1, Suite)
