# -*- coding: utf-8 -*-

from nose.plugins import Plugin as BasePlugin


class AppPlugin(BasePlugin):
    """
    Base application plugin
    """

    def __call__(self, app):
        """
        Push app instance

        :type app: noseapp.NoseApp
        """
        self.app = app
        return self
