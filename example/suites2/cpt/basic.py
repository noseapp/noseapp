# -*- coding: utf-8 -*-

from noseapp.case import step

from example.app.suite import Suite


suite = Suite(__name__, require=['random', 'settings'])


@suite.add_pre_run
def handler(case):
    case.prepare()


@suite.add_before
def setup():
    print 'Setup suite'


@suite.add_after
def teardown():
    print 'Teardown suite'


@suite.register
def the_first_test(case):
    if case.settings.get_fail:
        case.assertTrue(False)
    case.assertGreater(case.random.randint(1, 100), 0)


@suite.register
def the_two_test(case):
    case.assertTrue(case.random.randint(1, 100) > 0 < 101)


@suite.register
class ExampleCase(suite.TestCase):

    def test_one(self):
        if self.settings.get_fail:
            self.assertTrue(False)
        self.assertTrue(True)

    def test_two(self):
        self.assertTrue(True)


@suite.register
class ExampleStepsImplementation(suite.TestCase):

    def begin(self):
        self.num = self.random.randint(1, 100)

    @step(1, 'First step')
    def first(self):
        self.assertGreater(self.num, 0)

    @step(2, 'Second step')
    def second(self):
        if self.settings.get_fail:
            self.assertTrue(False)
        self.assertTrue(True)
