# -*- coding: utf8 -*-

import sys

from nose.suite import ContextSuite


def get_suite_master_id(suite):
    """
    Get id of master process
    """
    return suite._BaseSuite__master_id


class SuitePerformer(object):
    """
    Perform run suite
    """

    def __init__(self, suite, result, orig):
        self.orig = orig
        self.suite = suite
        self.result = result

    def run_one_test(self, test):
        """
        One test of suite to run
        """
        for callback in self.suite.pre_run_handlers:
            try:
                callback(test.test)
            except KeyboardInterrupt:
                raise
            except:
                self.orig.addError(test, sys.exc_info())
                return

        test(self.orig)

        for callback in self.suite.post_run_handlers:
            try:
                callback(test.test)
            except KeyboardInterrupt:
                raise
            except:
                self.orig.addError(test, sys.exc_info())

    def __call__(self, **kwargs):
        for test in self.suite.tests:
            if self.result.shouldStop:
                break

            if isinstance(test, BaseSuite):
                test.run(self.result, **kwargs)
                continue

            self.run_one_test(test)


class BaseSuite(ContextSuite):
    """
    Base suite
    """

    performer_class = SuitePerformer

    def __init__(self, *args, **kwargs):
        self.__master_id = id(self)
        self.__pre_run_handlers = kwargs.pop('pre_run_handlers', [])
        self.__post_run_handlers = kwargs.pop('post_run_handlers', [])

        super(BaseSuite, self).__init__(*args, **kwargs)

    @property
    def tests(self):
        return self._tests

    @property
    def pre_run_handlers(self):
        return self.__pre_run_handlers

    @property
    def post_run_handlers(self):
        return self.__post_run_handlers

    def run(self, result, **kwargs):
        if self.resultProxy:
            result, orig = self.resultProxy(result, self), result
        else:
            result, orig = result, result

        try:
            self.setUp()
        except KeyboardInterrupt:
            raise
        except:
            self.error_context = 'setup'
            result.addError(self, self._exc_info())
            return

        try:
            self.performer_class(self, result, orig)(**kwargs)
        finally:
            self.has_run = True

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                self.error_context = 'teardown'
                result.addError(self, self._exc_info())
