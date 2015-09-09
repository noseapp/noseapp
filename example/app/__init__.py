# -*- coding: utf-8 -*-

import os

from noseapp import NoseApp
from optparse import OptionGroup
from noseapp.case import TestCaseSettings

from example.ext.example import ExampleRandom


PLUGINS = None

CURRENT_CONFIG = os.getenv('NOSEAPP_CONFIG', 'base')
CONFIG_PATH = 'example.etc.{}'.format(CURRENT_CONFIG)


def create_app():
    path_to_suites = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'suites',
        ),
    )

    app1 = ExampleTestApp(
        config=CONFIG_PATH,
        plugins=PLUGINS,
        is_sub_app=True,
    )
    app1.load_suites(path_to_suites)

    app = ExampleTestApp(
        config=CONFIG_PATH,
        plugins=PLUGINS,
        sub_apps=[app1],
    )
    app.load_suites(path_to_suites)
    return app


class ExampleTestApp(NoseApp):

    def initialize(self):
        if self.is_sub_app:
            self.install_example_random()
            self.install_test_case_settings()

    def install_example_random(self):
        ExampleRandom.install(self)

    def install_test_case_settings(self):
        TestCaseSettings(
            get_fail=self.options.get_fail,
        ).install(self)

    def add_options(self, parser):
        group = OptionGroup(parser, 'Example-test-app')

        group.add_option(
            '--get-fail',
            dest='get_fail',
            action='store_true',
            default=False,
            help='Get fail in result.'
        )

        parser.add_option_group(group)
