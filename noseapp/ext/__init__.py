# -*- coding: utf-8 -*-

"""
Реализация полностью слизана с библиотеки flask.
"""


def setup():
    from ..exthook import ExtensionImporter
    importer = ExtensionImporter(['noseapp_%s', 'noseapp.%s'], __name__)
    importer.install()


setup()
del setup
