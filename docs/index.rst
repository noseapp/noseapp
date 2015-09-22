=======
NoseApp
=======

.. toctree::
    :maxdepth: 2

    app
    suite
    case
    runner
    manage
    extensions
    simple_example


About
=====

This is framework for test development with complex logic around, well, based on nose library.
You will can to build your regression testing on base noseapp library and will create your own extensions.

Installation
------------

::

  pip install noseapp


Motivation
==========

Why noseapp? What i can take from usage?


Background Initialization
-------------------------

Object model. Real suites!

application -> extensions -> suites -> test cases


Flexibility and control
-----------------------

* application is only one service point
* connect extensions, you can require extension by name for suite initialization.
* support original nose plugins (and noseapp.AppPlugin)
* you will can create common configuration of your application
* NoseApp class is implemented before, after callbacks methods
* you may create constructor of application(this is required procedure in reality). use initialize callback method for this.


Implementation by steps on test case class
------------------------------------------

* comfortable error messages in traceback
* before, finalize callback methods on base test case class
* interactive debug mode
* parametrize for flow of steps


Async
-----

* multiprocessing
* threading
* gevent
