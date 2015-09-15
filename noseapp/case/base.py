# -*- coding: utf-8 -*-

from unittest import TestCase as BaseTestCase

from noseapp.core import extensions


def make_test_case_class_from_function(
        func,
        base_class,
        doc=None,
        simple=False,
        class_name=None,
        class_name_creator=None):
    """
    It's just creating test case class from function.
    Function will be bound method (runTest) of new class.

    :param func: test function. for example: my_test = lambda case: 'just do it something'
    :param base_class: base class for making class
    :param simple: if true that not inject case instance
    :param class_name: name of new class. default function name
    :param class_name_creator: callable object for creating name of function object
    """
    if callable(class_name_creator):
        class_name = class_name_creator(func)

    cls = type(class_name or func.__name__, (base_class, ), {})
    cls.__doc__ = doc or func.__doc__

    if simple:
        cls.runTest = lambda s: func()
    else:
        cls.runTest = func

    return cls


def case_is_mount(case):
    """
    Return True if case is mount to suite else False

    :param case: test case class or instance

    :rtype: bool
    """
    return hasattr(case, '_of_suite')


class ToNoseAppTestCase(object):
    """
    This is mixin for NoseApp supporting
    """

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

        if suite.require and isinstance(suite.require, (list, tuple)):
            for ext_name in suite.require:
                ext = extensions.get(ext_name)

                suite.context.add_extension(ext_name, ext)

                setattr(cls, ext_name, ext)
                setattr(cls, '_of_suite', suite.name)

        return cls

    @property
    def of_suite(self):
        if hasattr(self, '_of_suite'):
            return self._of_suite
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
