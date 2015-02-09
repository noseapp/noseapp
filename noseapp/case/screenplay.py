# -*- coding: utf8 -*-

"""
Модуль позволяет оформлять TestCase, как пошаговый сценарий.

Пример:

    class CaseExample(ScreenPlayCase):

        USE_PROMPT = True  # использовать интерактивный отладчик или нет

        @step(1, u'Шаг 1')
        def step_1(self):
            self.assertTrue(True)

        @step(2, u'Шаг 2')
        def step_2(self):
            self.assertTrue(True)


    class CaseParametrizeExample(ScreenPlayCase):

        PARAMETRIZE = (  # параметризация сценария
            1, 2, 3
        )

        @step(1, u'Шаг 1')
        def step_1(self, i):
            self.assertGreater(i, 0)

        @step(2, u'Шаг 2')
        def step_2(self, i):
            self.assertGreater(i, 0)
"""

import re
import sys
import logging
from functools import wraps

from noseapp.case.base import TestCase


logger = logging.getLogger(__name__)


DOC_ATTRIBUTE_NAME = '__DOC__'
WEIGHT_ATTRIBUTE_NAME = '__WEIGHT__'
SCREENPLAY_ATTRIBUTE_NAME = '__SCREENPLAY__'

USE_PROMPT_ATTRIBUTE_NAME = 'USE_PROMPT'
PARAMETRIZE_ATTRIBUTE_NAME = 'PARAMETRIZE'

STEP_INFO_PATTERN = u'<{}.{}> Step {} "{}"'
ERROR_INFO_PATTERN = u'<{}.{}> ({}: "{}") Step {} "{}"\nWith params: {}'

EXCLUDE_METHOD_PATTERN = re.compile(
    r'^fail[A-Z]|^fail$|^assert[A-Z]|^assert_$',
)


class StepError(BaseException):
    """
    Ошбка при выполнении шага
    """
    pass


class StepFail(AssertionError):
    """
    Упавший assert при выполнении шага
    """
    pass


def step(num, doc=''):
    """
    Декоратор. Подписывает метод как шаг
    в последовательном сценарии TestCase

    :param num: номер шага
    :param doc: строка документации
    """

    def wrapper(f):
        if not isinstance(num, int):
            raise ValueError('step num mast be int only')

        setattr(f, DOC_ATTRIBUTE_NAME, doc)
        setattr(f, WEIGHT_ATTRIBUTE_NAME, num)
        setattr(f, SCREENPLAY_ATTRIBUTE_NAME, '')

        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def get_step_info(case, method):
    """
    Возвращает информацию о методе реализующим шаг сценария

    :param case: инстанс TestCase
    :param method: step метод
    """
    case_name = case.__class__.__name__
    method_name = method.__func__.__name__
    weight = getattr(method, WEIGHT_ATTRIBUTE_NAME)
    doc = getattr(method, DOC_ATTRIBUTE_NAME)

    return case_name, method_name, weight, doc


def perform_prompt(case_name, method_name, exit_code=0):
    """
    Останавливает выполнение. Предлагает продолжить работу,
    завершить работу или подрубить отладчик

    :param case_name: имя case класса
    :param method_name: имя метода шага
    :param exit_code: с каким кодом произвести выход
    """
    commands = {  # набор доступных команд в prompt
        'exit': 'q',
        'debug': 'd',
        'continue': 'c',
    }
    prompt = '>> {}.{} [{}]: '.format(
        case_name, method_name, ', '.join([c for _, c in commands.items()])
    )
    command = raw_input(prompt).strip()

    if command == commands['exit']:
        sys.exit(exit_code)
    elif command == commands['debug']:
        try:
            import ipdb as pdb
        except ImportError:
            import pdb

        pdb.set_trace()


def run_step(case, method, params=None):
    """
    Функция реализует запуск метода-шага

    :param case: инстанс TestCase
    :param method: step метод
    :param params: параметры для шага из PARAMETRIZE
    """
    case_name, method_name, weight, doc = get_step_info(case, method)
    step_info = STEP_INFO_PATTERN.format(
        case_name, method_name, weight, doc,
    )

    if getattr(case, USE_PROMPT_ATTRIBUTE_NAME, False):
        perform_prompt(case_name, method_name)

    logger.info(step_info)

    try:
        if params is not None:
            method(case, params)
        else:
            method(case)
    # ловим ошибки и форматируем их вывод
    except AssertionError as e:
        raise StepFail(
            ERROR_INFO_PATTERN.format(
                case_name,
                method_name,
                e.__class__.__name__,
                e.message,
                weight,
                doc,
                str(params),
            ).encode('utf-8', 'replace'),  # нужно для того, чтобы
            # русские буквы не были кракозябрами
        )
    except Exception as e:
        raise StepError(
            ERROR_INFO_PATTERN.format(
                case_name,
                method_name,
                e.__class__.__name__,
                e.message,
                weight,
                doc,
                str(params)
            ).encode('utf-8', 'replace'),
        )


def make_run_test(steps):
    """
    Создает метод runTest

    :param steps: список методов-шагов
    """

    def run_test(self):
        """
        Функция реализует последовательный запуск
        методов подисанных step декоратором
        """
        parametrize = getattr(self, PARAMETRIZE_ATTRIBUTE_NAME, None)

        if parametrize and hasattr(parametrize, '__iter__'):

            for params in parametrize:
                for step_method in steps:
                    run_step(self, step_method, params=params)

        else:

            for step_method in steps:
                run_step(self, step_method)

    return run_test


class ScreenPlayCaseMeta(type):
    """
    Метакласс собирает все методы которые подписаны,
    как шаги декоратором step, сортирует и создает метод
    runTest, который реализует последовательный запуск.
    """

    def __new__(cls, name, bases, dct):
        instance = type.__new__(cls, name, bases, dct)

        steps = []

        attributes = (  # готовим генератор который будет
            # отсеивать заведомо невалидные атрибуты
            a for a in dir(instance)
            if not a.startswith('_')
            and
            EXCLUDE_METHOD_PATTERN.search(a) is None
        )

        for atr in attributes:
            method = getattr(instance, atr, None)
            if hasattr(method, SCREENPLAY_ATTRIBUTE_NAME):
                steps.append(method)

        if steps:
            steps.sort(
                key=lambda m: getattr(m, WEIGHT_ATTRIBUTE_NAME),
            )
            instance.runTest = make_run_test(steps)

        return instance


class ScreenPlayCase(TestCase):
    """
    Базовый TestCase класс с готовой
    реализацией пошагового сценария внутри
    """

    __metaclass__ = ScreenPlayCaseMeta

    USE_PROMPT = False
    PARAMETRIZE = None
