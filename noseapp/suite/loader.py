# -*- coding: utf-8 -*-

import os
from importlib import import_module

from noseapp.suite.base import Suite


class LoadSuitesError(BaseException):
    pass


def is_exist(path):
    """
    Проверяет существование указанного пути
    """
    if not os.path.exists(path):
        raise LoadSuitesError('Dir "{}" does not exist'.format(path))


def is_package(path):
    """
    Проверяет является ли указанный путь python пакетом
    """
    if not os.path.isfile(os.path.join(path, '__init__.py')):
        raise LoadSuitesError('"{}" is not python package'.format(path))


def load_from_dir(path, import_base=None):
    """
    Выполнить загрузку из директории

    :param path: путь до директории
    :param import_base: базовый путь до модуля при импорте
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

        for suite in module_suites:
            suites.append(suite)

    return suites


def load_suites_from_path(path, import_base=None):
    """
    Рекурсивно обходит модули и пакеты внутри
    директории, загружает suites из модулей

    :param path: путь до папки откуда выгружать suites
    :param import_base: базовый путь до модуля при импорте
    """
    is_exist(path)

    suites = []

    map(suites.append, load_from_dir(path, import_base=import_base))

    for root, dirs, files in os.walk(path):

        for d in dirs:
            dir_abs_path = os.path.join(root, d)

            if import_base is None:
                import_base = d
            else:
                import_base = '{}.{}'.format(import_base, d)

            map(
                suites.append,
                load_suites_from_path(
                    dir_abs_path,
                    import_base=import_base,
                ),
            )

    return suites
