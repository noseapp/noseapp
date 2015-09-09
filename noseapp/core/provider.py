# -*- coding: utf-8 -*-

from noseapp.app import config


class FromNoseToApp(object):

    def __init__(self, app):
        """
        :type app: noseapp.app.NoseApp
        """
        self.__app = app

    def initialize(self, options):
        # Push options from parser to application
        self.__app.options = self.__app.config_class(
            config.load(options),
        )
        # Initialize application
        self.__app.initialize()

        def init_sub_app(sub_app):
            sub_app.options = self.__app.options
            sub_app.initialize()

        for sub_app in self.__app.sub_apps:
            init_sub_app(sub_app)

    def add_options(self, parser):
        self.__app.add_options(parser)

        for sub_app in self.__app.sub_apps:
            sub_app.add_options(parser)

    def before(self):
        self.__app.before()

        for sub_app in self.__app.sub_apps:
            sub_app.before()

    def after(self):
        self.__app.after()

        for sub_app in self.__app.sub_apps:
            sub_app.after()
