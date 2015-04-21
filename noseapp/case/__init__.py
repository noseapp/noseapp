# -*- coding: utf-8 -*-

from noseapp.case.base import TestCase
from noseapp.case.screenplay import step
from noseapp.case.screenplay import ScreenPlayCase
from noseapp.datastructures import ModifyDict as _BaseCaseSettings


class TestCaseSettings(_BaseCaseSettings):
    """
    Installation settings for test case from application

    Usage:
        settings = TestCaseSettings(
            debug=True,
            project_url='http://...',
        )
        settings.install(app)

        suite = Suite(__name__, require=['settings'])
    """

    name = 'settings'

    def install(self, app):
        app.shared_data(self.name, self)


__all__ = (
    step,
    TestCase,
    ScreenPlayCase,
    TestCaseSettings,
)
