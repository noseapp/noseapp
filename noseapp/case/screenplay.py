# -*- coding: utf8 -*-

"""
Step by step case
"""

import re
import sys
import logging
import traceback
from functools import wraps
from six import with_metaclass

from noseapp.utils import pyv
from noseapp.case.base import TestCase


logger = logging.getLogger(__name__)


DOC_ATTRIBUTE_NAME = '__DOC__'
WEIGHT_ATTRIBUTE_NAME = '__WEIGHT__'
SCREENPLAY_ATTRIBUTE_NAME = '__SCREENPLAY__'

STEP_INFO_PATTERN = u'<{}.{}> Step {} "{}"'

EXCLUDE_METHOD_PATTERN = re.compile(
    r'^fail[A-Z]|^fail$|^assert[A-Z]|^assert_$',
)

ERROR_MESSAGE_FULL_TEMPLATE = u"""

* Traceback:
{traceback}

* History:
{history}

* Point:
{case}.{method} -> Step {step} "{step_doc}"

* Flow:
{flow}

* Raised:
{raised}

* Message:
{message}
"""


class StepFail(AssertionError):
    pass


class StepError(Exception):
    pass


def re_raise_exc(e, msg):
    """
    Re raise exception with new message

    :param e: exception instance
    :param msg: exception message
    """
    def error(m):
        if isinstance(e, AssertionError):
            return StepFail(m)
        return StepError(m)

    if pyv.IS_PYTHON_2:
        raise error(msg)

    _, _, tb = sys.exc_info()
    raise error(msg).with_traceback(tb)


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


def format_traceback(tb):
    """
    Delete first line of traceback.

    :param tb: traceback message
    """
    return u'\n'.join(tb.splitlines()[1:])


def unicode_string(s):
    try:
        return pyv.unicode(s)
    except UnicodeDecodeError as e:
        try:
            return pyv.unicode(s.decode('utf-8'))
        except AttributeError:  # for py 3 only
            raise e


def get_step_info(case, method):
    """
    :param case: TestCase instance
    :param method: step method

    :return: tuple
    """
    case_name = case.__class__.__name__
    try:
        method_name = method.__func__.__name__
    except AttributeError:
        method_name = method.__name__
    weight = getattr(method, WEIGHT_ATTRIBUTE_NAME)
    doc = getattr(method, DOC_ATTRIBUTE_NAME)

    return case_name, method_name, weight, doc


def get_exception_message(e):
    """
    Get message from exception instance

    :param e: exception instance
    """
    if hasattr(e, 'message'):
        return e.message
    return u''.join(e.args)


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


def run_step(case, method, flow=None):
    """
    Run step

    :param case: TestCase instance
    :param method: step method
    :param flow: from FLOWS property
    """
    case_name, method_name, weight, doc = get_step_info(case, method)
    step_info = STEP_INFO_PATTERN.format(
        case_name, method_name, weight, doc,
    )

    if case.USE_PROMPT:
        perform_prompt(case_name, method_name)

    logger.info(step_info)

    try:
        if flow is not None:
            method(case, flow)
        else:
            method(case)
    except BaseException as e:
        if not case.ERROR_MESSAGE_TEMPLATE:
            raise

        orig_tb = traceback.format_exc()
        history = u'\n'.join(case.__history)
        exc_cls_name = e.__class__.__name__

        if case.RENDER_ERROR_MESSAGE and pyv.IS_PYTHON_2:  # feature for python 2 only
            msg = case.render_error_message(
                history=unicode_string(history),
                case=unicode_string(case_name),
                method=unicode_string(method_name),
                step=unicode_string(weight),
                step_doc=unicode_string(doc),
                flow=unicode_string(flow),
                raised=unicode_string(exc_cls_name),
                traceback=unicode_string(format_traceback(orig_tb)),
                message=unicode_string(get_exception_message(e)),
            )
        else:
            msg = '<{}.{}(num={}, doc={}, flow={})> {}'.format(
                unicode_string(case_name),
                unicode_string(method_name),
                unicode_string(weight),
                unicode_string(doc),
                unicode_string(flow),
                unicode_string(
                    get_exception_message(e),
                ),
            )

        re_raise_exc(e, msg)


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

        if self.FLOWS and hasattr(self.FLOWS, '__iter__'):

            for flow in self.FLOWS:
                for step_method in steps:
                    _, _, step, doc = get_step_info(self, step_method)
                    self.__history.append(history_line.format(step, doc))

                    run_step(self, step_method, flow=flow)
                else:
                    self.__history = []

        else:

            for step_method in steps:
                _, _, step, doc = get_step_info(self, step_method)
                self.__history.append(history_line.format(step, doc))

                run_step(self, step_method)

        self.finalize()

    return run_test


