#!/usr/bin/env python3

import network
import args_parser as ps
import line_parser as lp


def main():
    parser = ps.ArgsParser()
    args = parser.parser.parse_args()

    line_parser = lp.LineParser(args.url[0])

    if line_parser.proto != 'http':
        print(f'Protocol "{line_parser.proto}" is not supported :(')
        return 1

    net = network.Network(line_parser.host, line_parser.proto)

    if not net.try_getaddrinfo():
        print(f'Could not resolve host "{line_parser.host}"')
        return 2

    if net.try_connect_to_host():
        net.send_request(line_parser.path)
    else:
        print(f'Could not connect to host "{line_parser.host}"')
        return 3
    print(net.recv_request())
    return 0


if __name__ == '__main__':
    main()
