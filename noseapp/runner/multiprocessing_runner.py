# -*- coding: utf-8 -*-

from threading import Lock
from threading import Thread
from Queue import Queue as TaskQueue

from noseapp.utils.common import waiting_for
from noseapp.runner.base import measure_time
from noseapp.runner.base import BaseTestRunner
from noseapp.utils.common import TimeoutException


Process = ResultQueue = cpu_count = None


def _import_mp():
    """
    Import multiprocessing
    """
    global Process, ResultQueue, cpu_count

    from multiprocessing import Process
    from multiprocessing import Manager
    from multiprocessing import cpu_count

    m = Manager()

    Process, ResultQueue, cpu_count = (
        Process, m.Queue, cpu_count
    )


def task(suite, result, result_queue):
    """
    Task to perform suite
    """
    suite(result)

    del suite

    def get_value(value):
        if isinstance(value, basestring):
            return value
        return repr(value)

    failures = [[get_value(v) for v in f] for f in result.failures]
    errors = [[get_value(v) for v in e] for e in result.errors]
    skipped = [[get_value(v) for v in s] for s in result.skipped]

    result_queue.put_nowait([failures, errors, skipped, result.testsRun])


def run(processor, queue_handler):
    """
    Go, go, go!
    """
    workers = [
        Thread(target=processor.serve),
        Thread(target=queue_handler.handle),
    ]

    try:
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        processor.destroy()
    finally:
        processor.close()


class ResultQueueHandler(object):

    TEST_REPR = 'Test({})'

    def __init__(self, suites, result, result_queue):
        self._result = result
        self._comparison = {}
        self._result_queue = result_queue

        self._counter = 0
        self._length_suites = 0

        self._match(suites)

        self._counter_lock = Lock()

    def _match(self, suites):
        """
        Create dict: repr -> test
        """
        suite_list = [s for s in suites]
        self._length_suites = len(suite_list)

        for suite in suite_list:
            for test in suite:
                key = self.TEST_REPR.format(
                    repr(test.test),
                )

                if key in self._comparison:
                    raise ValueError('Test __repr__ "{}" already exist'.format(key))

                self._comparison[key] = test.test

    def _create_result(self, data):
        _repr, messages = data[0], data[1:]

        try:
            test = self._comparison[_repr]
        except KeyError:
            return None

        return tuple([test] + messages)

    def _add_failures(self, failures):
        for fail in failures:
            result = self._create_result(fail)

            if result:
                self._result.failures.append(result)

    def _add_errors(self, errors):
        for err in errors:
            result = self._create_result(err)

            if result:
                self._result.failures.append(result)

    def _add_skipped(self, skipped):
        for skip in skipped:
            result = self._create_result(skip)

            if result:
                self._result.failures.append(result)

    def handle(self):
        while self._counter < self._length_suites:
            failures, errors, skipped, tests_run = self._result_queue.get()

            self._add_failures(failures)
            self._add_errors(errors)
            self._add_skipped(skipped)

            with self._counter_lock:
                self._result.testsRun += tests_run
                self._counter += 1


class TaskProcessor(object):
    """
    Collect tasks and run with multiprocessing.Process
    """

    def __init__(self, processes, process_timeout=1800):
        """
        :param processes: nun processes
        :type processes: int
        :param process_timeout: number of seconds for process timeout
        :type process_timeout: int, float
        """
        self._processes = processes if processes > 0 else cpu_count()
        self._current = []
        self._queue = TaskQueue()
        self._process_timeout = process_timeout

    def _is_release(self):
        if len(self._current) < self._processes:
            return True

        for process in self._current:
            if not process.is_alive():
                process.terminate()
                self._current.remove(process)
                return True

        return False

    def add_task(self, target, args=None, kwargs=None):
        self._queue.put_nowait((target, args or tuple(), kwargs or dict()))

    def serve(self):
        while not self._queue.empty():
            try:
                waiting_for(self._is_release, timeout=self._process_timeout, sleep=0.01)
            except TimeoutException:
                self.destroy()
                raise

            target, args, kwargs = self._queue.get_nowait()
            process = Process(target=target, args=args, kwargs=kwargs)
            process.start()
            self._current.append(process)

    def destroy(self):
        """
        Kill all processes
        """
        for process in self._current:
            process.terminate()

    def close(self):
        for process in self._current:
            process.join()


class MultiprocessingTestRunner(BaseTestRunner):
    """
    Run suites with multiprocessing.Process
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
        processor = TaskProcessor(self.config.options.app_processes)
        queue_handler = ResultQueueHandler(suites, result, result_queue)

        for suite in suites:
            processor.add_task(task, args=(suite, result, result_queue))

        with measure_time(result):
            run(processor, queue_handler)

        self.config.plugins.finalize(result)

        return result
