# -*- coding: utf-8 -*-

from unittest import TestCase as BaseTestCase


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
    return hasattr(case, '_of_suite')


def get_case_master_id(case):
    """
    Get id of master process

    :type case: ToNoseAppTestCase
    """
    if hasattr(case, 'test'):
        case = case.test

    return case._ToNoseAppTestCase__master_id


class ExtensionStorage(object):
    """
    Storage for extensions of test case
    """

    def __init__(self, suite):
        """
        :type suite: noseapp.suite.base.Suite
        """
        self.__require = []
        self.__require.extend(suite.require)

        self.__extensions = dict(
            (k, v) for k, v in suite.context.extensions.items()
        )

    def __call__(self, name):
        if name in self.__require:
            return self.__extensions[name]

        raise LookupError(
            'Extension "{}" is not required'.format(name),
        )


class ToNoseAppTestCase(object):
    """
    This is mixin for NoseApp supporting
    """

    def __init__(self, *args, **kwargs):
        super(ToNoseAppTestCase, self).__init__(*args, **kwargs)

        self.__master_id = id(self)

    @classmethod
    def mount_to_suite(cls, suite):
        """
        Create class of suite

        :type suite: noseapp.suite.base.Suite
        """
        if case_is_mount(cls):
            raise RuntimeError(
                '"{}" already mount to {}'.format(
                    cls.__name__, cls._of_suite,
                ),
            )

        setattr(cls, '_of_suite', suite.name)
        setattr(cls, '_ext_storage', ExtensionStorage(suite))

        return cls

    @property
    def of_suite(self):
        if case_is_mount(self):
            return self._of_suite

        return None

    def ext(self, name):
        if case_is_mount(self):
            return self._ext_storage(name)

        return None

    def __str__(self):
        if case_is_mount(self):
            return '{} ({}:{})'.format(
                self._testMethodName,
                self._of_suite,
                self.__class__.__name__,
            )

        return super(ToNoseAppTestCase, self).__str__()


class TestCase(ToNoseAppTestCase, BaseTestCase):
    """
    Base case class
    """
    pass
