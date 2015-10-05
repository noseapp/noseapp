# -*- coding: utf-8 -*-

from unittest import TestCase

from noseapp.manage import funcs


class TestRegisterCommand(TestCase):

    def runTest(self):
        fake_command = lambda: None

        funcs.register_command('fake_command', fake_command)

        self.assertIn(fake_command, funcs.get_commands().values())
