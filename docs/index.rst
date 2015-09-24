Welcome to noseapp's documentation
==================================

.. toctree::
    :maxdepth: 2

    api
    example
    common

Installation
------------

::

    pip install noseapp


About
-----

This is framework for test development with complex logic around and based on nose library.


Async run
---------

* multiprocessing
* threading
* gevent


Quick start
===========

::

    import noseapp


    suite = noseapp.Suite('first_suite')


    @suite.register
    class TestCase(noseapp.TestCase):

        def test(self):
            # do something
            self.assertTrue(True)


    @suite.register
    class StepByStepCase(noseapp.ScreenPlayCase):

        def begin(self):
            pass

        @noseapp.step(1, 'comment to step')
        def step_one(self):
            self.assertTrue(True)

        @noseapp.step(2, 'comment to step')
        def step_two(self):
            self.assertTrue(True)

        def finalize(self):
            pass


    @suite.register
    def test_case(case):
        case.assertTrue(True)


    @suite.register(simple=True)
    def simple_test_case():
        assert True


    app = noseapp.NoseApp('example')
    app.register_suite(suite)

    app.run()
