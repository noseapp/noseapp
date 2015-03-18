=====
Suite
=====

Suite class is nose ContextSuite provider. Major task is collect test cases and build suite for TestRunner.


Simple example
--------------

::

    from noseapp import Suite


    suite = Suite(__name__)


Require extensions
------------------

You can extend TestCase class through suite. Use require param.

::

    suite = Suite(__name__, require=['my_extension_name'])


Set default require
-------------------

If all suites have same require, then create base class and use DEFAULT_REQUIRE constant.

::

    class MySuite(Suite):

        DEFAULT_REQUIRE = [
            'my_extension_name',
        ]


    suite = MySuite(__name__, require=['something_else'])


Mediator class
--------------

If is need change communication with nose library, you can set own mediator class.


::

    from noseapp.suite import TestCaseMediator


    class MyTestCaseMediator(TestCaseMediator):
        # your logic here
        pass


    class MySuite(Suite):

        mediator_class = MyTestCaseMediator
