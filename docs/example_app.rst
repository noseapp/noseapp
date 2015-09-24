Application
===========


Simple example
--------------

.. code-block:: python

    import noseapp

    app = noseapp.NoseApp('name')
    ...



Callbacks
---------


.. code-block:: python

    class MyTestApplication(noseapp.NoseApp):

        def setUpApp(self):
            # Your code for setup application here
            # Will be called after create instance
            pass

        def tearDownApp(self):
            # Will be called after get out of test program
            # Do it something here if you are needing
            pass

        def setUp(self):
            # Will be called before run suites
            pass

        def tearDown(self):
            # Will be called after runn suites

        def addOptions(self, parser):
            # add options to command line
            pass


Shared extensions
-----------------

Any callable object can be as extension. Result will be getting by required.


.. code-block:: python

    def simple_extension(*args, **kwargs)
        return (args, kwargs)


    app = noseapp.NoseApp('example')
    app.shared_extension(name='example', cls=simple_extension, args=(1, 2), kwargs={'a': 1})


    suite = noseapp.Suite('test', require=['example'])


    @suite.register
    def test_example(case):
        print case.ext('example')


    suite2 = noseapp.Suite('example_2')


    @suite2.register(require=['example'])
    def test_example_2(case):
        print case.ext('example')


Shared data
-----------

Instance will be getting copy of data


.. code-block:: python

    app = noseapp.NoseApp('example')
    app.shared_data('data', dict(a=1, b=2))


    suite = noseapp.Suite('test', require=['data'])


    @suite.register
    def test_example(case):
        print case.ext('data')


Register suites
---------------


.. code-block:: python

    app = noseapp.NoseApp('app')
    suite  = noseapp.Suite('suite')

    app.register_suite(suite)
    # or
    app.register_suites([suite])


Load suites
-----------

When you are using auto load suite sys.path get path to your folder for importing packages and modules.
We are recommend use module.__name__ as suite name if you are using that.


.. code-block:: python

    app = noseapp.NoseApp('app')
    app.load_suites('/absolute/path/to/suites')


Add callbacks to application instance
-------------------------------------


.. code-block:: python

    def setup():
        pass


    def teardown():
        pass


    app = noseapp.NoseApp('app')

    app.add_setup(setup)
    app.add_teardown(teardown)


Master and sub applications
---------------------------

Application can be as master and sub application. Sub application can't be running, it's context storage in fact.
So, let see example...

.. code-block:: python

    sub_app = noseapp.NoseApp.as_sub_app('sub')
    master_app = noseapp.NoseApp.as_master_app('master', sub_app)

    master_app.run()


This is alternative record

.. code-block:: python

    sub_app = noseapp.NoseApp('sub', is_sub_app=True)
    master_app = noseapp.NoseApp('master', sub_apps=[sub_app])

    master_app.run()


Merge context between applications
----------------------------------

.. code-block:: python

    from noseapp.app.context import merge_context


    sub_app_one = noseapp.NoseApp.as_sub_app('sub_one')
    sub_app_two = noseapp.NoseApp.as_sub_app('sub_two')

    # plugins and callbacks is merged here
    main_app = noseapp.NoseApp.as_master_app('master', sub_app_one, sub_app_two)

    sub_app_one.load_suites('/absolute/path/to/suites')
    sub_app_two.load_suites('/absolute/path/to/suites')

    merge_context(master_app, merge_suites=True)

    # if main app should load suites then...
    # main_app.load_suites('/absolute/path/to/suites', merge_suites=True)
    # suites will be merged by merge_suites flag. This available for master application only.
