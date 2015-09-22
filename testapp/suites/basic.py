# -*- coding: utf-8 -*-

from testapp.suite import MySuite
from testapp.case import MyTestCase


suite = MySuite(__name__)


@suite.add_before
def before():
    suite.ext('self_test').suite_before_called = True


@suite.add_after
def after():
    suite.ext('self_test').suite_after_called = True


@suite.add_pre_run
def pre_run(case):
    assert isinstance(case, MyTestCase)
    suite.ext('self_test').pre_run_case_called = True


@suite.add_post_run
def post_run(case):
    assert isinstance(case, MyTestCase)
    suite.ext('self_test').post_run_case_called = True


@suite.register
class CaseLikeClass(MyTestCase):

    def runTest(self):
        self.ext('self_test').worked_cases.append(self)

        self.assertFalse(self.ext('settings').debug)
        self.assertFalse(self.ext('settings').other_flag)


@suite.register
def case_like_func(case):
    case.ext('self_test').worked_cases.append(case)


@suite.register(simple=True)
def case_like_simple_func():
    suite.ext('self_test').worked_cases.append(case_like_simple_func)


assert len(suite.test_cases) == 3
