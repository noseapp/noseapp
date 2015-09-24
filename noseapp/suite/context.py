# -*- coding: utf-8 -*-


class SuiteContext(object):
    """
    Context storage of suite instance.

    Usage:

        >>> context = SuiteContext(['extension'])
        >>> context.add_setup(lambda: None)
        >>> ...
    """

    def __init__(self, require):
        """
        :param require: extensions names
        :type require: list
        """
        self.__require = require

        self.__setup = []
        self.__teardown = []

        self.__pre_run = []
        self.__post_run = []

        self.__test_cases = []
        self.__extensions = {}

    @property
    def pre_run(self):
        """
        Pre run callbacks storage.

        :rtype: list
        """
        return self.__pre_run

    @property
    def post_run(self):
        """
        Post run callbacks storage.

        :rtype: list
        """
        return self.__post_run

    @property
    def require(self):
        """
        Require extensions storage.

        :rtype: list
        """
        return self.__require

    @property
    def test_cases(self):
        """
        Test cases storage.

        :rtype: list
        """
        return self.__test_cases

    @property
    def extensions(self):
        """
        Storage for prepared extensions.

        :rtype: dict
        """
        return self.__extensions

    def add_test_case(self, case):
        """
        Add test case class to storage.

        :param case: test case class
        :type case: noseapp.case.base.ToNoseAppTestCase
        """
        self.__test_cases.append(case)

    def add_extension(self, name, ext):
        """
        Add prepared extension to storage.

        :param name: extension name
        :type name: str

        :param ext: prepared extension
        """
        self.__extensions[name] = ext

    def add_pre_run(self, func):
        """
        Add pre run callback to storage.

        :param func: callback for pre run
        :type func: callable
        """
        self.__pre_run.append(func)

    def add_post_run(self, func):
        """
        Add post run callback to storage.

        :param func: callback for post run
        :type func: callable
        """
        self.__post_run.append(func)

    def add_setup(self, func):
        """
        Add setup callback to storage.

        :param func: callback to setup
        :type func: callable
        """
        self.__setup.append(func)

    def add_teardown(self, func):
        """
        Add teardown callback to storage.

        :param func: callback to teardown
        :type func: callable
        """
        self.__teardown.append(func)

    def setup(self):
        """
        Method make call to chain of setup callback storage before run suite.
        For nose.suite.ContextSuite
        """
        for callback in self.__setup:
            callback()

    def teardown(self):
        """
        Method make call to chain of teardown callback storage after run suite.
        For nose.suite.ContextSuite
        """
        for callback in self.__teardown:
            callback()
