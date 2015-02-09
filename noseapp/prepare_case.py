# -*- coding: utf8 -*-


import unittest
from functools import wraps
from unittest import TestCase

from noseapp.datastructures import ModifyDict as Context


CONTEXT_CACHE_ATTRIBUTE_NAME = '__CACHE__'


def get_prepare_data(case, name):
    prepare_method = getattr(case, name.replace('test', 'prepare'), None)

    if callable(prepare_method):
        return prepare_method(Context())

    return None


def prepare_test_method(ctx, method):
        @wraps(method)
        def wrapper():
            return method(ctx)
        return wrapper


class PrepareTestCaseMeta(type):

    def __call__(cls, name):
        instance = type.__call__(cls, name)
        if instance.CACHED:
            print u'В метаклассе с кешом..............'
            ctx = get_prepare_data(instance, name)
            setattr(instance, CONTEXT_CACHE_ATTRIBUTE_NAME, ctx)
        return instance


class PrepareTestCase(TestCase):

    __metaclass__ = PrepareTestCaseMeta

    CACHED = False

    def prepare_example(self, ctx):
        ctx.result = 1
        return ctx

    def test_example(self, ctx):
        self.assertEqual(ctx.result, 1)

    def test_example2(self):
        print 1

    def run(self, result=None):
        if self.CACHED:
            print u'С кешом'
            ctx = getattr(self, CONTEXT_CACHE_ATTRIBUTE_NAME, None)
        else:
            print u'Без кеша'
            ctx = get_prepare_data(self, self._testMethodName)

        if ctx is not None:
            setattr(
                self,
                self._testMethodName,
                prepare_test_method(ctx, getattr(self, self._testMethodName)),
            )

        return super(PrepareTestCase, self).run(result=result)


unittest.main()
