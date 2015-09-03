=====
Suite
=====

Suite class is provider for nose ContextSuite. Major task is collect test cases and construction suite for run.


Simple example
--------------

::

    from noseapp import Suite


    suite = Suite(__name__)


Require extensions
------------------

You can extend TestCase class by extension. Use require param.

::

    suite = Suite(__name__, require=['my_extension_name'])


Set default require
-------------------

If all suites must have common require, then you can create own base class and use DEFAULT_REQUIRE constant.

::

    class MySuite(Suite):

        DEFAULT_REQUIRE = [
            'my_extension_name',
        ]


    suite = MySuite(__name__, require=['something_else'])


Usage skip decorators from suite instance
-----------------------------------------

::

    suite = Suite(__name__)


    @suite.skip('TODO: ...')  # skipIf, skipUnless
    @suite.register
    class MyTestCase(TestCase):
        pass


Add handler for test cases
--------------------------

Handler will be called before run

::

    suite = Suite(__name__)


    @suite.add_handler
    def run_test_handler(test):
        """
        :param test: instance of test case class
        """
        pass


them maybe more...


Mediator class
--------------

If you want to change communication with nose library, so you can change mediator class.


::

    from noseapp.suite import TestCaseMediator


    class MyTestCaseMediator(TestCaseMediator):
        # your logic here
        pass


    class MySuite(Suite):

        mediator_class = MyTestCaseMediator
