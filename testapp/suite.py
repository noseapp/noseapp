# -*- coding: utf-8 -*-

from noseapp import Suite

from testapp.case import MyTestCase


class MySuite(Suite):

    DEFAULT_REQUIRE = [
        'settings',
        'self_test',
    ]

    test_case_class = MyTestCase

    def setUp(self):
        self.ext('self_test').setup_suite_context_called = True

    def tearDown(self):
        self.ext('self_test').teardown_suite_context_called = True
