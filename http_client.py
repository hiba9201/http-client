#!/usr/bin/env python3
import argparse
import sys
import socket

from logic import errors as e
from logic import network
from logic import utils as u

URL_NOT_VALID = 1
NOT_SUPPORTED_PROTO = 2
CONNECTION_ERROR = 3
TIMEOUT_ERROR = 4
FILE_ERROR = 5


def create_args():
    parser = argparse.ArgumentParser(description='''Python3.7 implementation of 
                                     http client. Read "README.md" for more
                                     information''')
    parser.add_argument('url', type=str, help='Url for request')
    parser.add_argument('-a', '--agent', type=str,
                        default="Shartrash/1.0",
                        dest='agent', action='store',
                        help='change User-Agent header value')
    parser.add_argument('-n', '--no-keep-alive', default=False,
                        dest='no_keep', action='store_true',
                        help='''make connection header value
                        "close" instead of "keep-alive"''')
    parser.add_argument('-o', '--output', type=str, dest='output',
                        action='store',
                        help='load image to <LOAD> file if got one')
    parser.add_argument('-d', '--headers', type=str, dest='headers',
                        action='store', help='''add user headers to request
                        from <HEADERS> file''')
    parser.add_argument('-c', '--host', type=str, dest='host',
                        action='store', help='''specifies custom host for
                        request''')
    parser.add_argument('-m', '--method', type=str, dest='method',
                        action='store', default='GET',
                        help='''request method, GET by default
                        (others are not implemented)''')
    parser.add_argument('-r', '--no-redirects', action='store_true',
                        default=False, dest='no_redirects',
                        help='switch off redirecting')
    parser.add_argument('-x', '--max-redirects', action='store', type=int,
                        dest='max_redirects', default=sys.maxsize,
                        help='set maximum count of redirects')

    return parser.parse_args()


def main():
    args = create_args()

    parsed_line = u.parse_url(args.url)

    if not parsed_line['host']:
        print(f'Url "{args.url}" is not valid')
        sys.exit(URL_NOT_VALID)

    if parsed_line['proto'] not in ('http', 'https'):
        print(f'Protocol "{parsed_line["proto"]}" is not supported',
              file=sys.stderr)
        sys.exit(NOT_SUPPORTED_PROTO)

    net = network.Network(parsed_line['host'], parsed_line['proto'],
                          parsed_line['port'], args)

    try:
        net.connect_to_host()
        net.send_request(parsed_line["path"])
    except socket.gaierror:
        print(f'Could not connect to host "{parsed_line["host"]}"',
              file=sys.stderr)
        sys.exit(CONNECTION_ERROR)
    except TimeoutError:
        print(f'Connecting timed out', file=sys.stderr)
        sys.exit(TIMEOUT_ERROR)

    try:
        result = net.recv_response()
    except TimeoutError:
        print('Receiving timed out', file=sys.stderr)
        sys.exit(TIMEOUT_ERROR)
    except e.NonSuccessfulResponse as err:
        print(f"Response wasn't successful: {err}", file=sys.stderr)
        sys.exit(net.response_code)
    except e.ProtocolError as err:
        print(f'Protocol "{err}" is not supported',
              file=sys.stderr)
        sys.exit(NOT_SUPPORTED_PROTO)
    except socket.gaierror as err:
        print(err,
              file=sys.stderr)
        sys.exit(CONNECTION_ERROR)
    except OSError:
        print('Unable to write file', file=sys.stderr)
        sys.exit(FILE_ERROR)

    if not args.output:
        print(result)


if __name__ == '__main__':
    main()
