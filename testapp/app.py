# -*- coding: utf-8 -*-

import os

from noseapp import NoseApp
from noseapp.case import TestCaseSettings

from testapp.self_test import SelfTestEx


BASE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__name__),
        'testapp',
    ),
)


def get_full_path(*args):
    return os.path.join(BASE_PATH, *args)


def create_app(config='base', **kwargs):
    sub_app = TestApp.as_sub_app('sub')
    assert sub_app.is_sub_app

    master_app = TestApp.as_master_app(
        'master',
        sub_app,
        config='testapp.etc.{}'.format(config),
        **kwargs
    )
    assert master_app.is_master_app
    assert len(master_app.sub_apps) == 1

    master_app.load_suites(get_full_path('suites'))

    return master_app


class TestApp(NoseApp):

    def __init__(self, *args, **kwargs):
        self.self_test = SelfTestEx()
        self.shared_extension(cls=self.self_test)

        super(TestApp, self).__init__(*args, **kwargs)

    def setUpApp(self):
        self.self_test.setup_app_called = True

        settings = TestCaseSettings(
            debug=False,
            other_flag=False,
        )
        settings.install(self)

    def tearDownApp(self):
        self.self_test.teardown_app_called = True

    def setUp(self):
        self.self_test.setup_app_context_called = True

    def tearDown(self):
        self.self_test.teardown_app_context_called = True

    def addOptions(self, parser):
        self.self_test.add_options_called = True
