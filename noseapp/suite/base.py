# -*- coding: utf-8 -*-

from noseapp.suite.mediator import TestCaseMediator


class Suite(object):
    """
    Base Suite class for group or one TestCase.

    Usage DEFAULT_REQUIRE property for default extensions require.
    """

    mediator_class = TestCaseMediator

    def __init__(self, name, require=None):
        """
        :param name: suite name
        :type name: str
        :param require: extension names list
        :type require: list
        """
        self._name = name

        if hasattr(self, 'DEFAULT_REQUIRE'):
            self._require = self.DEFAULT_REQUIRE + (require or [])
        else:
            self._require = require

        self._mediator = self.mediator_class(require=self._require)

    @property
    def name(self):
        return self._name

    @property
    def require(self):
        return self._require

    def register(self, cls):
        """
        Add test case class

        :type cls: noseapp.case.TestCase
        """
        self._mediator.add_test_case(cls)
        return cls

    def get_map(self):
        return self._mediator.create_map()

    def __call__(self, nose_config, test_loader):
        """
        Build suite
        """
        return self._mediator.create_suite(nose_config, test_loader)

    def __repr__(self):
        return '<Suite {}>'.format(self._name)
