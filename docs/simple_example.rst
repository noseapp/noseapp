==============
Simple Example
==============

This is example of create simple project.


Extension
---------

::

    from random import randint


    class ExampleExtension(object):

        name = 'rand'

        def __init__(self, a, b):
            self._a = a
            self._b = b

        def get_random(self):
            return randint(self._a, self._b)


Config
------

::

    DEBUG = False
    # ...


Application
-----------

::

    from noseapp import NoseApp


    class MyTestApplication(NoseApp):

        def initialize(self):
            self.setup_example_ex()
            self.setup_case_settings()

        def setup_example_ex(self):
            self.shared_extension(
                cls=ExampleExtension,
                args=(1, 1000),
            )

        def setup_case_settings():
            settings = {
                'debug_mode': self.config.DEBUG,
            }

            self.shared_data('settings', settings)


    def create_app(config=None, argv=None, plugins=None):
        return MyTestApplication(
            'name',
            config=config, argv=argv, plugins=plugins,
        )


Suite
-----

::

    from noseapp import Suite


    suite = Suite(__name__, require=['rand', 'settings'])


TestCase
--------

::

    from noseapp import TestCase
    from noseapp.case import step
    from noseapp import ScreenPlayCase


    @suite.register
    def my_test_case(case):
        rand_int = case.ext('rend').get_random()
        case.assertGreater(rand_int, 0)

    @suite.register(simple=True)
    def my_simple_test_case():
        rand_int = suite.ext('rend').get_random()
        assert rand_int > 0


    @suite.register
    class BasicExampleCase(TestCase):

        def test(self):
            rand_int = self.ext('rend').get_random()
            self.assertGreater(rand_int, 0)


    @suite.register
    class StepByStepCase(ScreenPlayCase):

        def setUp(self):
            self.USE_PROMPT = self.ext('settings')['debug_mode']

        @step(1, 'step description')
        def step_one(self):
            rand_int = self.ext('rend').get_random()
            self.assertGreater(rand_int, 0)

        # @step(2, 'description')
        # def ...
