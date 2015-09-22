# -*- coding: utf-8 -*-


class SuiteContext(object):

    def __init__(self, require):
        self.__require = require

        self.__setup = []
        self.__teardown = []

        self.__pre_run_handlers = []
        self.__post_run_handlers = []

        self.__test_cases = []
        self.__extensions = {}

    @property
    def pre_run_handlers(self):
        return self.__pre_run_handlers

    @property
    def post_run_handlers(self):
        return self.__post_run_handlers

    @property
    def require(self):
        return self.__require

    @property
    def test_cases(self):
        return self.__test_cases

    @property
    def extensions(self):
        return self.__extensions

    def add_test_case(self, case):
        self.__test_cases.append(case)

    def add_extension(self, name, ext):
        self.__extensions[name] = ext

    def add_pre_run_handler(self, func):
        self.__pre_run_handlers.append(func)

    def add_post_run_handler(self, func):
        self.__post_run_handlers.append(func)

    def add_setup(self, func):
        self.__setup.append(func)

    def add_teardown(self, func):
        self.__teardown.append(func)

    def setup(self):
        """
        Callback for nose context
        """
        for callback in self.__setup:
            callback()

    def teardown(self):
        """
        Callback for nose context
        """
        for callback in self.__teardown:
            callback()
