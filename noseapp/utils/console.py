# -*- coding: utf8 -*-

import sys
from warnings import warn


def _print_line(string, spaces=0):
    """
    Выводит строку в консоль.

    :param string: строка для вывода в консоль
    :param spaces: кол-во пробелов перед строкой
    """
    sys.stdout.write('| {}{}\n'.format(_get_spaces(spaces), string))


def _print_total_info(suites, cases, methods):
    """
    Выводит значения итого

    :param suites: кол-во suite
    :param cases: кол-во классов TestCase
    """
    info = 'Total: suites: {}. cases: {}. methods: {}.\n'.format(
        suites, cases, methods,
    )

    separate = []

    for i in xrange(len(info) - 1):
        separate.append('-')

    sys.stdout.write('\n{}\n'.format(''.join(separate)))
    sys.stdout.write(info)


def _get_spaces(num):
    """
    Возвращает строку с указанным числом пробелов

    :param num: кол-во пробелов в строке
    """
    s = []

    for i in xrange(num):
        s.append(' ')

    return ''.join(s)


def _li(string):
    """
    Фоматирует строку в подпункт

    :param string: строка для форматирования
    """
    return '\_ * {}'.format(string)


def _doc(string, is_end):
    """
    Форматирует строку в докстринг

    :param string: строка для форматирования
    :param is_end: флаг сигнализирует о том, что это последня строка
    """
    return '| - {}{}'.format(string, '...' if is_end else '')


def exc_suite_info(suites, show_docs=True, doc_lines=1):
    """
    Вывести в консоль информацию о всех suite

    :param suites: список suite
    :param show_docs: флаг сигнализирует о том нужно показывать докстринги или нет
    :param doc_lines: кол-во срок которые нужно выводить из докстрингов
    """
    case_counter = 0
    suite_counter = 0
    method_counter = 0
    suite_names = set()

    # Suites
    for suite in suites:
        suite_counter += 1
        suite_name = suite.name

        if suite_name in suite_names:
            warn(
                'Duplicate suite name "{}"! Please rename your suite!'.format(
                    suite_name,
                ),
            )
        suite_names.add(suite_name)

        _print_line('* {}'.format(suite_name))

        mp = suite.get_map()

        # Cases
        for cls_name in mp:
            case_counter += 1

            _print_line(
                _li(
                    '{case} ({suite}:{case})'.format(
                        case=cls_name,
                        suite=suite_name,
                    ),
                ),
                spaces=2,
            )

            if show_docs:
                cls_doc = mp[cls_name]['cls'].__doc__

                if cls_doc:
                    line_counter = 0

                    for line in cls_doc.splitlines():
                        line = line.strip()

                        if line:
                            is_end = line_counter == doc_lines - 1

                            _print_line(_doc(line, is_end), spaces=4)

                            line_counter += 1

                            if is_end:
                                break

            # Tests
            for test_method in mp[cls_name]['tests']:
                method_counter += 1

                _print_line(
                    _li(
                        '{test} ({suite}:{case}.{test})'.format(
                            test=test_method,
                            case=cls_name,
                            suite=suite_name,
                        ),
                    ),
                    spaces=4,
                )

                if show_docs:
                    method_doc = mp[cls_name]['tests'][test_method].__doc__

                    if method_doc:
                        line_counter = 0

                        for line in method_doc.splitlines():
                            line = line.strip()

                            if line:
                                is_end = line_counter == doc_lines - 1

                                _print_line(_doc(line, is_end), spaces=6)

                                line_counter += 1

                                if is_end:
                                    break

    _print_total_info(suite_counter, case_counter, method_counter)

    sys.exit(0)
