# -*- coding: utf-8 -*-

"""
Auto load suites for register in noseapp.NoseApp
"""

import os
from importlib import import_module

from noseapp.suite import Suite


class LoadSuitesError(BaseException):
    pass


def is_exist(path):
    """
    Check exist path
    """
    if not os.path.exists(path):
        raise LoadSuitesError('Dir "{}" does not exist'.format(path))


def is_package(path):
    """
    May be path is python package?
    """
    if not os.path.isfile(os.path.join(path, '__init__.py')):
        raise LoadSuitesError('"{}" is not python package'.format(path))


def load_from_dir(path, import_base=None):
    """
    Load suites from dir

    :type path: str
    :param import_base: base import path
    :type import_base: str
    """
    if import_base:
        is_package(path)

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

    suites.extend(load_from_dir(path, import_base=import_base))

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
