# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

import noseapp


with open('requirements.txt') as fp:
    requirements = [req.strip() for req in fp.readlines() if not req.startswith('--')]


if __name__ == '__main__':
    setup(
        name='noseapp',
        version=noseapp.__version__,
        url='https://github.com/trifonovmixail/noseapp',
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        description='NoseApp pattern for test development',
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=requirements,
    )
