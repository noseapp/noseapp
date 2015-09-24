# -*- coding: utf-8 -*-

"""
Work with context of application
"""

from noseapp.plugins.base import AppPlugin


def app_callback(master_app, name, *args, **kwargs):
    """
    Wrapper for call callback of application

    :type master_app: noseapp.app.base.NoseApp
    :param name: callback name

    :params args, kwargs: args, kwargs of callback method
    """
    if master_app.is_sub_app:
        raise RuntimeError(
            'Can not call callback "{}" of {}. Application is sub application.'.format(
                name, master_app,
            ),
        )

    apps = [master_app]
    apps.extend(master_app.sub_apps)

    callback = lambda a: getattr(a, name)

    for app in apps:
        callback(app)(*args, **kwargs)


def prepare_plugins(plugins, app):
    """
    Prepare plugins to run

    :param plugins: plugin list
    :tyep app: noseapp.app.base.NoseApp
\    """
    for plugin in plugins:
        if isinstance(plugin, AppPlugin):
            plugin.init_app(app)


def merge_context(
        master_app,
        merge_setup=False,
        merge_suites=False,
        merge_plugins=False,
        merge_teardown=False):
    """
    Merge context from sub apps to master app.

    :param master_app: master app instance
    :type master_app: noseapp.app.base.NoseApp

    :param merge_setup: merge setup callbacks?
    :type merge_setup: bool

    :param merge_suites: merge suites?
    :type merge_suites: bool

    :param merge_plugins: merge plugins?
    :type merge_plugins: bool

    :param merge_teardown: merge teardown callbacks?
    :type merge_teardown: bool

    :raises: RuntimeError
    """
    if master_app.is_sub_app:
        raise RuntimeError(
            'Can not marge context of {}. Application is sub application.'.format(
                master_app,
            ),
        )

    # plugins
    if merge_plugins:
        plugins = []
        plugin_names = map(
            lambda p: p.name,
            master_app.context.plugins,
        )

        for plugin_list in map(lambda sa: sa.plugins, master_app.sub_apps):
            for plugin in plugin_list:
                if plugin.name not in plugin_names:
                    plugins.append(plugin)
                    plugin_names.append(plugin.name)

        master_app.context.plugins.extend(plugins)
        prepare_plugins(master_app.context.plugins, master_app)

    for sub_app in master_app.sub_apps:
        # suites
        if merge_suites:
            master_app.context.suites.extend(
                sub_app.suites,
            )

        # setup callbacks
        if merge_setup:
            master_app.context.setup_callbacks.extend(
                sub_app.context.setup_callbacks,
            )

        # teardown callbacks
        if merge_teardown:
            master_app.context.teardown_callbacks.extend(
                sub_app.context.teardown_callbacks,
            )


class AppContext(object):
    """
    Context storage of NoseApp instance.

    Class is storage for application data.
    Callback functions is here.

    Usage:

        >>> context = AppContext()
        >>> context.add_setup(lambda: print 'Hello World!')
        >>> ...
    """

    def __init__(self):
        # Suites instances
        self.__suites = []
        # Plugins instances
        self.__plugins = []

        # Setup callbacks
        self.__setup = []
        # Teardown callbacks
        self.__teardown = []

    @property
    def suites(self):
        """
        Suites storage.
        After register on application suite will be here.
        """
        return self.__suites

    @property
    def plugins(self):
        """
        Plugins storage.
        After add plugin to application he will be here.
        """
        return self.__plugins

    @property
    def setup_callbacks(self):
        """
        Setup callback storage
        """
        return self.__setup

    @property
    def teardown_callbacks(self):
        """
        Teardown callback storage
        """
        return self.__teardown

    def add_suite(self, suite):
        """
        Add suite to suite storage

        :param suite: suite instance
        :type suite: noseapp.suite.base.Suite
        """
        self.__suites.append(suite)

    def add_setup(self, func):
        """
        Add setup callback to setup callback storage

        :param func: function to call
        :type func: callable
        """
        self.__setup.append(func)

    def add_teardown(self, func):
        """
        Add teardown callback to teardown callback storage

        :param func: function to call
        :type func: callable
        """
        self.__teardown.append(func)

    def setup(self):
        """
        Method make call to chain of setup callback storage before run suites.
        For nose.suite.ContextSuite.
        """
        for callback in self.__setup:
            callback()

    def teardown(self):
        """
        Method make call to chain of teardown callback storage after run suites.
        For nose.suite.ContextSuite.
        """
        for callback in self.__teardown:
            callback()
