# -*- coding: utf-8 -*-

import os

from noseapp import NoseApp
from optparse import OptionGroup
from noseapp.case import TestCaseSettings

from example.ext.example import ExampleRandom


class FakePlugin(object):
    name = 'fake'


class FakePlugin2(object):
    name = 'fake2'


PLUGINS = None

CURRENT_CONFIG = os.getenv('NOSEAPP_CONFIG', 'base')
CONFIG_PATH = 'example.etc.{}'.format(CURRENT_CONFIG)


def create_app():
    path_to_suites = lambda folder: os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            folder,
        ),
    )

    app1 = ExampleTestApp.as_sub_app(
        'sub',
        config=CONFIG_PATH,
        plugins=PLUGINS,
    )
    app1.load_suites(path_to_suites('suites2'))

    app = ExampleTestApp.as_master_app(
        'master',
        # app1,
        config=CONFIG_PATH,
        plugins=PLUGINS,
    )
    app.load_suites(path_to_suites('suites'))
    return app


class ExampleTestApp(NoseApp):

    def setUpApp(self):
        # if self.is_sub_app:
        self.install_example_random()
        self.install_test_case_settings()

    def tearDownApp(self):
        print 'Hello Dolly'

    def install_example_random(self):
        ExampleRandom.install(self)

    def install_test_case_settings(self):
        TestCaseSettings(
            get_fail=self.options.get_fail,
        ).install(self)

    def addOptions(self, parser):
        if self.is_master_app:
            group = OptionGroup(parser, 'Example-test-app')

            group.add_option(
                '--get-fail',
                dest='get_fail',
                action='store_true',
                default=False,
                help='Get fail in result.'
            )

            parser.add_option_group(group)

    def setUp(self):
        print 'It is before of {}'.format(self)

    def tearDown(self):
        print 'It is after of {}'.format(self)
