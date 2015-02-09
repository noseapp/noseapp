# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger(__name__)


BASIC_STATEGY = 'basic'
GEVENT_STRATEGY = 'gevent'
THREAD_STRATEGY = 'thread'


def _get_strategy(options):
    """
    Возвращает стратегию запуска тестов
    внутри suite на основании nose_config

    :param options: опции из nose парсера
    """
    if options.app_processes and options.thread_pool:
        return THREAD_STRATEGY
    elif not options.app_processes and options.gevent_greanlets:
        return GEVENT_STRATEGY

    return BASIC_STATEGY


def get_suite_class(options):
    """
    Определяет стратегию, на основании
    этого возвращает класс для suite
    """
    strategy = _get_strategy(options)

    if strategy == BASIC_STATEGY:
        from noseapp.runner.suites.base import BaseSuite
        return BaseSuite
    elif strategy == GEVENT_STRATEGY:
        from noseapp.runner.suites.gevent_suite import GeventSuite
        return GeventSuite
    elif strategy == THREAD_STRATEGY:
        from noseapp.runner.suites.thread_suite import ThreadSuite
        return ThreadSuite


class TestCaseMediator(object):
    """
    Класс посредник между noseapp.suite.Suite, TestLoader, TestSuite
    и одним или группой TestCase. Обеспечивает связь между
    TestCase->TestLoader->TestSuite.

    Основная задача класса скрыть реализацию связи от пользователя
    в класса Suite. Так же данный паттерн позволяет гибко менять
    реализацию в Suite классе путем установки вашего Mediator класса.
    """

    def __init__(self, require):
        self._test_cases = []
        self._require = require

    @property
    def test_cases(self):
        """
        Возвращает список классов TestCase
        """
        return self._test_cases

    def create_map(self):
        """
        Создает карту зарегистрированных классов вида:
        {
            'class name': {
                'cls': 'link to class object',
                'tests': {
                    'method name': 'link to class method',
                },
            },
        }
        """
        mp = {}

        for case in self._test_cases:
            mp[case.__name__] = {
                'cls': case,
                'tests': dict(
                    (atr, getattr(case, atr))
                    for atr in dir(case)
                    if atr.startswith('test')
                    or
                    atr.startswith('runTest'),
                ),
            }

        return mp

    def create_suite(self, nose_config, test_loader):
        """
        Собираетвсе TestCase классы в набор suite и возвращает
        """
        suite_class = get_suite_class(nose_config.options)
        suite = suite_class(config=nose_config)

        for case in self._test_cases:
            suite.addTests(
                test_loader.loadTestsFromTestCase(
                    case.with_require(self._require),
                ),
            )

        return suite

    def add_test_case(self, test_case):
        """
        Добавить TestCase класс
        """
        self._test_cases.append(test_case)
