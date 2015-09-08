# -*- coding: utf-8 -*-

from noseapp import Suite as BaseSuite

from example.app.case import TestCase


class Suite(BaseSuite):

    test_case_class = TestCase
