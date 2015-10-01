# -*- coding: utf-8 -*-

from unittest import TestCase as _TestCase

from nose.case import Test as NoseTestWrapper

from noseapp.case.context import TestCaseContext
from noseapp.datastructures import ModifyDict as MountData


def make_test_case_class_from_function(
        func,
        base_class,
        doc=None,
        simple=False,
        class_name=None,
        class_name_creator=None):
    """
    It's just create test case class from function.
    Function will be bound method (runTest) of new class.

    :param func: test function. for example: my_test = lambda case: 'just do it something'
    :param base_class: base class for making class
    :param simple: if true that not inject case instance
    :param class_name: name of new class. default function name
    :param class_name_creator: callable object for creating name of function object
    """
    if callable(class_name_creator):
        class_name = class_name_creator(func)

    cls = type(
        class_name or func.__name__,
        (base_class, ),
        {
            '__doc__': doc or func.__doc__,
        },
    )

    if simple:
        cls.runTest = lambda s: func()
    else:
        cls.runTest = func

    return cls


def case_is_mount(case):
    """
    If case is mounting to suite then True else False

    :param case: test case class or instance

    :rtype: bool
    """
    return hasattr(case, '__mount_data__') \
        and \
        isinstance(case.__mount_data__, MountData)


def get_case_master_id(case):
    """
    Get id of master process

    :type case: ToNoseAppTestCase
    """
    if isinstance(case, NoseTestWrapper):
        case = case.test

    return case._ToNoseAppTestCase__master_id


class ToNoseAppTestCase(object):
    """
    This is mixin for noseapp supporting.
    Class must be first in inheritance chain!

    Usage::

        class MyTestCase(ToNoseAppTestCase, unittest.TestCase):
            pass
    """

    def __init__(self, *args, **kwargs):
        if not case_is_mount(self):
            raise RuntimeError(
                'Test case "{}" can not be created without mounting to suite'.format(
                    self.__class__,
                ),
            )

        super(ToNoseAppTestCase, self).__init__(*args, **kwargs)

        self.__master_id = id(self)

        if hasattr(self, 'REQUIRE'):
            self.__mount_data__.context.update_by_require(self.REQUIRE)

    @classmethod
    def mount_to_suite(cls, suite):
        """
        Mount class to suite.
        If this procedure will be ignored then class can't be instantiate.

        :type suite: noseapp.suite.base.Suite

        :raises: RuntimeError
        :rtype: cls
        """
        if case_is_mount(cls):
            raise RuntimeError(
                '"{}" already mount to {}'.format(
                    cls.__name__, cls.__mount_data__.of_suite,
                ),
            )

        setattr(
            cls,
            '__mount_data__',
            MountData(
                of_suite=suite.name,
                context=TestCaseContext(suite),
            ),
        )

        return cls

    @property
    def of_suite(self):
        """
        This is suite name after mounting.
        """
        return self.__mount_data__.of_suite

    def ext(self, name):
        """
        Get extension by name.
        Extension must be required.

        Example::

            suite = Suite(__name__, require=['extension'])

            @suite.register
            class Test(TestCase):

                def test(self):
                    ext = self.ext('extension')

        :param name: extension name
        :type name: str

        :raises: noseapp.core.extensions.ExtensionNotRequired
        """
        return self.__mount_data__.context.ext(name)

    def __str__(self):
        return '{} ({}:{})'.format(
            self._testMethodName,
            self.__mount_data__.of_suite,
            self.__class__.__name__,
        )


class TestCase(ToNoseAppTestCase, _TestCase):
    """
    Base case class
    """
    pass
