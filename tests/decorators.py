# -*- coding: utf8 -*-

from unittest import TestCase


class TestFlowsDecorator(TestCase):
    """
    Test decorator for parametrize test method
    """

    @staticmethod
    def create_fake_case():
        from noseapp.decorators import flows

        class FakeCase(object):
            counter = 0

            @flows(1, 2, 3)
            def run(self, i):
                self.counter += i

        return FakeCase()

    def runTest(self):
        case = self.create_fake_case()
        case.run()

        self.assertEqual(case.counter, 6)
