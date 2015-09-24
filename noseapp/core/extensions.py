# -*- coding: utf-8 -*-

"""
Tmp storage for extensions
"""

from copy import deepcopy
from contextlib import contextmanager

from noseapp.datastructures import ModifyDict as Transport


_EXTENSIONS = {}

WAS_INSTALLATION = False


class ExtensionNotFound(LookupError):
    pass


class ExtensionNotRequired(BaseException):
    pass


class InstallationError(BaseException):
    pass


@contextmanager
def installation():
    """
    Extensions must be installed only once.
    """
    global WAS_INSTALLATION

    if WAS_INSTALLATION:
        raise InstallationError('Extensions is already installed')

    yield

    clear()
    WAS_INSTALLATION = True


def get(name):
    """
    Get extension by name

    :param name: extension name
    :type name: basestring
    """
    try:
        ext = _EXTENSIONS[name]

        if ext.__class__ is Transport:
            return ext.cls(*ext.args, **ext.kwargs)

        return deepcopy(ext)
    except KeyError:
        raise ExtensionNotFound(name)


def set(name, ext, to_transport=False, args=None, kwargs=None):
    """
    Register extension in tmp storage

    :param name: extension name
    :type name: basestring
    :param ext: any objects
    :param to_transport: if True, create instance object with calling get function
    :type in_context: bool
    """
    if to_transport:
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
