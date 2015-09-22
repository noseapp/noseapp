# -*- coding: utf-8 -*-

from unittest import TestCase


class TestDefaultClasses(TestCase):
    """
    Test default classes in NoseApp class property
    """

    def runTest(self):
        from noseapp import NoseApp
        from noseapp.core import TestProgram
        from noseapp.app.config import Config
        from noseapp.core.factory import ClassFactory
        from noseapp.core.collector import CollectSuite

        self.assertEqual(NoseApp.config_class, Config)
        self.assertEqual(NoseApp.program_class, TestProgram)
        self.assertEqual(NoseApp.class_factory, ClassFactory)
        self.assertEqual(NoseApp.collector_class, CollectSuite)


class TestAppName(TestCase):

    def runTest(self):
        from noseapp import NoseApp

        app = NoseApp('hello')
        self.assertEqual(app.name, 'hello')
