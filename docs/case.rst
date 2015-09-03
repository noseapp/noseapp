========
TestCase
========

noseapp is supporting own test case class only!
In order to your test case class will be have support of noseapp, you are must to inherit mixin class noseapp.case.base.ToNoseAppTestCase


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


Implement step by step
----------------------

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


Base class give you callback method.
If exception in step method will be raised, finalize method can not be called!

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


You can parametrize flow step.

::

    from noseapp.datastructures import Context


    @suite.register
    class MyTestCase(ScreenPlayCase):

        FLOWS = (
            Context(
                name='NoseApp',
            ),
            Context(
                name='Tester',
            ),
        )

        @step(1, 'step description')
        def step_one(self, ctx):
            print 'Hello {}'.format(ctx.name)

        @step(2, 'step 2 description')
        def step_two(self, ctx):
            print 'Just saying hi, {}'.format(ctx.name)


Debug for steps.

::

    @suite.register
    class MyTestCase(ScreenPlayCase):

        USE_PROMPT = True

        # or

        def setUp(self):
            self.USE_PROMPT = True


Exception message format. You can change it. Use ScreenPlayCase.EXCEPTION_MESSAGE_FORMAT.
This is default template.

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
