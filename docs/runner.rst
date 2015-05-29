======
Runner
======

You can run application with making run method

::

    app = create_app()
    app.run()


Run application
---------------

::

    noseapp-manage run myproject.app:create_app


Run strategy
------------

* multiprocessing:
noseapp-manage run myproject.app:create_app --run-strategy multiprocessing --async-suites 4 --async-tests 2

* threading:
noseapp-manage run myproject.app:create_app --run-strategy threading --async-suites 4 --async-tests 2

* gevent:
noseapp-manage run myproject.app:create_app --run-strategy gevent --async-suites 4 --async-tests 2


Run one test or suite:

::

  noseapp-manage run myproject.app:create_app -t package.module:TestCase