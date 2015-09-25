# -*- coding: utf-8 -*-

from __future__ import absolute_import

from contextlib import contextmanager
from multiprocessing import cpu_count

from noseapp.utils.common import waiting_for
from noseapp.core.suite.base import BaseSuite
from noseapp.case.base import get_case_master_id
from noseapp.utils.common import TimeoutException
from noseapp.core.runner.base import RunPerformer
from noseapp.core.suite.base import get_suite_master_id


DEFAULT_RELEASE_TIMEOUT = 180  # default timeout for release processes list
DEFAULT_MAX_PROCESSES = cpu_count()  # default max processes num to run in a moment


@contextmanager
def terminate_processes(runner):
    """
    Do something with runner and
    terminate processes after this

    :type runner: MPSuiteRunner
    """
    try:
        yield
    finally:
        runner.terminate()
        runner.join()


def get_master_id(obj):
    """
    Get id of master process
    """
    if isinstance(obj, BaseSuite):
        return get_suite_master_id(obj)
    return get_case_master_id(obj)


def target(suite, mp_result):
    """
    Task to perform
    """
    suite(mp_result)
    mp_result.save_result()


class MPResult(object):
    """
    Sync result between processes
    """

    MATCH = {}  # id -> instance

    def __init__(self, result):
        from multiprocessing import Manager

        # Test result instance
        self.result = result

        # Result queue
        self.queue = Manager().Queue()

    def __getattr__(self, item):
        return getattr(self.result, item)

    @staticmethod
    def pack_result_storage(storage):
        """
        Pack result from storage
        """
        return [(get_master_id(s[0]), s[1]) for s in storage]

    def unpack_result_storage(self, storage):
        """
        Unpack result from storage
        """
        unpack_storage = []

        for master_id, message in storage:
            unpack_storage.append(
                (self.MATCH[master_id], message),
            )

        return unpack_storage

    def match(self, suite):
        """
        Match id of master process to instance
        """
        self.MATCH[get_suite_master_id(suite)] = suite

        def match(s):
            for o in s:
                if isinstance(o, BaseSuite):
                    self.MATCH[get_suite_master_id(o)] = o
                    match(o)
                else:
                    self.MATCH[get_case_master_id(o)] = o

        match(suite)

    def save_result(self):
        """
        Save result in queue
        """
        self.queue.put(
            (
                (
                    self.pack_result_storage(self.result.errors),
                    self.pack_result_storage(self.result.skipped),
                    self.pack_result_storage(self.result.failures),
                ),
                self.result.testsRun,
            ),
        )

    def make_result(self):
        """
        Merge result from queue to result instance
        """
        while not self.queue.empty():
            (errors, skipped, failures), run_tests = self.queue.get()

            self.result.errors.extend(self.unpack_result_storage(errors))
            self.result.skipped.extend(self.unpack_result_storage(skipped))
            self.result.failures.extend(self.unpack_result_storage(failures))

            self.result.testsRun += run_tests


class MasterProcess(object):
    """
    Run suites with multiprocessing
    """

    def __init__(self,
                 result,
                 max_processes=DEFAULT_MAX_PROCESSES,
                 release_timeout=DEFAULT_RELEASE_TIMEOUT):
        from multiprocessing import Process

        # Timeout for release stack
        self.release_timeout = release_timeout
        # Max processes to run
        self.max_processes = max_processes if max_processes > 0 else DEFAULT_MAX_PROCESSES

        # Tasks queue
        self.queue = []
        # Run processes stack
        self.stack = []

        # Class for create process
        self.process_class = Process

        # Result wrapper for sync
        self.mp_result = MPResult(result)

    def add_suite(self, suite):
        """
        Add suite to run
        """
        self.mp_result.match(suite)

        self.queue.append(
            self.process_class(
                target=target,
                args=(suite, self.mp_result),
            ),
        )

    def add_suites(self, suites):
        """
        Add suites to run. For usability only.
        """
        for suite in suites:
            self.add_suite(suite)

    def try_release(self):
        """
        Find not alive processes in stack and remove their
        """
        for process in self.stack:
            if not process.is_alive():
                process.terminate()
                process.join()
                self.stack.remove(process)

    def is_release(self):
        """
        Will be True if free place in stack else False
        """
        self.try_release()
        return len(self.stack) < self.max_processes

    def wait_release(self):
        """
        To wait free place in stack
        """
        try:
            waiting_for(self.is_release, timeout=self.release_timeout, sleep=0.001)
        except TimeoutException:
            raise TimeoutException(
                'Process list have not been release for "{}" sec.'.format(self.release_timeout),
            )

    def terminate(self):
        """
        Terminate processes from stack
        """
        for process in self.stack:
            process.terminate()

    def join(self):
        """
        Join processes from stack
        """
        for process in self.stack:
            process.join(timeout=self.release_timeout)

    def run(self):
        """
        Run suites
        """
        while self.queue:
            process = self.queue.pop()
            process.start()
            self.stack.append(process)
            self.wait_release()

        self.join()
        self.mp_result.make_result()


class MPRunPerformer(RunPerformer):

    def __call__(self, suites, result):
        max_size = self.runner.config.options.async_suites
        timeout = self.runner.config.options.multiprocessing_timeout

        # XXX:
        # We must prepare test result here for correct finalize.
        # Plugins chain will be still called with run suite
        # on resultProxy, but master process don't know about this
        self.runner.config.plugins.prepareTestResult(result)

        process = MasterProcess(
            result,
            max_processes=max_size,
            release_timeout=timeout,
        )
        process.add_suites(suites)

        with terminate_processes(process):
                process.run()
