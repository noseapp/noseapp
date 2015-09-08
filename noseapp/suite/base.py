# -*- coding: utf-8 -*-

import logging
import unittest
from types import FunctionType

from noseapp.case.base import TestCase
from noseapp.suite.mediator import SuiteMediator
from noseapp.case.base import make_test_case_class_from_function


logger = logging.getLogger(__name__)


class Suite(object):
    """
    Base Suite class for group or one TestCase.
    """

    HANDLERS = None
    DEFAULT_REQUIRE = None

    test_case_class = TestCase
    mediator_class = SuiteMediator

    def __init__(self, name, require=None):
        """
        :param name: suite name
        :type name: str
        :param require: extension names list
        :type require: list
        """
        self.__name = name
        self.__mediator = self.mediator_class(
            require=list(self.DEFAULT_REQUIRE or []) + list(require or []),
        )

        self.__current_app = None

        if self.HANDLERS:
            for handler in self.HANDLERS:
                self.add_handler(handler)

        self.before(lambda: self.setUp())
        self.after(lambda: self.tearDown())

    def initialize(self):
        """
        Callback. Will be called after registration on app.
        """
        pass

    @property
    def name(self):
        return self.__name

    @property
    def require(self):
        """
        List names of require extensions
        """
        return self.__mediator.require

    @property
    def handlers(self):
        """
        Handlers list
        """
        return self.__mediator.handlers

    @property
    def test_cases(self):
        """
        Test cases list
        """
        return self.__mediator.test_cases

    @property
    def current_app(self):
        """
        :rtype: noseapp.app.NoseApp
        """
        if self.__current_app is None:
            raise RuntimeError('Working outside app context')

        return self.__current_app

    @current_app.setter
    def current_app(self, app):
        self.__current_app = app

    @property
    def skip(self):
        """
        :rtype: unittest.skip
        """
        return unittest.skip

    @property
    def skip_if(self):
        """
        :rtype: unittest.skipIf
        """
        return unittest.skipIf

    @property
    def skip_unless(self):
        """
        :rtype: unittest.skipUnless
        """
        return unittest.skipUnless

    @property
    def TestCase(self):
        """
        :rtype: noseapp.case.base.TestCase
        """
        return self.test_case_class

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def add_handler(self, f):
        """
        Set test handler to run
        """
        return self.__mediator.add_handler(f)

    def before(self, f):
        """
        Set setup callback for suite prepare
        """
        return self.__mediator.add_setup(f)

    def after(self, f):
        """
        Set teardown callback for suite prepare
        """
        return self.__mediator.add_teardown(f)

    def register(self, cls):
        """
        Register test case class

        :type cls: noseapp.case.TestCase or function
        """
        logger.debug('Register test case "{}" in {} '.format(cls.__name__, repr(self)))

        if type(cls) == FunctionType:
            cls = make_test_case_class_from_function(
                cls,
                base_class=self.test_case_class,
            )
        self.__mediator.add_test_case(cls)

        return cls

    def get_map(self):
        """
        Get map of test classes

        :return: dict
        """
        return self.__mediator.create_map()

    def __call__(self, program_data, **kwargs):
        """
        Build suite

        :type program_data: noseapp.core.program.ProgramData

        :param shuffle: callable object for randomize test case list
        :param case_name: test name for building
        """
        return self.__mediator.create_suite(program_data, **kwargs)

    def __repr__(self):
        return '<Suite {}>'.format(self.__name)
