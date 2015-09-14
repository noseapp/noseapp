# -*- coding: utf-8 -*-

from example.app.suite import Suite


suite = Suite(__name__, require=['random', 'settings'])


@suite.register
class ExampleCase(suite.TestCase):

    def test_one(self):
        # raise Exception('Fuck!')
        if self.settings.get_fail:
            self.assertTrue(False)
        self.assertTrue(True)

    @suite.skip('And that')
    def test_two(self):
        self.assertTrue(True)
