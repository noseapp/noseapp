# -*- coding: utf-8 -*-

from noseapp import Suite as BaseSuite

from example.app.case import TestCase


class Suite(BaseSuite):

    test_case_class = TestCase

    def setUp(self):
        print 'It is setUp of {}'.format(self)

    def tearDown(self):
        print 'it is terDown of {}'.format(self)
