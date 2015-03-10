# -*- coding: utf-8 -*-

"""
Realisation from flask lib
"""


def setup():
    from ..exthook import ExtensionImporter
    importer = ExtensionImporter(['noseapp_%s', 'noseapp.%s'], __name__)
    importer.install()


setup()
del setup
