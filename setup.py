# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

import noseapp


if __name__ == '__main__':
    setup(
        name='noseapp',
        version=noseapp.__version__,
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        description='NoseApp pattern for test development',
        install_requires=[
            'nose==1.3.4',
        ],
    )
