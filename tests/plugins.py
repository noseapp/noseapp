# -*- coding: utf-8 -*-

from unittest import TestCase


class TestPushApp(TestCase):
    """
    Test push app with call plugin instance
    """

    def runTest(self):
        from noseapp import NoseApp
        from noseapp import AppPlugin

        plugin = AppPlugin()
        self.assertIsNone(plugin.app)

        plugin.init_app(NoseApp('test'))
        self.assertIsInstance(plugin, AppPlugin)
        self.assertIsInstance(plugin.app, NoseApp)
