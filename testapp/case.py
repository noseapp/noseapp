# -*- coding: utf-8 -*-

from noseapp import ScreenPlayCase

from testapp.self_test import SelfTestEx


class MyTestCase(ScreenPlayCase):

    @classmethod
    def setUpClass(cls):
        SelfTestEx.setup_case_class_called = True

    @classmethod
    def tearDownClass(cls):
        SelfTestEx.teardown_case_class_called = True

    def setUp(self):
        self.ext('self_test').setup_case_called = True

    def tearDown(self):
        self.ext('self_test').teardown_case_called = True
