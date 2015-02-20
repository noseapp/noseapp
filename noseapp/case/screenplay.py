# -*- coding: utf8 -*-

"""
=================
Step by step case
=================

Example::

  class CaseExample(ScreenPlayCase):

    USE_PROMPT = True  # usage interactive debug

    @step(1, 'description')
    def step_1(self):
      self.assertTrue(True)

    @step(2, 'description')
    def step_2(self):
      self.assertTrue(True)


  class CaseParametrizeExample(ScreenPlayCase):

    PARAMETRIZE = (
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

STEP_INFO_PATTERN = u'<{}.{}> Step {} "{}"'

ERROR_INFO_PATTERN = u"""

* History:
{}

* Point:
{}.{} -> Step {} "{}"

* Params:
{}

* Raise:
{}

* Message:
{}
"""

EXCLUDE_METHOD_PATTERN = re.compile(
    r'^fail[A-Z]|^fail$|^assert[A-Z]|^assert_$',
)


class StepError(BaseException):
    pass


class StepFail(AssertionError):
    pass


def step(num, doc=''):
    """
    Decorator. Use wrapper method as case step.

    :param num: step num
    :type num: int
    :param doc: step description
    :type doc: str, unicode
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
    :param case: TestCase instance
    :param method: step method

    :return: tuple
    """
    case_name = case.__class__.__name__
    method_name = method.__func__.__name__
    weight = getattr(method, WEIGHT_ATTRIBUTE_NAME)
    doc = getattr(method, DOC_ATTRIBUTE_NAME)

    return case_name, method_name, weight, doc


def perform_prompt(case_name, method_name, exit_code=0):
    """
    Interactive mode for debug

    :param case_name: case class name
    :param method_name: step method name
    :param exit_code: exit code
    """
    commands = {  # prompt commands
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
    Run step

    :param case: TestCase instance
    :param method: step method
    :param params: params from PARAMETRIZE property
    """
    case_name, method_name, weight, doc = get_step_info(case, method)
    step_info = STEP_INFO_PATTERN.format(
        case_name, method_name, weight, doc,
    )

    if case.USE_PROMPT:
        perform_prompt(case_name, method_name)

    logger.info(step_info)

    try:
        if params is not None:
            method(case, params)
        else:
            method(case)
    # handle errors
    except AssertionError as e:
        raise StepFail(
            ERROR_INFO_PATTERN.format(
                u'\n'.join(case.__history),
                case_name,
                method_name,
                weight,
                doc,
                params,
                e.__class__.__name__,
                e.message,
            ).encode('utf-8', 'replace'),
        )
    except Exception as e:
        raise StepError(
            ERROR_INFO_PATTERN.format(
                u'\n'.join(case.__history),
                case_name,
                method_name,
                weight,
                doc,
                params,
                e.__class__.__name__,
                e.message,
            ).encode('utf-8', 'replace'),
        )


def make_run_test(steps):
    """
    Create runTest method

    :param steps: steps list
    """

    def run_test(self):
        run_test.__doc__ = self.__doc__

        self.begin()

        self.__history = []
        history_line = u'{}. {}'

        if self.PARAMETRIZE and hasattr(self.PARAMETRIZE, '__iter__'):

            for params in self.PARAMETRIZE:
                for step_method in steps:
                    _, _, step, doc = get_step_info(self, step_method)
                    self.__history.append(history_line.format(step, doc))

                    run_step(self, step_method, params=params)
                else:
                    self.__history = []

        else:

            for step_method in steps:
                _, _, step, doc = get_step_info(self, step_method)
                self.__history.append(history_line.format(step, doc))

                run_step(self, step_method)

        self.finalize()

    return run_test


class ScreenPlayCaseMeta(type):
    """
    Build step methods and create runTest
    """

    def __new__(cls, name, bases, dct):
        instance = type.__new__(cls, name, bases, dct)

        steps = []

        attributes = (
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
    Base TestCase class. Enjoy :)
    """

    __metaclass__ = ScreenPlayCaseMeta

    USE_PROMPT = False
    PARAMETRIZE = None

    def begin(self):
        """
        Call before run steps
        """
        pass

    def finalize(self):
        """
        Call after run steps.
        If exception in step method be raised,
        this method can not be called.
        """
        pass
