===========
Application
===========

Application is only one initialization point of collect suites prepare infrastructure. And so...


Initialization
--------------

You must implemented initialization method on you application class. This is will be your constructor. Original method is busy other job.
I would like to save usage __init__ method, but it's not easy.


::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def initialize(self):
            # my script here...


Configuration
-------------

You may use python module as configuration storage

::

    # this is file etc.base(etc/base.py)

    DEBUG = False
    # ...


::

    app = MyTestApplication(config='etc.base')
    # or by file path
    app = MyTestApplication(config='/home/user/project/etc/base.py')


Config property will be have data from python file.


Shared extensions
-----------------

You may expand test cases from application. Extension must be callable object. Extension will be available by name as property.

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

Sometimes, may be needed to create configuration for test cases. You can this from application. Data will be copied during installation.

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


    def add_options(self, parser):
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

        def before(self):
            # This callback will be called before run tests
            pass

        def after(self):
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
            config=config, argv=argv, plugins=plugins,
        )
