=====
Suite
=====

Suite class is provider for nose ContextSuite. Major task is collect test cases and construction suite to run.


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


Example
-------

::

    from noseapp import Suite


    class MySuite(Suite):

        DEFAULT_REQUIRE = ['example']

        def setUp(self):
            self.ext('example').do_something()

        def tearDown(self):
            self.ext('example').do_something()


    suite = MySuite(__name__)


Usage skip from suite instance
------------------------------

::

    suite = Suite(__name__)


      # skipIf, skipUnless
    @suite.register(skip='TODO: ...')
    class MyTestCase(TestCase):

        @suite.skip('TODO: ...')
        def test(self):
            pass


Add pre-post run for test cases
-------------------------------

Handler will be called before run

::

    suite = Suite(__name__)


    @suite.add_pre_run
    def pre_run_test(test):
        """
        :param test: instance of test case class
        """
        pass


    @suite.add_post_run
    def post_run_test(test):
        """
        :param test: instance of test case class
        """
        pass


them maybe more...


Add before, after
-----------------

You may add setup, teardown callbacks

::

    suite = Suite(__name__)


    @suite.add_before
    def setup():
        pass


    @suite.add_after
    def teardown():
        pass
