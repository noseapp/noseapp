# -*- coding: utf-8 -*-

"""
To release library.

Usage:

    python to_release.py
"""

import os
import subprocess


GIT_BIN = 'git'
PYTHON_BIN = 'python'
FROM_BRANCH = 'master'
PACKAGE_NAME = 'noseapp'

SUBPROCESS_OPTIONS = {
    'shell': True,
    'cwd': os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
        ),
    ),
}


def sudo(command):
    if os.getlogin() != 'root':
        return 'sudo {}'.format(command)
    return command


def python(command):
    return '{} {}'.format(PYTHON_BIN, command)


def git(command):
    return '{} {}'.format(GIT_BIN, command)


def call(command):
    return subprocess.call(command, **SUBPROCESS_OPTIONS)


def check_output(command):
    return subprocess.check_output(command, **SUBPROCESS_OPTIONS)


def check_git_branch():
    command = git('branch')
    output = check_output(command)

    assert '* {}'.format(FROM_BRANCH) in output.split('\n'),\
        'Please check current git branch. Branch for build "{}"'.format(FROM_BRANCH)


def delete_old_files():
    command = sudo('rm -rf ./{}.egg-info ./dist/'.format(PACKAGE_NAME))
    call(command)


def run_tests():
    command = sudo(python('setup.py test'))
    exit_code = call(command)

    assert exit_code == 0, 'Tests was worked with errors'


def upload_to_pip():
    command = sudo(python('setup.py register sdist upload'))
    exit_code = call(command)

    assert exit_code == 0, 'Upload to pip error'


def main():
    check_git_branch()
    delete_old_files()
    run_tests()
    upload_to_pip()


if __name__ == '__main__':
    main()
