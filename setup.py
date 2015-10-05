# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


__version__ = '2.2.1'


if __name__ == '__main__':
    setup(
        name='noseapp',
        version=__version__,
        url='https://github.com/trifonovmixail/noseapp',
        packages=find_packages(exclude=('testapp*', 'tests*')),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        license='GNU LGPL',
        description='Framework for test development',
        keywords='test unittest framework nose application',
        long_description=open('README.rst').read(),
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=[
            'six',
            'nose==1.3.7',
        ],
        entry_points={
            'console_scripts': [
                'noseapp-manage = noseapp.manage.__main__:run',
            ],
        },
        test_suite='tests',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Testing',
        ],
    )
