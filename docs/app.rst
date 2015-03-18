===========
Application
===========

Application is initialization point for service test cases through suites, as well for prepare test infrastructure.

 :And so...:

 What are the objectives decided with Application?

 * expand cases with extensions
 * prepare test infrastructure


Initialization
--------------

For initialization your application, base class implemented "initialize" callback method.

::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def initialize(self):
            # my script here...


Configuration
-------------

Use python module for configuration storage

::

    # this file as etc.base

    DEBUG = False
    # ...


::

    app = MyTestApplication(config='etc.base')
    # or by file path
    app = MyTestApplication(config='/home/user/project/etc/base.py')

Use config property inside application class. Config will build before call initialize method.


Shared extensions
-----------------

You can expand test cases from application. Extension must be class or function. After calling extension result will be
available by name in your test case as property.

::

    from random import randint

    from noseapp import NoseApp


    class ExampleExtension(object):

        name = 'rand'

        def __init__(self, a, b):
            self._a = a
            self._b = b

        def get_random(self):
            return randint(self._a, self._b)


    class MyTestApplication(NoseApp):

        def initialize(self):
            self.setup_example_ex()

        def setup_example_ex(self):
            self.shared_extension(
                cls=ExampleExtension,
                args=(1, 1000),
            )


Shared data
-----------

Sometimes, may be needed configuration for test cases from application. You can shared dictionary, list, tuple
or your data structures. Data will be copied during installation.

::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def initialize(self):
            self.setup_case_settings()

        def setup_case_settings(self):
            case_settings = {
                'hello': 'world',
            }
            self.shared_data('settings', case_settings)


Callbacks
---------

You can use callback methods for prepare test infrastructure.

::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def before(self):
            # This callback will be called before run tests
            pass

        def after(self):
            # This callback will be called after run tests
            pass


Register suites
---------------

Application must know about suites. Register suites is required procedure for your application.
There are several ways...

::

    app = create_app()

    # method one. import your suite and register.
    app.register_suite(suite)
    # method two. register list suites.
    app.register_suites([suite])
    # method three. Auto load suites from path.
    # path can be package or simple dir.
    app.load_suites('/absolute/path/to/dir')


Recommend
---------

* Ideal case if your application class contains setup methods only.
* Try create application instance through create function wrapper. This is a sign of good manners :)

::

    def create_app(config=None, argv=None, plugins=None):
        return MyTestApplication(
            config=config, argv=argv, plugins=plugins,
        )
