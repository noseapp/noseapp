# -*- coding: utf-8 -*-

"""
NoseApp management.

Command line interface:
    noseapp-manage <command name>, <command args>, <command kwargs> [options]

Example:
    noseapp-manage command argument1 argument2 argument3=value
"""

import os
import imp
import sys
import inspect
import traceback
from importlib import import_module
from collections import OrderedDict


_COMMANDS = OrderedDict()


def _error(msg):
    sys.stdout.write('error: {}\n'.format(msg))
    sys.exit(1)


def _get_command_name():
    try:
        return sys.argv[1]
    except IndexError:
        _error('command name is required')


def _get_command(name):
    try:
        return _COMMANDS[name]
    except KeyError:
        _error('command "{}" is not found'.format(name))


def _get_create_app_func(path):
    try:
        module, func = path.split(':')
    except ValueError:
        _error('incorrect import path to get application function')
    except IndexError:
        _error('import path is required as first argument of signature')

    module = import_module(module)
    func = getattr(module, func, None)

    if callable(func):
        return func

    _error('function for get application is not found')


def _load_manage_py():
    manage_py = os.path.join(os.getcwd(), 'manage.py')

    if os.path.isfile(manage_py):
        manage_module = imp.new_module(manage_py.rstrip('.py'))
        manage_module.__file__ = manage_py

        try:
            execfile(manage_py, manage_module.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load manage file "{}"'.format(e.strerror)
            raise


def register_command(name, command):
    """
    Register command to run.

    Usage::

        def say_hello():
            "Help here"
            print 'Hello world!'

        register_command('hello', say_hello)
        # to run: noseapp-manage hello
        # help: noseapp-manage help hello

    :param name: command name
    :param command: callable object
    """
    assert callable(command), 'command is not callable'
    assert isinstance(name, basestring), 'name of command must be string only'

    _COMMANDS[name] = command


class DefaultCommands(object):

    @staticmethod
    def help(command_name=None):
        """
        :param command_name: command name
        """
        sys.stdout.write(__doc__)

        if command_name:
            command_func = _get_command(command_name)

            sys.stdout.write('\nCommand: {} ({}):\n'.format(command_name, inspect.getfile(command_func)))

            sys.stdout.write('{}\n'.format(command_func.__doc__))
        else:
            sys.stdout.write('\nCommands:\n\n')

            for command_name in _COMMANDS:
                sys.stdout.write('    * {}\n'.format(command_name))

        sys.stdout.write('\n')

    @staticmethod
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
                from gevent.monkey import patch_all
                patch_all()
                break

        app = _get_create_app_func(app_path)(**kwargs)
        app.run()

    # TODO:
    # @staticmethod
    # def create_project(name):
    #     """
    #     Create base structure of project
    #     """
    #     pass


# Add commands here. Order is important.
register_command('help', DefaultCommands.help)
register_command('run', DefaultCommands.run_app)


def run():
    _load_manage_py()

    command = _get_command(
        _get_command_name(),
    )

    args = []
    kwargs = {}

    arguments = []

    for arg in sys.argv[2:]:
        if arg.startswith('-'):
            break

        arguments.append(arg)

    for arg in arguments:
        if '=' in arg:
            k, v = arg.split('=')
            kwargs[k.strip()] = v.strip()
        else:
            args.append(arg.strip())

    try:
        command(*args, **kwargs)
    except TypeError:
        _error(
            'Is invalid signature of command, may be?\n\n{}'.format(
                traceback.format_exc(),
            ),
        )


if __name__ == '__main__':
    run()
