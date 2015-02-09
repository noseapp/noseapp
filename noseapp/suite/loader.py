# -*- coding: utf-8 -*-

import os
import imp
import errno

from noseapp.suite.base import Suite


class LoadSuiteError(BaseException):
    pass


class AutoLoad(object):
    """
    Автозагрузчик Suite по указанному пути.

    Рекурсивно вычисляет все дирректории внутри каталога,
    проходит по каталогам, находит python модули и инстансы
    Suite внутри них.
    """

    def __init__(self, path):
        if not os.path.exists(path):
            raise LoadSuiteError('Dir "{}" does not exist'.format(path))

        self._suites = set()

        self.all_dirs = []

        base_path = os.path.realpath(
            os.path.expanduser(path),
        )

        self.all_dirs.append(base_path)

        self._collect_dirs(base_path)
        self._do_load()

    def _collect_dirs(self, path):
        """
        Рекурсивно вычисляет пути ко всем
        дирректориям внутри каталога

        :param path: абсолютнй путь до каталога
        """
        for root, dirs, files in os.walk(path):
            for d in dirs:
                dir_path = os.path.join(root, d)
                self.all_dirs.append(dir_path)
                self._collect_dirs(dir_path)

    def _do_load(self):
        """
        Выполняет загрузку из списка дирректорий
        """
        for d in self.all_dirs:
            self._load_suites_from_dir(d)

    def _load_suites_from_dir(self, path):
        """
        Выгружает инстансы Suite из дирректории

        :param path: абсолютнй путь до дрректории
        """
        files = filter(
            lambda r: r.endswith('.py') and not r.startswith('_'),
            os.listdir(path),
        )

        if not files:
            return

        for f in files:
            file_path = os.path.join(path, f)
            module = imp.new_module(file_path.rstrip('.py'))
            module.__file__ = file_path

            try:
                execfile(file_path, module.__dict__)
            except IOError as e:
                if e.errno in (errno.ENOENT, errno.EISDIR):
                    continue

                e.strerror = 'Unable to load file "{}"'.format(e.strerror)
                raise

            contents = (  # подготовить генератор, который на каждую итерацию
                # будет доставать только значения public атрибутов
                getattr(module, content, None)
                for content in dir(module)
                if not content.startswith('_')
            )

            # поготовить генератор который будет возвращать только инстансы Suite
            suites = (suite for suite in contents if isinstance(suite, Suite))

            for s in suites:
                self._suites.add(s)

    def get_result(self):
        """
        Возвращает результат загрузки
        """
        return list(self._suites)
