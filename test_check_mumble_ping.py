#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import sys

sys.path.append('..')

from check_mumble_ping import commandline
from check_mumble_ping import main

class CLITesting(unittest.TestCase):

    def test_commandline(self):
        actual = commandline(['-H', 'localhost'])
        self.assertEqual(actual.host, 'localhost')
        self.assertEqual(actual.port, 64738)
