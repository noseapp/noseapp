# -*- coding: utf-8 -*-

import logging
import unittest
from types import FunctionType

from noseapp.core import loader
from noseapp.core import extensions
from noseapp.case.base import TestCase
from noseapp.suite.context import SuiteContext
from noseapp.case.base import make_test_case_class_from_function


logger = logging.getLogger(__name__)


def suite_is_mount(suite):
    """
    If suite is mounting to app then True else False

    :param suite: suite instance
    :type suite: Suite

    :rtype: bool
    """
    return bool(suite.of_app)


class Suite(object):
    """
    Base Suite class for group or one TestCase.

    Simple example:

        suite = Suite(__name__)

        suite.register
        def my_test_case(case):
            case.assertTrue(True)
    """

    # Constant is pre set for require param
    DEFAULT_REQUIRE = None

    # This class is base class for make test case from function
    test_case_class = TestCase

    def __init__(self, name, require=None, context=None):
        """
        :param name: suite name
        :type name: str
        :param require: extension names list
        :type require: list
        :param context: context instance
        :type context: noseapp.suite.context.SuiteContext
        """
        # Suite name. Must be str only
        self.__name = name
        # of app name
        self.__of_app = None
        # Was suite built? True or False
        self.__is_build = False

        # Context of this instance
        self.__context = context or SuiteContext(
            list(self.DEFAULT_REQUIRE or []) + list(require or []),
        )

        # Push callbacks to context. They'll be called with nose suite.
        self.add_before(lambda: self.setUp())
        self.add_after(lambda: self.tearDown())

    @property
    def name(self):
        if self.__of_app:
            return '{}.{}'.format(
                self.__of_app, self.__name,
            )

        return self.__name

    @property
    def of_app(self):
        return self.__of_app

    @property
    def context(self):
        return self.__context

    @property
    def is_build(self):
        return self.__is_build

    @property
    def test_cases(self):
        return self.__context.test_cases

    @property
    def require(self):
        return self.__context.require

    def mount_to_app(self, app):
        """
        :type app: noseapp.app.base.NoseApp
        """
        if suite_is_mount(self):
            raise RuntimeError(
                '{} already mount to <NoseApp {}>. '.format(self, self.__of_app),
            )

        self.__of_app = app.name

        app.context.add_suite(self)

    @property
    def TestCase(self):
        """
        :rtype: noseapp.case.base.TestCase
        """
        return self.test_case_class

    def setUp(self):
        """
        Callback. Will be called run before run suite.
        """
        pass

    def tearDown(self):
        """
        Callback. Will be called run after run suite.
        """
        pass

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

    # unit test style
    skipIf = skip_if
    skipUnless = skip_unless

    def add_pre_run(self, func):
        """
        Set function for pre run test case.

        example:
            suite.add_pre_run(lambda case: case.do_something())
        """
        self.__context.add_pre_run_handler(func)
        return func

    def add_post_run(self, func):
        """
        Set function for post run test case.

        example:
            suite.add_post_run(lambda case: case.do_something())
        """
        self.__context.add_post_run_handler(func)
        return func

    def add_before(self, func):
        """
        Set setup callback for suite prepare
        """
        self.__context.add_setup(func)
        return func

    def add_after(self, func):
        """
        Set teardown callback for suite prepare
        """
        self.__context.add_teardown(func)
        return func

    def ext(self, name):
        """
        Get extension by name.
        Extensions will be available after built suite.

        :param name: extension name
        """
        if not self.__is_build:
            raise RuntimeError(
                'Extension is not allow. Suite is not building.',
            )

        if name not in self.__context.require:
            raise LookupError(
                'Extension "{}" is not required'.format(name),
            )

        return self.__context.extensions.get(name)

    def register(self, cls=None, **kwargs):
        """
        Register test case on context

        :param cls: test case class
        :type cls: noseapp.case.TestCase or function

        :param simple: use for simple test function
        :type simple: bool

        :param skip: if to set then skip case
        :type skip: str

        :rtype: cls
        """
        if not cls and not kwargs:
            raise TypeError('cls param or **kwargs is required')
        elif cls and kwargs:
            raise TypeError('**kwargs can not be used with cls param')

        def wrapped(_class, simple=False, skip=None):
            if type(_class) == FunctionType:
                _class = make_test_case_class_from_function(
                    _class,
                    simple=simple,
                    base_class=self.test_case_class,
                )

            if skip:
                unittest.skip(skip)(_class)

            self.__context.add_test_case(_class)

            logger.debug(
                'Register test case "{}" in {}'.format(
                    _class.__name__, repr(self),
                ),
            )

            return _class

        if cls:
            return wrapped(cls)

        def wrapper(_class):
            return wrapped(_class, **kwargs)

        return wrapper

    def get_map(self):
        """
        Get map of test classes

        {
            'class name': {
                'cls': 'link to class object',
                'tests': {
                    'method name': 'link to class method',
                },
            },
        }

        :return: dict
        """
        mp = {}

        for case in self.__context.test_cases:
            mp[case.__name__] = {
                'cls': case,
                'tests': dict(
                    (atr, getattr(case, atr))
                    for atr in dir(case)
                    if atr.startswith(loader.TEST_NAME_PREFIX)
                    or
                    atr == loader.DEFAULT_TEST_NAME,
                ),
            }

        return mp

    def __call__(self,
                 program_data,
                 shuffle=None,
                 case_name=None,
                 method_name=None):
        """
        Build suite

        :type program_data: noseapp.core.program.ProgramData

        :param shuffle: callable object for randomize test case list
        :param case_name: test name for build
        :param method_name: test case method name for build
        """
        if not self.__of_app:
            raise RuntimeError('Suite can not be building, not mount to app')

        self.__is_build = True

        for ext_name in self.context.require:
            ext = extensions.get(ext_name)
            self.context.add_extension(ext_name, ext)

        if callable(shuffle):
            shuffle(self.__context.test_cases)

        def make_suites():
            suites = []

            if case_name:
                case = loader.load_case_from_suite(case_name, self)
                tests = loader.load_tests_from_test_case(
                    case.mount_to_suite(self),
                    method_name=method_name,
                )

                suites.append(
                    program_data.suite_class(
                        tests,
                        context=case,
                        config=program_data.config,
                        resultProxy=program_data.result_proxy_factory,
                        pre_run_handlers=self.__context.pre_run_handlers,
                        post_run_handlers=self.__context.post_run_handlers,
                    ),
                )
            else:
                for case in self.__context.test_cases:
                    tests = loader.load_tests_from_test_case(
                        case.mount_to_suite(self),
                    )

                    suites.append(
                        program_data.suite_class(
                            tests,
                            context=case,
                            config=program_data.config,
                            resultProxy=program_data.result_proxy_factory,
                            pre_run_handlers=self.__context.pre_run_handlers,
                            post_run_handlers=self.__context.post_run_handlers,
                        ),
                    )

            return suites

        return program_data.suite_class(
            make_suites(),
            context=self.__context,
            config=program_data.config,
        )

    def __repr__(self):
        return '<Suite {}>'.format(self.name)
