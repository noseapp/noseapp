
import os

from noseapp.plugins.base import AppPlugin


class AppConfigurePlugin(AppPlugin):

    name = 'app-configure'

    def options(self, parser, env=os.environ):
        super(AppConfigurePlugin, self).options(parser, env=env)

        parser.add_option(
            '--app-processes',
            dest='app_processes',
            default=0,
            type=int,
            help='Spread test run among this many processes.'
        )
        parser.add_option(
            '--gevent',
            dest='gevent_pool',
            default=0,
            type=int,
            help='Spread test run among this many gevent greanlets.'
        )
        parser.add_option(
            '--greenlets',
            dest='gevent_greanlets',
            default=0,
            type=int,
            help='Spread greenlets inside suite greanlet.'
        )
        parser.add_option(
            '--threads',
            dest='thread_pool',
            default=0,
            type=int,
            help='Spread threads inside process.'
        )
        parser.add_option(
            '--ls',
            dest='ls',
            action='store_true',
            default=False,
            help='Show suites tree.'
        )
        parser.add_option(
            '--doc',
            dest='doc',
            action='store_true',
            default=False,
            help='Show docstring in suite info.'
        )
