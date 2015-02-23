# -*- coding: utf-8 -*-

from unittest import TestCase


class TestModifyDict(TestCase):
    """
    Test noseapp.datastructures.ModifyDict class
    """

    def runTest(self):
        from noseapp.datastructures import ModifyDict

        dct = ModifyDict(test=1)

        self.assertIn('test', dct)
        self.assertEqual(dct['test'], 1)
        self.assertEqual(dct.get('none'), None)

        dct.hello = 'world'

        self.assertEqual(dct.hello, 'world')

        self.assertRaises(AttributeError, lambda: dct.no_attr)
