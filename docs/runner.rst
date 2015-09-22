======
Runner
======

You can run application with run method call. But it's not good idea.

::

    app = create_app()
    app.run()


Run application
---------------

We do it so

::

    noseapp-manage run myproject.app:create_app


Where "myproject.app:create_app" is path to import of callable object


Run strategy
------------

* multiprocessing(default async):
noseapp-manage run myproject.app:create_app --run-strategy multiprocessing --async-suites 4 --async-tests 2
or
noseapp-manage run myproject.app:create_app --async-suites 4 --async-tests 2

* threading:
noseapp-manage run myproject.app:create_app --run-strategy threading --async-suites 4 --async-tests 2

* gevent:
noseapp-manage run myproject.app:create_app --run-strategy gevent --async-suites 4 --async-tests 2


One test or suite to run:

::

  noseapp-manage run myproject.app:create_app -t package.module:TestCase

