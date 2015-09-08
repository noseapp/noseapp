# -*- coding: utf-8 -*-

from random import Random

from noseapp.core import ExtensionInstaller


class ExampleRandom(object):

    name = 'random'

    def __init__(self, sid):
        self.__random = Random(sid)

    def __getattr__(self, item):
        return getattr(self.__random, item)

    @classmethod
    def install(cls, app):
        installer = ExtensionInstaller(
            cls, (app.config.RANDOM_EX_SID, ), {},
        )
        app.shared_extension(cls=installer)
        return installer
