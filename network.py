import re
import socket
import urllib.parse as up

import utils as u


class Network:
    def __init__(self, host, protocol, port, args):
        self.sock = socket.socket()
        self.host = host
        self.proto = protocol
        self.port = port
        self.args = args
        self.addr = ()

    def try_getaddrinfo(self):
        try:
            self.addr = socket.getaddrinfo(self.host, self.port,
                                           socket.AF_INET,
                                           socket.SOCK_STREAM)[0][4]
        except Exception:
            return False

        return True

    def try_connect_to_host(self):
        try:
            self.sock.connect(self.addr)
        except Exception:
            return False

        return True

    def send_request(self, path):
        connection = 'keep-alive' if self.args.keep else 'close'
        headers = [f"GET {path} HTTP/1.1",
                   "Accept: */*",
                   "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                   f"User-Agent: {self.args.agent}",
                   f"Connection: {connection}",
                   f'Host: {self.host}']
        user_headers = u.Utils.get_headers(self.args.headers)
        headers[len(headers):] = user_headers
        headers.append('\r\n')
        self.sock.sendall(up.unquote_to_bytes(" \r\n".join(headers)))

    def recv_request(self):
        headers = {}
        page = []

        with self.sock.makefile('rb') as socket_file:
            socket_file.readline()
            for line in socket_file:
                decoded_line = line.decode('utf-8')
                if decoded_line.strip() == '':
                    break
                typ = decoded_line[0:decoded_line.index(':')]
                value = decoded_line[decoded_line.index(':') + 2:]
                headers[typ] = value.strip()

            if ('Content-type' in headers and
                    'image' in headers['Content-type']):
                if self.args.load:
                    with open(self.args.load, 'wb') as f:
                        for line in socket_file:
                            f.write(line)
                    return ''

                buffer = []
                for line in socket_file:
                    buffer.append(line)

                return b''.join(buffer)

            encod = 'utf-8'
            if ('Content-type' in headers and
                    'charset' in headers['Content-type']):
                encod = re.match(r'.+charset=(.+)', headers['Content-type'])[1]

            if 'Content-Length' in headers:
                return socket_file.read(int(
                    headers['Content-Length'])).decode(encod)

            try:
                for line in socket_file:
                    page.append(line.decode(encoding=encod))
            except socket.timeout:
                if len(page) == 0:
                    raise TimeoutError

        return ''.join(page)