def build_class(cls):
    """
    Collect step methods and build class
    """
    steps = []

    attributes = (
        a for a in dir(cls)
        if not a.startswith('_')
        and
        EXCLUDE_METHOD_PATTERN.search(a) is None
    )

    for atr in attributes:
        method = getattr(cls, atr, None)
        if hasattr(method, SCREENPLAY_ATTRIBUTE_NAME):
            steps.append(method)

    if steps:
        steps.sort(
            key=lambda m: getattr(m, WEIGHT_ATTRIBUTE_NAME),
        )
        cls.runTest = make_run_test(steps)

    return cls


class ScreenPlayCaseMeta(type):
    """
    Build step methods and create runTest
    """

    def __new__(mcs, name, bases, dct):
        steps = []

        cls = type.__new__(mcs, name, bases, dct)

        attributes = (
            a for a in dir(cls)
            if not a.startswith('_')
            and
            EXCLUDE_METHOD_PATTERN.search(a) is None
        )

        for atr in attributes:
            method = getattr(cls, atr, None)
            if hasattr(method, SCREENPLAY_ATTRIBUTE_NAME):
                steps.append(method)

        if steps:
            steps.sort(
                key=lambda m: getattr(m, WEIGHT_ATTRIBUTE_NAME),
            )
            cls.runTest = make_run_test(steps)

        return cls


class ScreenPlayCase(with_metaclass(ScreenPlayCaseMeta, TestCase)):
    """
    Test case for implementation by step script

    Usage::

        class CaseExample(ScreenPlayCase):

            USE_PROMPT = True  # usage interactive debug

            @step(1, 'description')
            def step_1(self):
                self.assertTrue(True)

            @step(2, 'description')
            def step_2(self):
                self.assertTrue(True)


        class CaseParametrizeExample(ScreenPlayCase):

            FLOWS = (
              1, 2, 3
            )

            @step(1, u'Step 1')
            def step_1(self, i):
                self.assertGreater(i, 0)

            @step(2, u'Step 2')
            def step_2(self, i):
                self.assertGreater(i, 0)


        class SimpleCaseClass(ScreenPlayCase):

            def test(self):
                pass
    """

    FLOWS = None
    USE_PROMPT = False

    RENDER_ERROR_MESSAGE = False
    ERROR_MESSAGE_TEMPLATE = ERROR_MESSAGE_FULL_TEMPLATE

    @property
    def error_template_params(self):
        """
        Params for ERROR_MESSAGE_TEMPLATE render.

        :rtype: dict
        """
        return {}

    def begin(self):
        """
        Callback. Will be called before run steps.
        """
        pass

    def finalize(self):
        """
        Callback. Will be called after run steps.
        If exception at step method will be raised then
        method can't to be called.
        """
        pass

    def render_error_message(self, **kwargs):
        """
        Render error message by template.
        """
        kwargs.update(self.error_template_params)
        message = unicode_string(self.ERROR_MESSAGE_TEMPLATE)

        for k, v in kwargs.items():
            message = message.replace(u'{%s}' % k, v)

        return message.encode('utf-8', 'replace')
