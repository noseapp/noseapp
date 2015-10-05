# -*- coding: utf-8 -*-

"""
NoseApp management.

Command line interface:
    noseapp-manage <command name>, <command args>, <command kwargs> [options]

Example:
    noseapp-manage command argument1 argument2 argument3=value
"""

import sys
import inspect

from noseapp.utils import pyv
from noseapp.manage import funcs


def help(command_name=None):
    """
    :param command_name: command name
    """
    sys.stdout.write(__doc__)

    if command_name:
        command_func = funcs.get_command(command_name)

        sys.stdout.write('\nCommand: {} ({}):\n'.format(command_name, inspect.getfile(command_func)))

        sys.stdout.write('{}\n'.format(command_func.__doc__))
    else:
        sys.stdout.write('\nCommands:\n\n')

        commands = funcs.get_commands()

        for command_name in commands:
            sys.stdout.write('    * {}\n'.format(command_name))

    sys.stdout.write('\n')


def run_app(app_path, **kwargs):
    """
    Command for run application.

    :usage:
        noseapp-manage run import.path.to:get_app_function

    :app_path: path for importing application
    :kwargs: kwargs of create application function
    """
    for argv in sys.argv:
        if 'gevent' in argv:
            if pyv.IS_PYTHON_3:
                raise pyv.UnSupportedError('gevent lib unsupported with python 3')

            try:
                from gevent.monkey import patch_all
                patch_all()
            except ImportError as e:
                raise ImportError(
                    '{}. {}.'.format(e.message, 'Please install gevent'),
                )

            break

    app = funcs.get_create_app_func(app_path)(**kwargs)
    app.run()
