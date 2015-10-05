# -*- coding: utf-8 -*-

import sys
import traceback

from noseapp.manage import funcs
from noseapp.manage import commands


# Add commands here. Order is important.
funcs.register_command('help', commands.help)
funcs.register_command('run', commands.run_app)


def run():
    funcs.load_manage_py()

    command = funcs.get_command()

    args = []
    kwargs = {}

    arguments = []

    for arg in sys.argv[2:]:
        if arg.startswith('-'):
            break

        arguments.append(arg)

    for arg in arguments:
        if '=' in arg:
            k, v = arg.split('=')
            kwargs[k.strip()] = v.strip()
        else:
            args.append(arg.strip())

    try:
        command(*args, **kwargs)
    except TypeError:
        funcs.error(
            'Is invalid signature of command, may be?\n\n{}'.format(
                traceback.format_exc(),
            ),
        )


run()
