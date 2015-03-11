# -*- coding: utf-8 -*-

"""
Tmp storage for extensions
"""

from copy import deepcopy

from noseapp.datastructures import ModifyDict as Transport


_EXTENSIONS = {}


class ExtensionNotFound(BaseException):
    pass


class ExtensionNotRequired(BaseException):
    pass


def get(name, require=None):
    """
    Get extension by name

    :param name: extension name
    :type name: basestring
    :param require: allow extensions list
    :type require: list or tuple
    """
    if require is not None and name not in require:
        raise ExtensionNotRequired(name)

    try:
        ext = _EXTENSIONS[name]

        if ext.__class__ is Transport:
            return ext.cls(*ext.args, **ext.kwargs)

        return deepcopy(ext)
    except KeyError:
        raise ExtensionNotFound(name)


def set(name, ext, in_context=False, args=None, kwargs=None):
    """
    Register extension in tmp storage

    :param name: extension name
    :type name: basestring
    :param ext: any objects
    :param in_context: if True, create instance object with call get function
    :type in_context: bool
    """
    if in_context:
        _EXTENSIONS[name] = Transport(
            cls=ext, args=args or tuple(), kwargs=kwargs or dict(),
        )
    else:
        _EXTENSIONS[name] = ext

    return ext


def clear():
    """
    Clear tmp
    """
    global _EXTENSIONS
    _EXTENSIONS = {}
