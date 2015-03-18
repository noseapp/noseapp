Create Application
==================

Application is the entry point for service cases through suites, as well to prepare for test infrastructure.

What are the objectives decided with Application?
-------------------------------------------------

* expand cases with extensions
* prepare a testing facility


Simple Example
--------------

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
            self.setup_case_settings()

        def setup_example_ex(self):
            self.shared_extension(
                cls=ExampleExtension,
                args=(1, 1000),
            )

        def setup_case_settings():
            settings = {
                'debug_mode': self.config.DEBUG
            }

            self.shared_data('settings', settings)


    def create_app(config=None, argv=None, plugins=None):
        return MyTestApplication(
            config=config, argv=argv, plugins=plugins,
        )
