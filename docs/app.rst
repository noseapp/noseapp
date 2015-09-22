===========
Application
===========

Application is entry point to your test program. And so...


Callbacks
---------

* NoseApp.setUpApp: setup application callback, will be called after create instance
* NoseApp.tearDownApp: callback will be called after performing test program
* NoseApp.setUp: will be called before run suites
* NoseApp.tearDown: will be called after run suites
* NoseApp.addOptions: add options to OptionParser


::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def setUpApp(self):
            # my script here...


Configuration
-------------

You may use python module as configuration storage

::

    # this is file etc.base(etc/base.py)

    DEBUG = False
    # ...


::

    app = MyTestApplication('name', config='etc.base')
    # or by file path
    app = MyTestApplication('name', config='/home/user/project/etc/base.py')

    app.config.DEBUG


Config property will be have data from python file.


Shared extensions
-----------------

You may expand test cases from application. Extension must be callable object.

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

        def setUpApp(self):
            self.setup_example_ex()

        def setup_example_ex(self):
            self.shared_extension(
                cls=ExampleExtension,
                args=(1, 1000),
            )


Shared data
-----------

Sometimes, may be needed to create configuration for test cases. You can that from application. Data will be copied during installation.

::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def setUpApp(self):
            self.setup_case_settings()

        def setup_case_settings(self):
            case_settings = {
                'hello': 'world',
            }
            self.shared_data('settings', case_settings)


We are recommended do it well

::

    from noseapp.case import TestCaseSettings

    settings = TestCaseSettings(
        debug=True,
        project_url='http://...',
    )
    settings.install(app)


App options to command line
---------------------------

NoseApp class have callback method for this.

::


    def addOptions(self, parser):
        parser.add_option(
            '--project-url',
            dest='project_url',
            default='http://my-site.com',
            help='Project URL',
        )


Callbacks for prepare
---------------------

You would like use this, i'm sure... :)

::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def setUp(self):
            # This callback will be called before run tests
            pass

        def tearDown(self):
            # This callback will be called after run tests
            pass


Register suites
---------------

Suite like single blueprint and application don't know about him, so, register suites is required procedure.
There are several ways...

::

    app = create_app()

    # method one. import your suite and register.
    app.register_suite(suite)
    # method two. register suites list.
    app.register_suites([suite])
    # method three. Auto load suites by path.
    # path can be package or simple dir.
    app.load_suites('/absolute/path/to/dir')


Recommend
---------

We do recommend to create application instance with wrapper function. This is a sign of good manners :)

::

    def create_app(config=None, argv=None, plugins=None):
        return MyTestApplication(
            'name',
            config=config, argv=argv, plugins=plugins,
        )


Master and sub application
--------------------------

You can use application as sub application

::

    sub_app = NoseApp.as_sub_app('hello')
    master_app = NoseApp.as_master_app('world', sub_app)

    sub_app.load_suites('...')
    master_app.load_suites('...', merge_suites=True)
