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
        packages=find_packages(include=('noseapp', )),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        license='GNU LGPL',
        description='Framework for test development',
        keywords='test unittest framework nose application',
        long_description=open('README.rst').read(),
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=requirements,
        test_suite='tests',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Testing',
        ],
    )
