============
Installation
============

::

  pip install noseapp


==========
Extensions
==========

* noseapp_daemon https://pypi.python.org/pypi/noseapp_daemon
* noseapp_requests https://pypi.python.org/pypi/noseapp_requests
* noseapp_selenium - https://pypi.python.org/pypi/noseapp_selenium
* noseapp_alchemy - coming soon https://github.com/noseapp/noseapp_alchemy


===========
What's new?
===========

* Installation settings for test case

Example::

    from noseapp.case import TestCaseSettings

    settings = TestCaseSettings(
        debug=True,
        project_url='http://...',
    )
    settings.install(app)

    suite = Suite(__name__, require=['settings'])

* Add command line options from application class

Example::

    class MyTestApplication(NoseApp):

        def add_options(self):
            self.parser.add_option(
                    '--project-url',
                    dest='project_url',
                    default='http://my-site.com',
                    help='Project URL',
                )

* Added manage module. You may run apllication with noseapp-manage run command. See noseapp-manage help.
* Your may add run hadler for test case of suite.

Example::

    suite.add_handler(lambda test: None)
    #or
    @suite.add_handler
    def run_test_handler(test):
        """
        :param test: instance of test case class
        """
        pass


===========
Quick start
===========

::

  from random import randint

  from noseapp import Suite
  from noseapp import NoseApp
  from noseapp import TestCase
  from noseapp.case import step
  from noseapp import ScreenPlayCase

  class ExampleExtesnion(object):

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
          cls=ExampleExtesion,
          args=(1, 1000),
        )

      def setup_case_settings():
        settings = {
          'interactive_mode': True # may be False :)
        }

        self.shared_data('settings', settings)


  def create_app(config=None, argv=None, plugins=None):
    return MyTestApplication(
      config=config, argv=argv, plugins=plugins,
    )

  # create your app plagin
  #
  # from noseapp import AppPlugin
  #
  # class MyAppPlugin(AppPlugin):
  #
  #     name = 'my-app-plugin'
  #
  #     def ...(self):
  #         self.app....
  #
  # app = create_app(plugins=[MyAppPlugin()], argv=['--with-my-app-plugin'])


  # use config module for configuration of application
  #
  # app = create_app(config='etc.base')
  # or
  # app = create_app(config='/home/user/projects/example/etc/base.py')
  # or
  # app = create_app()
  # app.config.from_module('etc.base')
  # or
  # app.config.from_py_file('/home/user/projects/example/etc/base.py')
  #
  # use config property inside application class


  suite = Suite(__name__, require=['rand', 'settings'])


  # create your suite class and use default require
  #
  # class MySuite(Suite):
  #     DEFAULT_REQUIRE = ['settings']


  @suite.register
  class BasicExampleCase(TestCase):

    rand = None  # from MyTestApplication.setup_example_ex

    def test(self):
      rand_int = self.rend.get_random()
      self.assertGreater(rand_int, 0)


  @suite.register
  class StepByStepCase(ScreenPlayCase):

    settings = None  # from MyTestApplication.setup_case_settings

    def setUp(self):
      self.USE_PROMPT = self.settings['interactive_mode']

    @step(1, 'step description')
    def step_one(self):
      rand_int = self.rend.get_random()
      self.assertGreater(rand_int, 0)

    @step(2, 'description')
    def ...



=====================
Usage noseapp runners
=====================

With multiprocessing:
  * processes:
    noseapp-manage run myproject.app:create_app --app-processes 2 (one suite === one process)

  * processes and threads:
    noseapp-manage run myproject.app:create_app --app-processes 4 --threads 2 (one suite == one process, one test == one thread)

  * threads only:
    noseapp-manage run myproject.app:create_app --threads 2 (one suite == one thread)


With gevent:
  * noseapp-manage run myproject.app:create_app --gevent 4 (one suite == one greenlet)

  * noseapp-manage run myproject.app:create_app --gevent 4 --greenlets 2 (one suite == one greenlet, one test == one greenlet)


Run one test or suite:

::

  noseapp-manage run myproject.app:create_app -t package.module:TestCase

Use --ls option for suite tree to console


============================
Creating your own extensions
============================

You will can create extensions for nose app as independent library. Usage redirect imports from noseapp.ext

Example::

  # from your lib
  from noseapp_my_ext import Extension
  # With redirect import
  from noseapp.ext.my_ext import Extension

Good luck and easy testing!