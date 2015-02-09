# -*- coding: utf-8 -*-

from Queue import Queue as TaskQueue

from noseapp.utils.common import waiting_for
from noseapp.utils.runner import measure_time
from noseapp.runner.base import BaseTestRunner
from noseapp.utils.common import TimeoutException


Process = ResultQueue = cpu_count = None


def _import_mp():
    """
    Импортирует все, что нужно из multiprocessing.
    Необходимость этой функции возникает из-за того,
    что импорт нужно сделать тогда, когда все необходимое
    в TestRunner проинициализированно.
    """
    global Process, ResultQueue, cpu_count

    from multiprocessing import Process
    from multiprocessing import Manager
    from multiprocessing import cpu_count

    m = Manager()

    Process, ResultQueue, cpu_count = (
        Process, m.Queue, cpu_count,
    )


def task(suite, result, result_queue):
    """
    Задача на запуск suite.
    После выполнения формирует результат и ставит его в очередь.
    """
    suite(result)

    del suite  # инстанс suite нам больше не нужен, удаляем

    def get_value(value):
        """
        Если значение будет, не строка, то это test метод.
        Поскольку метод из процесса передать нельзя, то передаем
        его repr, т.к. он составлен уникального для каждого теста.
        """
        if isinstance(value, basestring):
            return value
        return repr(value)

    failures = [[get_value(v) for v in f] for f in result.failures]
    errors = [[get_value(v) for v in e] for e in result.errors]
    skipped = [[get_value(v) for v in s] for s in result.skipped]

    result_queue.put_nowait([failures, errors, skipped, result.testsRun])


class ResultQueueHandler(object):
    """
    Обработчик очереди результатов
    """

    TEST_REPR = 'Test({})'  # repr формат который будет создан в результате

    def __init__(self, suites, result):
        self._result = result
        self._comparison = {}

        self._counter = 0
        self._length_suites = 0

        self._match(suites)

    def __call__(self, result_queue):
        """
        При вызове экземпляра начинаем слушать очередь
        до тех пор пока не получим все результаты.
        """
        while self._counter < self._length_suites:
            failures, errors, skipped, tests_run = result_queue.get()

            self._add_failures(failures)
            self._add_errors(errors)
            self._add_skipped(skipped)

            self._result.testsRun += tests_run
            self._counter += 1

    def _match(self, suites):
        """
        Для того чтобы сформировать результат нам
        нужно уметь определять для какого кейса он
        был создан. Поэтому готовим таблицу отношений
        вида repr -> тест, т.к. id при выполнении в
        процессе у него будет другой.
        """
        suite_list = [s for s in suites]
        self._length_suites = len(suite_list)

        for suite in suite_list:
            for test in suite:
                key = self.TEST_REPR.format(
                    repr(test.test),
                )

                if key in self._comparison:  # если в разных модулях будут классы с
                    # одинаковыми именами и с методами, которые имеют одинаковое название,
                    # то таблица отношений окажется невалидной.
                    raise ValueError('Test __repr__ "{}" already exist'.format(key))

                self._comparison[key] = test.test

    def _create_result(self, data):
        """
        Создает новый результат для добавления
        """
        _repr, messages = data[0], data[1:]
        test = self._comparison[_repr]
        del self._comparison[_repr]
        return tuple([test] + messages)

    def _add_failures(self, failures):
        for fail in failures:
            self._result.failures.append(
                self._create_result(fail),
            )

    def _add_errors(self, errors):
        for err in errors:
            self._result.failures.append(
                self._create_result(err),
            )

    def _add_skipped(self, skipped):
        for skip in skipped:
            self._result.failures.append(
                self._create_result(skip),
            )


class TaskProcessor(object):
    """
    Класс организует работу с очередью задач
    """

    def __init__(self, processes, process_timeout=1800):
        """
        :param processes: кол-во одновременно работающих процессов
        :param process_timeout: timeout на выполнение процесса
        """
        self._processes = processes if processes > 0 else cpu_count()
        self._current = []
        self._closed = False
        self._queue = TaskQueue()
        self._process_timeout = process_timeout

    def _release(self):
        """
        Освобождает место в текущем списке процессов,
        если удалось освободить, то True, иначе False
        """
        if len(self._current) < self._processes:
            return True

        for process in self._current:
            if not process.is_alive():
                process.terminate()
                self._current.remove(process)
                return True

        return False

    def _perform(self):
        """
        Начать выполнение тасков
        """
        if not self._closed:
            raise RuntimeError(
                'Processor is open, please close processor',
            )

        while not self._queue.empty():
            try:
                waiting_for(self._release, timeout=self._process_timeout, sleep=0.01)
            except TimeoutException:
                self.kill()
                raise

            target, args, kwargs = self._queue.get_nowait()
            process = Process(target=target, args=args, kwargs=kwargs)
            process.start()
            self._current.append(process)

    def add_task(self, target, args=None, kwargs=None):
        """
        Добавить задачу в очередь

        :param target: функция котторую нужно выполнить
        :param args, kwargs: аргументы которые нужно передать target
        """
        if self._closed:
            raise RuntimeError('Processor is closed')

        self._queue.put_nowait((target, args or tuple(), kwargs or dict()))

    def serve(self):
        """
        Обслуживать очередь.
        Этот метод приводит объект в состояние выполнения,
        после того, как вызван этот метод в очередь уже
        ничего нельзя добавить.
        """
        self._closed = True
        self._perform()

    def kill(self):
        """
        Убить процессы
        """
        if not self._closed:
            raise RuntimeError(
                'Processor is open, please close processor',
            )

        for process in self._current:
            process.terminate()

    def close(self):
        """
        Закончить работу и дождаться
        завершения оставшихся процессов.
        """
        if not self._closed:
            raise RuntimeError('Processor is not working')

        for process in self._current:
            process.join()


class MultiprocessingTestRunner(BaseTestRunner):
    """
    Многопоточный запуск тестов.
    Одна noseapp.suite.Suite == 1 процесс.
    Порядок регистрации в приложении имеет значение.
    """

    def run(self, suites):
        wrapper = self.config.plugins.prepareTest(suites)
        if wrapper is not None:
            suites = wrapper

        wrapped = self.config.plugins.setOutputStream(self.stream)
        if wrapped is not None:
            self.stream = wrapped

        result = self._makeResult()

        _import_mp()

        result_queue = ResultQueue()
        queue_handler = ResultQueueHandler(suites, result)

        size = self.config.options.app_processes

        if size < 0:
            size = cpu_count()

        processor = TaskProcessor(size)

        for suite in suites:
            processor.add_task(task, args=(suite, result, result_queue))

        with measure_time(result):
            try:
                processor.serve()
                queue_handler(result_queue)
            except KeyboardInterrupt:
                processor.kill()
            finally:
                processor.close()

        self.config.plugins.finalize(result)
        return result
