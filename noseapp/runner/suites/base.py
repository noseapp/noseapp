# -*- coding: utf8 -*-

from nose.suite import ContextSuite


class BaseSuite(ContextSuite):
    """
    Base suite
    """

    def _run(self, result, orig):
        for test in self._tests:
                if result.shouldStop:
                    break
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
            self._run(result, orig)
        finally:
            self.has_run = True

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                self.error_context = 'teardown'
                result.addError(self, self._exc_info())
