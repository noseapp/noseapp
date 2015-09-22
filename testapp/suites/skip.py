# -*- coding: utf-8 -*-

from noseapp import Suite
from noseapp import TestCase


suite = Suite(__name__)


@suite.register
class TestCaseClassToSkip(TestCase):

    @suite.skip_if(True, 'Skip if True')
    def test_skip_if(self):
        pass

    @suite.skip_unless(False, 'Skip unless True')
    def test_skip_unless(self):
        pass


@suite.register(skip='Skip test case function')
def skip_test_function(case):
    pass


@suite.register(simple=True, skip='Skip simple function case')
def skip_simple_func_case():
    pass
