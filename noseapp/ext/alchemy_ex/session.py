# -*- coding: utf-8 -*-

"""
Модуль обеспечивает связь между ORM и db engine
"""


_SESSION = None


def set(session):
    global _SESSION
    _SESSION = session


def get():
    if _SESSION is None:
        raise RuntimeError('working outside session scope')

    return _SESSION
