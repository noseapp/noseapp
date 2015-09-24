# -*- coding: utf-8 -*-

from noseapp.core import extensions


class TestCaseContext(object):
    """
    Context of test case instance
    """

    def __init__(self, suite):
        """
        :param suite: suite instance
        :type suite: noseapp.suite.base.Suite
        """
        self.__extensions = dict(
            (k, v) for k, v in suite.context.extensions.items()
        )
        self.__require = [r for r in suite.require]

    @property
    def require(self):
        """
        Extensions names storage

        :rtype: list
        """
        return self.__require

    def update_by_require(self, require):
        """
        Update extension storage by require from extensions tmp

        :param require: extensions names
        :type require: list
        """
        self.__require.extend(require)

        for ext_name in require:
            self.__extensions[ext_name] = extensions.get(ext_name)

    def ext(self, name):
        """
        Get extension by name

        :param name: extension name

        :raises: core.extensions.ExtensionNotRequired
        """
        if name in self.__require:
            return self.__extensions[name]

        raise extensions.ExtensionNotRequired(name)
