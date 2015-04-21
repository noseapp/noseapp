# -*- coding: utf-8 -*-

from unittest import TestCase

from noseapp import NoseApp as _NoseApp


class NoseApp(_NoseApp):

    def initialize(self):
        pass


class TestInitExtensions(TestCase):
    """
    Test init extension without share
    """

    @staticmethod
    def create_fake_extension():

        class FakeExtension(object):

            name = 'test'

        return FakeExtension

    def runTest(self):
        from noseapp import TestCase
        from noseapp.core.extensions import ExtensionNotFound

        app = NoseApp()
        ex_cls = self.create_fake_extension()
        app.shared_extension(cls=ex_cls)

        TestCase.setup_extensions(require=['test'])

        self.assertTrue(hasattr(TestCase, 'test'))
        self.assertIsInstance(TestCase.test, ex_cls)
        self.assertRaises(ExtensionNotFound, TestCase.setup_extensions, require=['no_ex'])


class TestScreenPlayCase(TestCase):
    """
    Test noseapp.case.ScreenPlayCase class
    TODO: Test flows
    """

    @staticmethod
    def create_test_class():
        from noseapp.case import step
        from noseapp import ScreenPlayCase

        class StepByStep(ScreenPlayCase):

            def begin(self):
                self.counter = 0

            @step(1)
            def step_one(self):
                self.counter += 1

            @step(2)
            def step_two(self):
                self.counter += 1

            def finalize(self):
                self.counter += 1

        return StepByStep

    def runTest(self):
        from noseapp.case.screenplay import ScreenPlayCaseMeta

        case_cls = self.create_test_class()

        self.assertEqual(case_cls.FLOWS, None)
        self.assertEqual(case_cls.USE_PROMPT, False)
        self.assertEqual(case_cls.__metaclass__, ScreenPlayCaseMeta)

        case = case_cls(methodName='runTest')

        self.assertTrue(hasattr(case, 'runTest'))

        case.runTest()

        self.assertEqual(case.counter, 3)
