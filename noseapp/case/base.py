# -*- coding: utf-8 -*-

from unittest import TestCase as BaseTestCase

from noseapp.core import extensions


def make_test_case_class_from_function(
        func,
        base_class,
        class_name=None,
        class_name_creator=None):
    """
    It's just creating test case class from function.
    Function will be bound method (runTest) of new class.

    :param func: test function. for example: my_test = lambda case: 'just do it something'
    :param base_class: base class for making class
    :param class_name: name of new class. default function name
    :param class_name_creator: callable object for creating name of function object
    """
    if callable(class_name_creator):
        class_name = class_name_creator(func)

    cls = type(class_name or func.__name__, (base_class, ), {})
    cls.runTest = func  # bound this

    return cls


class ToNoseAppTestCase(object):
    """
    This is mixin for NoseApp supporting
    """

    @classmethod
    def setup_extensions(cls, require):
        """
        Init require extensions

        :param require: extensions list
        :type require: list or tuple
        """
        if require and hasattr(require, '__iter__'):
            for ext_name in require:
                setattr(cls, ext_name, extensions.get(ext_name))

        return cls


class TestCase(BaseTestCase, ToNoseAppTestCase):
    """
    Base case class
    """
    pass
