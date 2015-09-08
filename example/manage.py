# -*- coding: utf-8 -*-

from noseapp import manage


def say_hello(name=None):
    print 'Hello {}!'.format(name or 'kitty')


manage.register_command('say_hello', say_hello)
