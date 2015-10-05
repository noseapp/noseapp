# -*- coding: utf-8 -*-

"""
Module for supporting py 2-3 versions.
"""

import sys


class PyVersionError(BaseException):
    pass


class UnSupportedError(PyVersionError):
    pass


IS_PYTHON_3 = sys.version_info >= (3, 0)
IS_PYTHON_2 = not IS_PYTHON_3


def check_py_version():
    error_mess = 'Unsupported py version. Need python 2.7 and greater.'

    if not IS_PYTHON_3 and not IS_PYTHON_2:
        raise PyVersionError(error_mess)

    if sys.version_info < (2, 7):
        raise PyVersionError(error_mess)


if IS_PYTHON_3:
    basestring = str
elif IS_PYTHON_2:
    basestring = basestring


if IS_PYTHON_3:
    unicode = str
elif IS_PYTHON_2:
    unicode = unicode
