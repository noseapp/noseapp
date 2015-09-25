Suite
=====

Suite class is provider for nose.suite.ContextSuite. Major task is collect test cases and construction suite to run.


Simple example
--------------

.. code-block:: python

    >>> from noseapp import Suite

    >>> suite = Suite(__name__)


Callbacks
---------

.. code-block:: python

    class MySuite(Suite):

        def setUp(self):
            # Will be called before run suite
            pass

        def tearDown(self):
            # Will be called after run suite
            pass


    suite = MySuite(__name__)


Require extensions
------------------

.. code-block:: python

    >>> suite = Suite(__name__, require=['extension_name'])
    >>> suite.ext('extension_name')


Set default require
-------------------

If all suites must have common require, then you can create base class and use DEFAULT_REQUIRE constant.

.. code-block:: python

    class MySuite(Suite):

        DEFAULT_REQUIRE = [
            'extension_name',
        ]


    suite = MySuite(__name__, require=['something_else'])
    suite.ext('extension_name')
    suite.ext('something_else')


Usage skip
----------

.. code-block:: python

    suite = Suite(__name__)


    @suite.register(skip='TODO: ...')  # skip class. you may use skip decorator for that.
    class MyTestCase(TestCase):

        @suite.skip('TODO: ...')
        def test_one(self):
            pass

        @suite.skip_if(True, 'Message')
        def test_two(self):
            pass

        @suite.skip_unless(False, 'Message')
        def test_three(self):
            pass


    @suite.register(skip='TODO: ...')
    def my_test(case):
        pass


    @suite.skip_if(True, 'Message')
    @suite.register(simple=True)
    def my_simple_test():
        pass


Add callbacks
-------------

.. code-block:: python

    suite = Suite(__name__)


    @suite.add_pre_run
    def pre_run_test(test):
        """
        :param test: instance of test case class
        """
        # Callback will be called before run test
        pass

    # or

    @suite.add_pre_run(lambda t: None)


    @suite.add_post_run
    def post_run_test(test):
        """
        :param test: instance of test case class
        """
        # Callback will be called after run test
        pass

    # or

    @suite.add_post_run(lambda t: None)


    @suite.add_setup
    def setup():
        pass

    # or

    @suite.add_setup(lambda: None)


    @suite.add_teardown
    def teardown():
        pass

    # or

    @suite.add_teardown(lambda: None)


them maybe more...


Test case class
---------------


.. code-block:: python

    from noseapp import TestCase


    class MyTestCase(TestCase):

        def assertCallable(self, obj, msg=None):
            self.assertTrue(callable(obj), (msg or 'not callable'))


    class MySuite(Suite):

        test_case_class = MyTestCase


    suite = MySuite('name')


    @suite.register
    def test_case(case):
        """
        :type case: MyTestCase
        """
        case.assertCallable(lambda: None)


    @suite.register
    class CheckCallable(suite.TestCase):

        def test(self):
            self.assertCallable(lambda: None)


Usage extensions
----------------

Extensions will be available after build suite only, usage callbacks for that.


.. code-block:: python

    class MySuite(Suite):

        DEFAULT_REQUIRE = [
            'example_ex_name',
        ]

        def setUp(self):
            extension = self.ext('example_ex_name')
            extension.do_something()

        def tearDown(self):
            extension = self.ext('example_ex_name')
            extension.do_something()


Suite management by context object
----------------------------------

.. code-block:: python

    from noseapp.suite.context import SuiteContext


    COMMON_REQUIRE = [
        'extension_name',
    ]


    def common_pre_run(case):
        case.do_something()


    def common_post_run(case):
        case.do_something()


    def common_setup():
        pass


    def common_teardown():
        pass


    class MySuiteContext(SuiteContext):

        def __init__(self, *require):
            super(MySuiteContext, self).__init__(list(require))

            self.require.extend(COMMON_REQUIRE)

            self.add_pre_run(common_pre_run)
            self.add_post_run(common_post_run)

            self.add_setup(common_setup)
            self.add_teardown(common_teardown)


    suite = Suite(__name__, context=MySuiteContext())

    suite2 = Suite(__name__, context=MySuiteContext('other_extension'))
