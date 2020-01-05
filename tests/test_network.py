import sys
import os
import unittest
import functools
from unittest import mock

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from logic import errors
from logic import network


class Arguments:
    def __init__(self):
        self.agent = 'Shartrash/1.0'
        self.no_keep = False
        self.output = None
        self.headers = 'headers.txt'
        self.host = None
        self.method = None
        self.no_redirects = False
        self.max_redirects = sys.maxsize


def fake_connect(sock, self):
    sock.makefile = functools.partial(open, 'tests/test_response.txt')
    self.sock = sock


class TestNetwork(unittest.TestCase):
    @mock.patch('logic.network.socket')
    def test_receive(self, Socket):
        net = network.Network('', '', 80, Arguments())
        net.sock = Socket
        net.sock.makefile = functools.partial(open, 'tests/test_response.txt')
        self.assertEqual('content', net.recv_response())

    @mock.patch('logic.network.socket')
    def test_not_found(self, Socket):
        net = network.Network('', '', 80, Arguments())
        net.sock = Socket
        net.sock.makefile = functools.partial(open, 'tests/test_404.txt')
        self.assertRaises(errors.NonSuccessfulResponse,
                          net.recv_response)

    @mock.patch('logic.network.socket')
    def test_receive_gzip(self, Socket):
        net = network.Network('', '', 80, Arguments())
        net.sock = Socket
        net.sock.makefile = functools.partial(open, 'tests/test_gzip')
        self.assertEqual('content', net.recv_response())

    @mock.patch('logic.network.socket')
    def test_receive_with_output(self, Socket):
        args = Arguments()
        args.output = 'tests/test_output.txt'
        net = network.Network('', '', 80, args)
        net.sock = Socket
        net.sock.makefile = functools.partial(open, 'tests/test_response.txt')
        net.recv_response()
        with open('tests/test_output.txt') as f:
            text = f.read()
        self.assertEqual('content', text)


if __name__ == '__main__':
    TestNetwork().run()
