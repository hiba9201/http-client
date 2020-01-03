import re
import argparse


class Utils:
    @staticmethod
    def parse_url(url):
        line_re = re.compile(r'(\w+)://([\w\-.]+):?(\d+)?(/.+)?')
        match = line_re.match(url)
        parsed = {'proto': match and match[1], 'host': match and match[2],
                  'port': match and match[3] or 80,
                  'path': match and match[4] or '/'}

        return parsed

    @staticmethod
    def get_headers(headers_file):
        headers = []
        if not headers_file:
            return headers

        with open(headers_file) as f:
            for line in f:
                if len(line.strip()) != 0 and re.match(r'[\w-]+: [\w-]+',
                                                       line.strip()):
                    headers.append(line.strip())

        return headers

    @staticmethod
    def create_args():
        default_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) " +
                         "AppleWebKit/537.36 (KHTML, like Gecko) " +
                         "Chrome/78.0.3904.108 Safari/537.36")
        parser = argparse.ArgumentParser(
            description='Python3.7 implementation of http client. ' +
                        'Read "README.md" for more information')
        parser.add_argument('url', type=str, help='Url for request')
        parser.add_argument('-a', '--agent', type=str, default=default_agent,
                            dest='agent', action='store',
                            help='change User-Agent header value')
        parser.add_argument('-k', '--keep', default=True,
                            dest='keep', action='store_false',
                            help='make connection header value' +
                                 ' "close" instead of "keep-alive"'
                            )
        parser.add_argument('-l', '--load', type=str, dest='load',
                            action='store',
                            help='load image to <LOAD> file if got one')
        parser.add_argument('-d', '--headers', type=str, dest='headers',
                            action='store', help='add user headers to request')

        return parser.parse_args()
