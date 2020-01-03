#!/usr/bin/env python3

import sys

import network
import utils as u


def main():
    args = u.Utils.create_args()

    line_parser = u.Utils.parse_url(args.url)

    if not line_parser['host']:
        sys.stderr.write(f'Url "{args.url}" is not valid\n')
        sys.exit(4)

    if line_parser['proto'] != 'http':
        sys.stderr.write(
            f'Protocol "{line_parser["proto"]}" is not supported :(\n')
        sys.exit(1)

    net = network.Network(line_parser['host'], line_parser['proto'],
                          line_parser['port'], args)

    if not net.try_getaddrinfo():
        sys.stderr.write(f'Could not resolve host "{line_parser["host"]}"\n')
        sys.exit(2)

    if net.try_connect_to_host():
        net.send_request(line_parser["path"])
    else:
        sys.stderr.write(
            f'Could not connect to host "{line_parser["host"]}"\n')
        sys.exit(3)

    try:
        result = net.recv_request()
    except TimeoutError:
        sys.stderr.write('Receive timed out\n')
        sys.exit(5)
    except OSError:
        sys.stderr.write('Unable to write file\n')
        sys.exit(6)

    print(result)


if __name__ == '__main__':
    main()
