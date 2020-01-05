import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from logic import utils as u


class TestUtils(unittest.TestCase):
    def test_parse_url(self):
        url = 'https://anytask.org'
        parsed = u.parse_url(url)
        self.assertEqual(parsed['proto'], 'https')
        self.assertEqual(parsed['host'], 'anytask.org')
        self.assertEqual(parsed['port'], 443)
        self.assertEqual(parsed['path'], '/')

    def test_parse_url_unknown_proto(self):
        url = 'hts://anytask.org'
        parsed = u.parse_url(url)
        self.assertEqual(parsed['port'], 80)

    def test_parse_url_with_path(self):
        url = 'https://anytask.org/home'
        parsed = u.parse_url(url)
        self.assertEqual(parsed['path'], '/home')

    def test_parse_start_line(self):
        parsed_line = u.parse_response_start_line('HTTP/1.1 404 Not Found')
        self.assertEqual(['HTTP/1.1', '404', 'Not Found'], parsed_line)

    def test_get_headers(self):
        headers = u.get_headers('tests/headers.txt')
        self.assertEqual(['Cache-Control: no-cache', 'Accept-Ranges: bytes'],
                         headers)


if __name__ == '__main__':
    TestUtils().run()
