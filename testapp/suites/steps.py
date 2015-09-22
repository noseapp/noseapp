# -*- coding: utf-8 -*-

from noseapp import step
from noseapp import Suite
from noseapp import ScreenPlayCase


suite = Suite(__name__)


@suite.add_post_run
def post_run(case):
    case.assertFalse(hasattr(case, 'num'))


@suite.register
class StepByStepCase(ScreenPlayCase):

    def begin(self):
        self.num = 1

    @step(1, u'step one')
    def one(self):
        self.num += 1

    @step(2, u'step two')
    def two(self):
        self.assertEqual(self.num, 2)

    def finalize(self):
        del self.num


assert len(suite.test_cases) == 1
