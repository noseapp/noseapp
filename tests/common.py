# -*- coding: utf-8 -*-

from unittest import TestCase


class SelfTest(TestCase):
    """
    Test of full cycle:
        * Create application
        * Call to callbacks
        * Config data
        * Tests to run
        * Shared extensions
        * Shared data

    Test given guarantee to application is stable working,
    but that's not means for test program api
    """

    def setUp(self):
        from testapp.app import create_app

        self.app = create_app(exit=False)
        self.assertTrue(self.app.run())

    def check_config(self):
        self.assertEqual(self.app.config.DEFAULT, 1)
        self.assertEqual(self.app.config.CONSTANT, 2)

    def check_callbacks(self):
        self.assertTrue(self.app.self_test.add_options_called)

        self.assertTrue(self.app.self_test.setup_app_called)
        self.assertTrue(self.app.self_test.teardown_app_called)

        self.assertTrue(self.app.self_test.setup_app_context_called)
        self.assertTrue(self.app.self_test.teardown_app_context_called)

        self.assertTrue(self.app.self_test.setup_suite_context_called)
        self.assertTrue(self.app.self_test.teardown_suite_context_called)

        self.assertTrue(self.app.self_test.setup_case_called)
        self.assertTrue(self.app.self_test.teardown_case_called)

        self.assertTrue(self.app.self_test.setup_case_class_called)
        self.assertTrue(self.app.self_test.teardown_case_class_called)

        self.assertTrue(self.app.self_test.suite_before_called)
        self.assertTrue(self.app.self_test.suite_after_called)
        self.assertTrue(self.app.self_test.pre_run_case_called)
        self.assertTrue(self.app.self_test.post_run_case_called)

    def check_was_worked(self):
        self.assertGreater(len(self.app.self_test.worked_cases), 0)

    def runTest(self):
        self.check_config()
        self.check_callbacks()
        self.check_was_worked()
