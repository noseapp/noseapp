# -*- coding: utf8 -*-

from nose.suite import ContextSuite


def run_test(suite, test, orig):
    for handler in suite.handlers:
        try:
            handler(test.test)
        except KeyboardInterrupt:
            raise
        except:
            suite.error_context = 'setup'
            orig.addError(suite, suite.exc_info())
            return

    test(orig)


def perform_chain(suite, result, orig, pool=None):
    for test in suite.tests:
        if result.shouldStop:
            break

        if isinstance(test, BaseSuite):
            test.run(result, pool=pool)
            continue

        run_test(suite, test, orig)


class BaseSuite(ContextSuite):
    """
    Base suite
    """

    perform_chain = perform_chain

    def __init__(self, *args, **kwargs):
        self._handlers = kwargs.pop('handlers', [])

        super(BaseSuite, self).__init__(*args, **kwargs)

    @property
    def tests(self):
        return self._tests

    @property
    def handlers(self):
        return self._handlers

    def exc_info(self):
        return self._exc_info()

    def run(self, result, pool=None):
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
            self.perform_chain(result, orig, pool=pool)
        finally:
            self.has_run = True

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                self.error_context = 'teardown'
                result.addError(self, self._exc_info())
