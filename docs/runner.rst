======
Runner
======

You can run application with making run method

::

    app = create_app()
    app.run()

NoseApp support three async run type:

 * multiprocessing
 * threading
 * gevent


Processes and threads
---------------------

Two processes (one suite == one process)

::

    runner.py --app-processes 2


Two processes, two treads (one suite == one process, one test == one thread)

::

    runner.py --app-processes 2 --threads 2


Two threads (one suite == one thread)

::

    runner.py --threads 2 (one suite == one thread)


Gevent
------

Two greenlets (one suite == one greenlet)

::

    runner.py --gevent 2

Four greenlets (one suite == one greenlet, one test == one greenlet)

::

    runner.py --gevent 2 --greenlets 2
