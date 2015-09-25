Command manager
===============

Noseapp framework have command manager.

Usage:

>>> noseapp-manage <command name> <command args> <command kwargs> [options]


Example::

    >>> noseapp-manage help

    NoseApp management.

    Command line interface:
        noseapp-manage <command name>, <command args>, <command kwargs> [options]

    Example:
        noseapp-manage command argument1 argument2 argument3=value

    Commands:

        * help
        * run


.. autofunction:: noseapp.manage.register_command
