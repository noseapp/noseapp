# -*- coding: utf-8 -*-

from unittest import TestCase


class TestPushApp(TestCase):
    """
    Test push app with call plugin instance
    """

    def runTest(self):
        from noseapp import AppPlugin

        plugin = AppPlugin()
        self.assertFalse(hasattr(plugin, 'app'))

        instance = plugin(object())
        self.assertIsInstance(instance, AppPlugin)
        self.assertTrue(hasattr(plugin, 'app'))
        self.assertIsInstance(plugin.app, object)
