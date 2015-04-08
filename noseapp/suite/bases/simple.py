# -*- coding: utf8 -*-

from nose.suite import ContextSuite


class BaseSuite(ContextSuite):
    """
    Base suite
    """

    def __init__(self, *args, **kwargs):
        self._handlers = kwargs.pop('handlers', [])

        super(BaseSuite, self).__init__(*args, **kwargs)

    def _run_suite_handler(self, result, orig):
        for test in self._tests:
                if result.shouldStop:
                    break
                self._run_test_handler(test, orig)

    def _run_test_handler(self, test, orig):
        for handler in self._handlers:
            try:
                handler(test.test)
            except KeyboardInterrupt:
                raise
            except:
                self.error_context = 'setup'
                orig.addError(self, self._exc_info())
                return

        test(orig)

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
            self._run_suite_handler(result, orig)
        finally:
            self.has_run = True

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                self.error_context = 'teardown'
                result.addError(self, self._exc_info())
