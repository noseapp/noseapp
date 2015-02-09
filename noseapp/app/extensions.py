# -*- coding: utf-8 -*-


"""
Модуль позволяет шарить расширения между TestCase
"""

from copy import deepcopy

from noseapp.datastructures import ModifyDict


_EXTENSIONS = {}


class ExtensionNotFound(BaseException):
    """
    Расширение не найдено
    """
    pass


class ExtensionNotRequired(BaseException):
    """
    Расширение не подключено
    """
    pass


def get(name, require=None):
    """
    Получить расширение.

    :param name: имя расширения
    :param require: список разрешенных расширений
    """
    if require is not None and name not in require:
        raise ExtensionNotRequired(name)

    try:
        ext = _EXTENSIONS[name]

        if ext.__class__ is ModifyDict:
            return ext.cls(*ext.args, **ext.kwargs)

        return deepcopy(ext)  # каждая suite получит копию расширения
        # чтобы не иметь не иметь возможности шарить изменения
    except KeyError:
        raise ExtensionNotFound(name)


def set(name, ext, in_context=False, args=None, kwargs=None):
    """
    Зарегистрировать расширение

    :param name: имя расширения
    :param ext: параметр может по сути содержать все, что угодно
    :param in_context: флаг указывает на то, что нужно создать инстанс в контексте инициализации TestCase
    """
    if in_context:
        _EXTENSIONS[name] = ModifyDict(
            cls=ext, args=args or tuple(), kwargs=kwargs or dict(),
        )
    else:
        _EXTENSIONS[name] = ext

    return ext


def clear():
    """
    Очистить хранимку расширений
    """
    global _EXTENSIONS
    _EXTENSIONS = {}
