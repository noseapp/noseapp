# -*- coding: utf-8 -*-

import logging
import unittest
from types import FunctionType

from noseapp.core import loader
from noseapp.core import extensions
from noseapp.suite.context import SuiteContext
from noseapp.case.screenplay import ScreenPlayCase
from noseapp.case.base import make_test_case_class_from_function


logger = logging.getLogger(__name__)


def suite_is_mount(suite):
    """
    If suite is mounting to app then True else False.

    :param suite: suite instance
    :type suite: Suite

    :rtype: bool
    """
    return bool(suite.of_app)


class Suite(object):
    """
    Base Suite class for group or one TestCase.

    Usage::

        suite = Suite(__name__)

        @suite.register
        class Case(suite.TestCase):

            def runTest(self):
                pass

        @suite.register
        def my_test_case(case):
            case.assertTrue(True)

        @suite.register(simple=True)
        def simple_test():
            assert True
    """

    # Constant is pre set for require param
    DEFAULT_REQUIRE = None

    # This class is base class for making test case from function
    test_case_class = ScreenPlayCase

    def __init__(self, name, require=None, context=None):
        """
        :param name: suite name
        :type name: str

        :param require: extension names
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

        # Push callbacks to context. They'll be called with run nose suite.
        self.__context.add_setup(lambda: self.setUp())
        self.__context.add_teardown(lambda: self.tearDown())

    @property
    def name(self):
        """
        Suite name.
        If suite is mounting to app then name
        is <app_name>.<suite_name> else <suite_name>.
        """
        if self.__of_app:
            return '{}.{}'.format(
                self.__of_app, self.__name,
            )

        return self.__name

    @property
    def of_app(self):
        """
        Name of mounted application.

        :rtype: str or None
        """
        return self.__of_app

    @property
    def context(self):
        """
        Suite context.

        :rtype: noseapp.suite.context.SuiteContext
        """
        return self.__context

    @property
    def is_build(self):
        """
        If suite is building return True else False.

        :rtype: bool
        """
        return self.__is_build

    @property
    def test_cases(self):
        """
        Test cases storage of context.

        :rtype: list
        """
        return self.__context.test_cases

    @property
    def require(self):
        """
        Extensions names storage of context.

        :rtype: list
        """
        return self.__context.require

    @property
    def status(self):
        """
        Get suite status.
        If suite is mounted to application
        then 'mounted' else 'unmounted'.

        :rtype: str
        """
        return 'mounted' if self.__of_app else 'unmounted'

    def mount_to_app(self, app):
        """
        :param app: application instance
        :type app: noseapp.app.base.NoseApp

        :raises: RuntimeError
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
        Get test case class from suite instance.
        Will be return a test_case_class alias.
        The alias is base class for making test case from function.

        :rtype: noseapp.case.screenplay.ScreenPlayCase
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
        Proxy to unittest.skip.

        Example::

            class Test(suite.TestCase):

                @suite.skip('TODO: ...')
                def test(self):
                    pass

        :rtype: unittest.skip
        """
        return unittest.skip

    @property
    def skip_if(self):
        """
        Proxy to unittest.skipIf.

        :rtype: unittest.skipIf
        """
        return unittest.skipIf

    @property
    def skip_unless(self):
        """
        Proxy to unittest.skipUnless.

        :rtype: unittest.skipUnless
        """
        return unittest.skipUnless

    # unit test style
    skipIf = skip_if
    skipUnless = skip_unless

    def add_pre_run(self, func):
        """
        Add function for pre run test case to context.

        Example::

            @suite.add_pre_run
            def pre_run(case):
                case.do_something()

            # or

            suite.add_pre_run(lambda case: case.do_something())
        """
        self.__context.add_pre_run(func)
        return func

    def add_post_run(self, func):
        """
        Add function for post run test case to context.

        Example::

            @suite.add_post_run
            def post_run(case):
                case.do_something()

            # or

            suite.add_post_run(lambda case: case.do_something())
        """
        self.__context.add_post_run(func)
        return func

    def add_setup(self, func):
        """
        Add setup callback to context.

        Example::

            @suite.add_setup
            def setup():
                pass

            # or

            suite.add_setup(lambda: None)
        """
        self.__context.add_setup(func)
        return func

    def add_teardown(self, func):
        """
        Add teardown callback to context.

        Example::

            @suite.add_teardown
            def teardown():
                pass

            # or

            suite.add_teardown(lambda: None)
        """
        self.__context.add_teardown(func)
        return func

    def ext(self, name):
        """
        Get extension by name.
        Extensions will be available after build suite.

        Example::

            class MySuite(Suite):

                DEFAULT_REQUIRE = [
                    'extension',
                ]

                def setUp(self):
                    ext = self.ext('extension')

        :param name: extension name
        :type name: str

        :raises: RuntimeError, noseapp.core.extensions.ExtensionNotRequired
        """
        if not self.__is_build:
            raise RuntimeError(
                'Extensions is not available. Suite is not building.',
            )

        if name not in self.__context.require:
            raise extensions.ExtensionNotRequired(name)

        return self.__context.extensions.get(name)

    def register(self, cls=None, **kwargs):
        """
        Add test case to context.

        Example::

            @suite.register
            class TestCase(suite.TestCase):

                def test(self):
                    pass

            # Skip test
            @suite.register(skip='TODO: ...')
            def test(case):
                pass

            # Require extension for test case only
            @suite.register(require=['extension'])
            def test_require_ex(case):
                ext = case.ext('extension')

        :param cls: test case class
        :type cls: noseapp.case.TestCase or function

        :param simple: use for simple test function
        :type simple: bool

        :param skip: if to set then skip case
        :type skip: str

        :param require: extensions names
        :type require: list

        :raises: TypeError, RuntimeError
        :rtype: cls
        """
        if not cls and not kwargs:
            raise TypeError('cls param or **kwargs is required')
        elif cls and kwargs:
            raise TypeError('**kwargs can not be used with cls param')

        def wrapped(_class, simple=False, skip=None, require=None):
            if type(_class) == FunctionType:
                _class = make_test_case_class_from_function(
                    _class,
                    simple=simple,
                    base_class=self.TestCase,
                )

            if skip:
                unittest.skip(skip)(_class)

            if hasattr(_class, 'REQUIRE'):
                raise RuntimeError('"REQUIRE" attribute can not be pre set')

            if require:
                setattr(_class, 'REQUIRE', require)

            self.__context.add_test_case(_class)

            logger.debug(
                'Register test case "{}" on {}'.format(
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
        Get map of test classes.

        ::

            {
                'class name': {
                    'cls': link_to_class,
                    'tests': {
                        'method name': link_to_test_method,
                    },
                },
            }

        :rtype: dict
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
        Build suite. After call suite instance will be
        created instance of nose.suite.ContextSuite

        :param program_data: instance of ProgramData
        :type program_data: noseapp.core.program.ProgramData

        :param shuffle: callable object for randomize test case list
        :param case_name: test name for build
        :param method_name: test case method name for build

        :raises: RuntimeError
        :rtype: noseapp.core.suite.base.BaseSuite
        """
        if not self.__of_app:
            raise RuntimeError('Suite can not be building, not mounted to app')

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
                        pre_run_handlers=self.__context.pre_run,
                        post_run_handlers=self.__context.post_run,
                        resultProxy=program_data.result_proxy_factory,
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
                            pre_run_handlers=self.__context.pre_run,
                            post_run_handlers=self.__context.post_run,
                            resultProxy=program_data.result_proxy_factory,
                        ),
                    )

            return suites

        return program_data.suite_class(
            make_suites(),
            context=self.__context,
            config=program_data.config,
        )

    def __repr__(self):
        return '<Suite({}): {}>'.format(self.status, self.name)
