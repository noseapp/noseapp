# -*- coding: utf-8 -*-

"""
Auto load suites for register in noseapp.NoseApp
"""

import os
from importlib import import_module


TEST_NAME_PREFIX = 'test'
DEFAULT_TEST_NAME = 'runTest'


class LoaderError(BaseException):
    pass


def is_exist(path):
    """
    Check exist path
    """
    if not os.path.exists(path):
        raise LoaderError('Dir "{}" is not exist'.format(path))


def is_package(path):
    """
    May be path is python package?
    """
    if not os.path.isfile(os.path.join(path, '__init__.py')):
        return False
    return True


def load_suites_from_dir(path, import_base=None):
    """
    Load suites from dir

    :type path: str
    :param import_base: base import path
    :type import_base: str
    """
    from noseapp.suite.base import Suite

    if import_base and not is_package(path):
        return []

    suites = []

    py_files = filter(
        lambda f: f.endswith('.py') and not f.startswith('_'),
        os.listdir(path),
    )
    modules = (m.rstrip('.py') for m in py_files)

    for module in modules:

        if import_base:
            module = '{}.{}'.format(import_base, module)

        module = import_module(module)

        module_suites = (
            getattr(module, atr)
            for atr in dir(module)
            if isinstance(
                getattr(module, atr, None), Suite,
            )
        )

        suites.extend(module_suites)

    return suites


def load_suites_from_path(path, import_base=None):
    """
    Recursive load suites from path

    :param path: path to dir
    :type path: str
    :param import_base: base import path
    :type import_base: str
    """
    is_exist(path)

    suites = []

    copy_import_base = import_base

    suites.extend(
        load_suites_from_dir(path, import_base=import_base),
    )

    for root, dirs, files in os.walk(path):

        for d in dirs:
            dir_abs_path = os.path.join(root, d)

            if import_base is None:
                _import_base = d
            else:
                _import_base = '{}.{}'.format(import_base, d)

            suites.extend(
                load_suites_from_path(
                    dir_abs_path,
                    import_base=_import_base,
                ),
            )

            import_base = copy_import_base

    return suites


def load_tests_from_test_case(
        test_case_class,
        method_name=None,
        test_name_prefix=TEST_NAME_PREFIX,
        default_test_name=DEFAULT_TEST_NAME):
    """
    Create instances of test_case_class by test names
    """
    cls_dir = dir(test_case_class)

    if method_name:
        if method_name not in cls_dir:
            raise LoaderError(
                'Method "{}" of "{}" class is not found'.format(
                    method_name, test_case_class.__name__,
                ),
            )
        return map(test_case_class, [method_name])

    def is_test_name(name):
        return name.startswith(test_name_prefix) \
            or \
            name == default_test_name

    return map(test_case_class, filter(is_test_name, cls_dir))


def load_suite_by_name(name, suites):
    """
    Find suite in list by name

    :param name: suite name
    :param suites: suites list
    """
    for suite in suites:
        if suite.name == name:
            return suite
    else:
        raise LoaderError(
            'Suite "{}" is not found'.format(name),
        )


def load_case_from_suite(class_name, suite):
    """
    Find test case class by class name in suite or suite mediator

    :param class_name: class name
    :param suite: suite or suite mediator instance
    """
    for case in suite.test_cases:
        if case.__name__ == class_name:
            return case
    else:
        raise LoaderError(
            'Test case "{}" is not found'.format(class_name),
        )
