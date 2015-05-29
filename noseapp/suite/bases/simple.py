# -*- coding: utf8 -*-

from nose.suite import ContextSuite


class RunSuite(object):

    def __init__(self, suite, result, orig):
        self._orig = orig
        self._suite = suite
        self._result = result

    def run_test(self, test):
        for handler in self._suite.handlers:
            try:
                handler(test.test)
            except KeyboardInterrupt:
                raise
            except:
                self._suite.error_context = 'setup'
                self._orig.addError(self, self._suite._exc_info())
                return

        test(self._orig)

    def perform(self):
        for test in self._suite.tests:
            if self._result.shouldStop:
                break

            self.run_test(test)


class BaseSuite(ContextSuite):
    """
    Base suite
    """

    run_suite_class = RunSuite

    def __init__(self, *args, **kwargs):
        self._handlers = kwargs.pop('handlers', [])

        super(BaseSuite, self).__init__(*args, **kwargs)

    @property
    def tests(self):
        return self._tests

    @property
    def handlers(self):
        return self._handlers

    def run(self, result):
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
            runner = self.run_suite_class(self, result, orig)
            runner.perform()
        finally:
            self.has_run = True

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                self.error_context = 'teardown'
                result.addError(self, self._exc_info())
