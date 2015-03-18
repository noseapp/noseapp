========
TestCase
========

Noseapp support own case classes only! Why? Because TestCase class must have "with_require" method. This method
is class wrapper for extension installation.


Simple Example
--------------

::

    from noseapp import Suite
    from noseapp import TestCase


    suite = Suite(__name__)


    @suite.register
    class MyTestCase(TestCase):

        def runTest(self):
            pass


Implements step by step
-----------------------

Realizing test script by steps.

::

    from noseapp import Suite
    from noseapp.case import step
    from noseapp import ScreenPlayCase


    suite = Suite(__name__)


    @suite.register
    class MyTestCase(ScreenPlayCase):

        @step(1, 'step description')
        def step_one(self):
            print 'Hello NoseApp!'

        @step(2, 'step 2 description')
        def step_two(self):
            print 'Just saying hi'


Use begin, finalize callbacks.
If exception in step method be raised, this method can not be called!

::

    @suite.register
    class MyTestCase(ScreenPlayCase):

        def begin(self):
            print('do something')

        @step(1, 'step description')
        def step_one(self):
            print('Hello NoseApp!')

        @step(2, 'step 2 description')
        def step_two(self):
            print('Just saying hi')

        def finalize(self):
            print('do something')


You can parametrize test flows.

::

    from noseapp.datastructures import ModifyDict as TestContext


    @suite.register
    class MyTestCase(ScreenPlayCase):

        FLOWS = (
            TestContext(
                name='NoseApp',
            ),
            TestContext(
                name='Tester',
            ),
        )

        @step(1, 'step description')
        def step_one(self, ctx):
            print 'Hello {}'.format(ctx.name)

        @step(2, 'step 2 description')
        def step_two(self, ctx):
            print 'Just saying hi, {}'.format(ctx.name)


Enable debug for steps.

::

    @suite.register
    class MyTestCase(ScreenPlayCase):

        USE_PROMPT = True

        # or

        def setUp(self):
            self.USE_PROMPT = True


ScreenPlayCase have error handle and formatting exception info. Exception message template:

::

    * {traceback}

    * History:
    {history}

    * Point:
    {case}.{method} -> Step {step} "{step_doc}"

    * Flow:
    {flow}

    * Raised:
    {raised}

    * Message:
    {message}
