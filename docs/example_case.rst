Test case
=========

noseapp is supporting own test case class only!
In order to your test case class will be have support of noseapp, you are must to inherit mixin class noseapp.case.base.ToNoseAppTestCase


Simple Example
--------------

.. code-block:: python

    from noseapp import Suite
    from noseapp import TestCase


    suite = Suite(__name__)


    @suite.register
    class MyTestCase(TestCase):

        def runTest(self):
            self.assertTrue(True)


    @suite.register
    def my_test_case(case):
        case.assertTrue(True)


    @suite.register(simple=True)
    def my_simple_test_case():
        assert True


Require extension
-----------------

.. code-block:: python

    suite = Suite(__name__, require=['extension_name'])


    @suite.register
    class MyTestCase(TestCase):

        def setUp(self):
            extension = self.ext('extension_name')
            extension.do_something()


    suite2 = Suite(__name__)


    @suite.register(require=['extension_name'])
    def my_test(case):
        extension = case.ext('extension_name')
        extension.do_something()


Implement step by step
----------------------

.. code-block:: python

    from noseapp import step
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


Base class give you callbacks methods.
If exception in step method will be raised, finalize method can not be called!

.. code-block:: python

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

.. code-block:: python

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
            print 'Just say hi, {}'.format(ctx.name)


Debug for steps.

.. code-block:: python

    @suite.register
    class MyTestCase(ScreenPlayCase):

        USE_PROMPT = True

        # or

        def setUp(self):
            self.USE_PROMPT = True


Exception message template. You can change it. Use ScreenPlayCase.ERROR_MESSAGE_TEMPLATE for that. Parameters in template isn't necessarily required.
 This is full template:

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
