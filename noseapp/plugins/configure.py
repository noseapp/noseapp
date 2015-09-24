
import os
import time
from optparse import OptionGroup

from noseapp.plugins.base import AppPlugin
from noseapp.app.context import app_callback
from noseapp.core.constants import RunStrategy


class AppConfigurePlugin(AppPlugin):

    name = 'app-configure'

    def options(self, parser, env=os.environ):
        super(AppConfigurePlugin, self).options(parser, env=env)

        group = OptionGroup(parser, 'NoseApp base options')

        group.add_option(
            '--run-strategy',
            dest='run_strategy',
            default=RunStrategy.SIMPLE,
            type=str,
            help='Can be in ({})'.format(', '.join(RunStrategy.ALL)),
        )
        group.add_option(
            '--async-suites',
            dest='async_suites',
            default=0,
            type=int,
            help='Number of suites to async run.',
        )
        group.add_option(
            '--async-tests',
            dest='async_tests',
            default=0,
            type=int,
            help='Number of tests to async run. Limit to tests within suite.',
        )
        group.add_option(
            '--multiprocessing-timeout',
            dest='multiprocessing_timeout',
            default=1800,
            type=int,
            help='Process timeout. To multiprocessing strategy only.',
        )
        group.add_option(
            '--ls',
            dest='ls',
            action='store_true',
            default=False,
            help='Show suites tree.',
        )
        group.add_option(
            '--doc',
            dest='doc',
            action='store_true',
            default=False,
            help='Show docstring of test cases. To --ls option only.',
        )
        group.add_option(
            '-t', '--test',
            dest='run_test',
            default='',
            type=str,
            help='Run test case or suite by name.',
        )
        group.add_option(
            '--random',
            dest='random',
            action='store_true',
            default=False,
            help='Get running within random shuffle',
        )
        group.add_option(
            '--random-seed',
            dest='random_seed',
            default=int(time.time()),
            type=int,
            help='Seed of random shuffle. To --random option only.',
        )

        parser.add_option_group(group)

        if self.app:
            app_callback(self.app, 'addOptions', parser)
