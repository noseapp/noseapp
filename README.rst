
=====
About
=====

This is framework for test development with complex logic based on nose library

:background Initialization: application -> extensions -> suites -> test cases
:flexibility and control:
 * application is only one service point
 * require extensions for test case through suite initialization
 * opportunity set default require on your base suite class
 * support nose plugins (noseapp.AppPlugin)
 * creation of application configuration
 * before, after callbacks on base application class
:implementation by steps for test case:
 * memorized steps for exception info
 * before, finalize callbacks on base test case class
 * interactive debug mode
 * parametrize step flow
:asynchrony:
 * multiprocessing
 * threading
 * gevent event loop

===========
Quick start
===========

app.py::

  from random import randint

  from noseapp import NoseApp

  class ExampleExtesion(object):
    
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
          'interactiv_mode': True # may be False :)
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


  # use config module for configuration in your application
  #
  # app = create_app(config='etc.base')
  # or
  # app = create_app(config='/home/user/projects/example/etc/base.py')
  #
  # use config property inside application class


example_suite.py::

  from noseapp import Suite
  from noseapp import TestCase
  from noseapp.case import step
  from noseapp import ScreenPlayCase


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


runner.py::

  from .app import create_app
  
  
  if __name__ == '__main__':
    app = create_app()
    
    from .example_suite import suite
    app.register_suite(suite)
    # or
    # app.register_suites([suite])
    # or
    # app.load_suites(path_to_dir)

    app.run()


=====================
Usage noseapp runners
=====================

With multiprocessing:
  * processes:
    runner.py --app-processes 2 (one suite === one process)

  * processes and threads:
    runner.py --app-processes 4 --threads 2 (one suite == one process, one test == one thread)

  * threads only:
    runner.py --threads 2 (one suite == one thread)


With gevent:
  * runner.py --gevent 4 (one suite == one greenlet)
  * runner.py --gevent 4 --greenlets 2 (one suite == one greenlet, one test == one greenlet)


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
