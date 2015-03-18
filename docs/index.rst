=======
NoseApp
=======

.. toctree::
    :maxdepth: 2

    app
    suite
    case
    runner
    extensions
    simple_example


About
=====

This is framework for test development with complex logic based on nose library.
Build your regression testing process with noseapp library.


Installation
------------

::

  pip install noseapp


Motivation
==========

Why noseapp? What i can get from usage?


Background Initialization
-------------------------

application -> extensions -> suites -> test cases


Flexibility and control
-----------------------

* application is only one service point
* require extensions for test case through suite initialization
* opportunity set default require on your base suite class
* support nose plugins (noseapp.AppPlugin)
* creation of application configuration
* before, after callbacks on base application class


Implementation by steps for test case
-------------------------------------

* memorized steps for exception info
* before, finalize callbacks on base test case class
* interactive debug mode
* parametrize step flow


Async
-----

* multiprocessing
* threading
* gevent event loop
