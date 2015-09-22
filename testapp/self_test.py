# -*- coding: utf-8 -*-


class SelfTestEx(object):

    name = 'self_test'

    setup_case_class_called = False
    teardown_case_class_called = False

    def __init__(self):
        self.worked_cases = []

        self.add_options_called = False

        self.setup_app_called = False
        self.teardown_app_called = False

        self.setup_app_context_called = False
        self.teardown_app_context_called = False

        self.setup_suite_context_called = False
        self.teardown_suite_context_called = False

        self.setup_case_called = False
        self.teardown_case_called = False

        self.suite_before_called = False
        self.suite_after_called = False

        self.pre_run_case_called = False
        self.post_run_case_called = False

    def __call__(self):
        return self
