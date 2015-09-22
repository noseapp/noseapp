# -*- coding: utf-8 -*-

from nose.plugins import Plugin as BasePlugin


class AppPlugin(BasePlugin):
    """
    Base application plugin
    """

    def __init__(self):
        super(AppPlugin, self).__init__()

        self.app = None

    def init_app(self, app):
        """
        Push app instance

        :type app: noseapp.NoseApp
        """
        self.app = app
