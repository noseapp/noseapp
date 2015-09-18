# -*- coding: utf-8 -*-

from noseapp.plugins.base import AppPlugin


def app_callback(app, name, *args, **kwargs):
    """
    Wrapper for call callback of application

    :type app: noseapp.app.base.NoseApp
    :param name: callback name

    :params args, kwargs: args, kwargs of callback method
    """
    if app.is_sub_app:
        raise RuntimeError(
            'Can not call callback "{}" of {}. Application is sub application.'.format(
                name, app,
            ),
        )

    apps = [app]
    apps.extend(app.sub_apps)

    callback = lambda a: getattr(a, name)

    for application in apps:
        callback(application)(*args, **kwargs)


def merge_context(
        master_app,
        merge_setup=False,
        merge_suites=False,
        merge_plugins=False,
        merge_teardown=False):
    """
    Merge context from sub apps to master app

    :param master_app: master app instance
    :type master_app: noseapp.app.base.NoseApp
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

        for plugin in master_app.context.plugins:
            if isinstance(plugin, AppPlugin):
                plugin.init_app(master_app)

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
    Context of NoseApp instance
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
        return self.__suites

    @property
    def plugins(self):
        return self.__plugins

    @property
    def setup_callbacks(self):
        return self.__setup

    @property
    def teardown_callbacks(self):
        return self.__teardown

    def add_suite(self, suite):
        self.__suites.append(suite)

    def add_setup(self, f):
        self.__setup.append(f)

    def add_teardown(self, f):
        self.__teardown.append(f)

    def setup(self):
        """
        Method do call to callback list before run application.
        Will be use for nose suite.
        """
        for callback in self.__setup:
            callback()

    def teardown(self):
        """
        Method do call to callback list after run application.
        Will be use for nose suite.
        """
        for callback in self.__teardown:
            callback()
