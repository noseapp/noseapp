======
Manage
======

You will can create your command for command line interface noseapp-manage


Create my manage.py
-------------------

Create manage.py file. Run nosepp-manage command in context of directory with your manage file.


Create and register command
---------------------------

::

    from noseapp import manage


    def my_command():
        print 'Hello World!'


    manage.register_command('hello_world', my_command)


To run:

::

    noseapp-manage hello_world


Command arguments
-----------------

::

    def my_command(*args, **kwargs):
        print 'Args: ', args
        print 'Kwargs: ', kwargs


To run:

::

    noseapp-manage my_command arg1, arg2, param=1


Usage help
----------

Common:

::

    noseapp-manage help


For command:

::

    noseapp-manage help command
