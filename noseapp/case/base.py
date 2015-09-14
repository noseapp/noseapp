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


class ToNoseAppTestCase(object):
    """
    This is mixin for NoseApp supporting
    """

    @classmethod
    def of_suite(cls, suite):
        """
        Create class of suite

        :type suite: noseapp.suite.base.Suite
        """
        if suite.require and isinstance(suite.require, (list, tuple)):
            for ext_name in suite.require:
                ext = extensions.get(ext_name)

                suite.context.add_extension(ext_name, ext)

                setattr(cls, ext_name, ext)
                setattr(cls, 'of_suite', suite.name)

        return cls

    def __str__(self):
        if hasattr(self, 'of_suite'):
            return '{} ({}:{})'.format(
                self._testMethodName,
                self.of_suite,
                self.__class__.__name__,
            )

        return super(ToNoseAppTestCase, self).__str__()


class TestCase(ToNoseAppTestCase, BaseTestCase):
    """
    Base case class
    """
    pass
