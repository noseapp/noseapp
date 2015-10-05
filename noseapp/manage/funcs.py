# -*- coding: utf-8 -*-

import os
import sys
import imp
from importlib import import_module
from collections import OrderedDict

from noseapp.utils import pyv


_COMMANDS_STORAGE = OrderedDict()


def error(msg):
    sys.stdout.write('error: {}\n'.format(msg))
    sys.exit(1)


def get_command_name():
    try:
        return sys.argv[1]
    except IndexError:
        error('command name is required')


def get_command(name=get_command_name()):
    try:
        return _COMMANDS_STORAGE[name]
    except KeyError:
        error('command "{}" is not found'.format(name))


def get_commands():
    return _COMMANDS_STORAGE


def get_create_app_func(path):
    try:
        module, func = path.split(':')
    except ValueError:
        error('incorrect import path to get application function')
    except IndexError:
        error('import path is required as first argument of signature')

    module = import_module(module)
    func = getattr(module, func, None)

    if callable(func):
        return func

    error('function for get application is not found')


def load_manage_py():
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
    assert isinstance(name, pyv.basestring), 'name of command must be string only'

    _COMMANDS_STORAGE[name] = command
