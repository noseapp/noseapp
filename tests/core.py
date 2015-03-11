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
