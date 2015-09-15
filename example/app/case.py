# -*- coding: utf-8 -*-

from noseapp import ScreenPlayCase as BaseTestCase


class TestCase(BaseTestCase):

    @staticmethod
    def prepare():
        print 'Case is preparing'
