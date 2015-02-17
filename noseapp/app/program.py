# -*- coding: utf8 -*-

import sys

from nose.core import TestProgram as BaseTestProgram

from noseapp.app import extensions
from noseapp.utils.console import exc_suite_info
from noseapp.suite.collector import CollectSuites


# Стратегии указывают на то, какой TestRunner будем использовать
BASIC_STRATEGY = 'basic'
GEVENT_STRATERY = 'gevent'
THREADS_STRATEGY = 'threads'
MULTIPROCESSING_STRATEGY = 'multiprocessing'


def _get_strategy(options):
    """
    Возвращает стратегию запуска
    на основании опций sys.argv
    """
    if options.app_processes:
        return MULTIPROCESSING_STRATEGY
    elif options.gevent_pool:
        return GEVENT_STRATERY
    elif options.thread_pool:
        return THREADS_STRATEGY
    else:
        return BASIC_STRATEGY


def get_test_runner_class(options):
    """
    На основании стратегии импортирует
    класс testRunner и возвращает его
    """
    strategy = _get_strategy(options)

    if strategy == BASIC_STRATEGY:
        from noseapp.runner.base import BaseTestRunner
        return BaseTestRunner
    elif strategy == MULTIPROCESSING_STRATEGY:
        from noseapp.runner.multiprocessing_runner import MultiprocessingTestRunner
        return MultiprocessingTestRunner
    elif strategy == GEVENT_STRATERY:
        from noseapp.runner.gevent_runner import GeventTestRunner
        return GeventTestRunner
    elif strategy == THREADS_STRATEGY:
        from noseapp.runner.threads_runner import ThreadsTestRunner
        return ThreadsTestRunner


class TestProgram(BaseTestProgram):
    """
    Класс который отвечает за запуск тестов
    """

    collector_class = CollectSuites

    def __init__(self, app, argv, *args, **kwargs):
        self._app = app
        self._argv = argv

        super(TestProgram, self).__init__(argv=argv, *args, **kwargs)

        self._app.config.init_nose_config(self.config)
        self._app.initialize()

    # для того чтобы TestProgram не запустился при
    # иициализации нужно обезоружить эти 2 метода
    def createTests(self):
        pass

    def runTests(self):
        pass

    def init_suites(self):
        """
        Инициализация suite из приложения
        """
        if self.config.options.ls:  # если нужно показать дерево suite, то делаем это
            exc_suite_info(self._app.suites, show_docs=self.config.options.doc)

        if len(self._argv) > 2:
            load_path = self._argv[1]
        else:
            load_path = ''

        collector = self.collector_class(
            load_path, self._app.suites, self.testLoader, self.config,
        )

        self.test = collector.make_result()

    def perform(self):
        """
        Запуск suite
        """
        self.init_suites()

        extensions.clear()

        test_runner = get_test_runner_class(self.config.options)

        self.testRunner = test_runner(stream=self.config.stream,
                                      verbosity=self.config.verbosity,
                                      config=self.config)

        plug_runner = self.config.plugins.prepareTestRunner(self.testRunner)

        if plug_runner is not None:
            self.testRunner = plug_runner

        self._app.before()

        result = self.testRunner.run(self.test)
        self.success = result.wasSuccessful()

        self._app.after()

        if self.exit:
            sys.exit(not self.success)

        return self.success
