# -*- coding: utf8 -*-

from nose.suite import ContextSuite


def run_test(suite, test, orig):
    for callback in suite.pre_run_handlers:
        try:
            callback(test.test)
        except KeyboardInterrupt:
            raise
        except:
            suite.error_context = 'setup'
            orig.addError(suite, suite._exc_info()())
            return

    test(orig)

    for callback in suite.post_run_handlers:
        try:
            callback(test.test)
        except KeyboardInterrupt:
            raise
        except:
            suite.error_context = 'teardown'
            orig.addError(suite, suite._exc_info()())


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
        self.__pre_run_handlers = kwargs.pop('pre_run_handlers', [])
        self.__post_run_handlers = kwargs.pop('post_run_handlers', [])

        super(BaseSuite, self).__init__(*args, **kwargs)

    @property
    def tests(self):
        return [t for t in self._tests]

    @property
    def pre_run_handlers(self):
        return self.__pre_run_handlers

    @property
    def post_run_handlers(self):
        return self.__post_run_handlers

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
