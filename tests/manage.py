# -*- coding: utf-8 -*-

from unittest import TestCase

from noseapp import manage


class TestRegisterCommand(TestCase):

    def runTest(self):
        fake_command = lambda: None

        manage.register_command('fake_command', fake_command)

        self.assertIn(fake_command, manage._COMMANDS.values())
