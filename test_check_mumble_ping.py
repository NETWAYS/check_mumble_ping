#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import sys
import struct

sys.path.append('..')

from check_mumble_ping import commandline
from check_mumble_ping import return_plugin
from check_mumble_ping import ping_mumble
from check_mumble_ping import main

class CLITesting(unittest.TestCase):

    def test_commandline(self):
        actual = commandline(['-H', 'localhost'])
        self.assertEqual(actual.host, 'localhost')
        self.assertEqual(actual.port, 64738)


class UtilTesting(unittest.TestCase):

    @mock.patch('builtins.print')
    def test_return_plugin(self, mock_print):
        return_plugin(0, "message")
        mock_print.assert_called_with('Mumble: OK - message')

    @mock.patch('check_mumble_ping.socket')
    def test_ping_mumble(self, mock_socket):

        mock_data = b'\x01\x02\x03\x04' + struct.pack('>Q', 1234567890123456789) + struct.pack('>iii', 1, 2, 3)

        m = mock.MagicMock()
        m.recvfrom.return_value = (mock_data, 2)

        mock_socket.socket.return_value = m

        actual = ping_mumble('localhost')
        expected = {'version': (2, 3, 4), 'user': (1, 2), 'time': -1234567890121573.8, 'rate': 3, 'len': 24}

        self.assertEqual(actual['version'], expected['version'])
        self.assertEqual(actual['rate'], expected['rate'])
        self.assertEqual(actual['len'], expected['len'])

class MainTesting(unittest.TestCase):

    @mock.patch('check_mumble_ping.ping_mumble', side_effect=Exception('error'))
    def test_main_error(self, mock_ping):
        args = commandline(['-H', 'localhost'])
        actual = main(args)

        self.assertEqual(actual, 3)
        mock_ping.assert_called_with('localhost', 64738)

    @mock.patch('check_mumble_ping.ping_mumble')
    def test_main_ok(self, mock_ping):
        mock_ping.return_value = {
            "version": 'version',
            "user": 'user',
            "time": 1.23,
            "rate": 1000,
            "len": 5
        }

        args = commandline(['-H', 'localhost'])
        actual = main(args)

        self.assertEqual(actual, 0)
        mock_ping.assert_called_with('localhost', 64738)
