# -*- coding: utf-8 -*-

import os
import errno
import signal
import logging
import subprocess

import psutil
from noseapp.utils.common import waiting_for
from noseapp.utils.common import TimeoutException


logger = logging.getLogger(__name__)


TIMEOUT = 3.0
WAIT_SLEEP = 1.0


def get_std(stdout, stderr, cmd_prefix):
    """
    Возвращает lambda функции для настройки
    stderr и stdout в subprocess.Popen

    :param stdout: путь до файла stdout
    :param stderr: путь до файла stderr
    :param cmd_prefix: префикс для запуска демона
    """
    if stdout and stderr and cmd_prefix:
        if not os.path.isfile(stdout):
            file(stdout, 'w').close()

        if not os.path.isfile(stderr):
            file(stderr, 'w').close()

        return lambda: open(stdout, 'a'), lambda: open(stderr, 'a')

    return lambda: None, lambda: None


def process_terminate(process):
    """
    Завершение процесса subprocess.Popen

    :type process: subprocess.Popen
    """
    try:
        process.terminate()

        try:
            waiting_for(
                process.poll,
                timeout=TIMEOUT,
                sleep=WAIT_SLEEP,
            )
        except TimeoutException:
            process.kill()

    except (psutil.NoSuchProcess, OSError):
        pass


def kill_process(pid):
    """
    Завершить процесс по pid

    :param pid: id процесса
    """
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass


def kill_children(pid):
    """
    Завершает все дочерние процессы по pid родителя

    :param pid: id родительского процесса
    """
    try:
        for ch in psutil.Process(pid).children(recursive=True):
            process_terminate(ch)
    except psutil.NoSuchProcess:
        pass


class PidFileObject(object):
    """
    Класс реализует интерфейс для работы с pid файлом
    """

    def __init__(self, file_path):
        self.file_path = file_path

    @property
    def exist(self):
        try:
            return os.path.isfile(self.file_path)
        except TypeError:
            return False

    @property
    def path(self):
        return self.file_path

    @property
    def pid(self):
        if not self.file_path:
            return None

        try:
            with open(self.file_path) as fp:
                return int(fp.readline().strip())
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise
        except ValueError:
            pass

        return None

    def remove(self):
        if self.exist:
            try:
                os.unlink(self.file_path)
            except OSError:
                pass

    def __repr__(self):
        return '<PidFile {}>'.format(self.file_path)


class DaemonInterface(object):
    """
    Интерфейс для управления демоном
    """

    @property
    def name(self):
        """
        Имя демона
        """
        raise NotImplementedError(
            'Property "name" should be implemented in subclasses.',
        )

    @property
    def cmd(self):
        """
        cmd для запуска
        """
        raise NotImplementedError(
            'Property "cmd" should be implemented in subclasses.',
        )

    @property
    def process_options(self):
        """
        Опции для subprocess.Popen
        """
        return {}

    def begin(self):
        """
        Callback вызывается после инициализации класса
        """
        pass

    def before_start(self):
        """
        Callback вызывается перед запуском
        """
        pass

    def after_start(self):
        """
        Callback вызывается после запуска
        """
        pass

    def before_stop(self):
        """
        Callback вызывается перед остановкой
        """
        pass

    def after_stop(self):
        """
        Callback вызывается после остановки
        """
        pass


class Daemon(DaemonInterface):
    """
    Базовый класс демона
    """

    def __init__(self, daemon_bin,
                 working_dir=None,
                 client=None,
                 pid_file=None,
                 config_file=None,
                 cmd_prefix=None,
                 stdout=None,
                 stderr=None):
        """
        :param daemon_bin: путь до executable файла
        :param working_dir: путь до рабочей дирректории
        :param client: инстанс клиента
        :param pid_file: путь до pid файла
        :param config_file: путь до конфиг файла
        :param cmd_prefix: префикс к cmd для запуска
        :param stdout: путь до файла куда нужно писать stdout(работает только совместно с cmd_prefix)
        :param stderr: путь до файла куда нужно писать stderr(работает только совместно с cmd_prefix)
        """
        self.daemon_bin = daemon_bin
        self.client = client
        self.pid_file = PidFileObject(pid_file)
        self.config_file = config_file
        self.working_dir = working_dir or '.'

        if cmd_prefix:
            self.cmd_prefix = [c.strip() for c in cmd_prefix.split(' ')]
        else:
            self.cmd_prefix = None

        self.process = None
        self.children = []
        self.get_stdout, self.get_stderr = get_std(stdout, stderr, cmd_prefix)

        self.begin()

    @property
    def started(self):
        """
        Флаг сигнализирует о том, что демон запущен
        """
        return bool(self.process) or self.pid_file.exist

    @property
    def stopped(self):
        """
        Инверсия флага started
        """
        return not self.started

    def start(self):
        """
        Стартует демона
        """
        if self.started:
            return

        logger.debug('Daemod "%s" start', self.name)

        self.before_start()

        self.process = subprocess.Popen(
            self.cmd if not self.cmd_prefix else self.cmd_prefix + self.cmd,
            stderr=self.get_stderr(),
            stdout=self.get_stdout(),
            **self.process_options
        )

        self.after_start()

    def stop(self):
        """
        Останавливает демона
        """
        if self.stopped:
            return

        logger.debug('Daemod "%s" stop', self.name)

        self.before_stop()

        if self.pid_file.exist:
            kill_process(self.pid_file.pid)
        elif self.process:
            kill_children(self.process.pid)
            process_terminate(self.process)

        self.pid_file.remove()

        self.process = None

        self.after_stop()
