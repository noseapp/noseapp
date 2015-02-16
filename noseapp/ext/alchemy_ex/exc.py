# -*- coding: utf-8 -*-


class BaseError(BaseException):
    """Базовый класс для формирования ошибок"""
    pass


class ValidationError(BaseError):
    """Ошибки валидации"""
    pass


class NotFound(BaseError):
    """Не найдено"""
    pass


class InvalidBindKey(BaseError):
    """
    Не найден ключ по которому нужно вытащить движок
    """
    pass
