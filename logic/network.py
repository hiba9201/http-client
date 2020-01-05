import gzip
import re
import socket
import urllib.parse as up
import ssl

from logic import errors as e
from logic import utils as u


class Network:
    REDIRECTS = 0

    def __init__(self, host, protocol, port, args):
        self.sock = socket.socket()
        self.sock.settimeout(180)
        self.host = host
        self.proto = protocol
        self.port = port
        self.args = args
        self.addr = ()
        self.response_code = 0

    def connect_to_host(self):
        self.sock.connect((self.host, int(self.port)))
        if self.proto == 'https':
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(self.sock,
                                            server_hostname=self.host)

    def send_request(self, path):
        connection = 'close' if self.args.no_keep else 'keep-alive'
        host = self.args.host if self.args.host is not None else self.host

        headers = [f"{self.args.method} {path} HTTP/1.1",
                   f"User-Agent: {self.args.agent}",
                   f"Connection: {connection}",
                   f'Host: {host}']

        user_headers = u.get_headers(self.args.headers)
        headers.extend(user_headers)
        headers.append('\r\n')

        self.sock.sendall(up.unquote_to_bytes("\r\n".join(headers)))

    def recv_response(self):
        headers = {}
        page = []

        with self.sock.makefile('rb') as socket_file:
            start_line = socket_file.readline().decode('utf-8')
            _, code, msg = u.parse_response_start_line(start_line)

            self.response_code = int(code)

            for line in socket_file:
                decoded_line = line.decode('utf-8')
                if not decoded_line.strip():
                    break
                typ, value = decoded_line.split(': ', maxsplit=1)
                headers[typ.lower()] = value.lower().strip()

            if (code.startswith('3') and not self.args.no_redirects and
                    Network.REDIRECTS < self.args.max_redirects and
                    'location' in headers):
                Network.REDIRECTS += 1

                parsed_url = u.parse_url(headers['location'])
                if parsed_url['proto'] not in ('http', 'https'):
                    raise e.ProtocolError(parsed_url['proto'])

                net = Network(parsed_url['host'],
                              parsed_url['proto'],
                              parsed_url['port'], self.args)

                net.connect_to_host()
                net.send_request(parsed_url["path"])

                return net.recv_response()

            if code != '200':
                raise e.NonSuccessfulResponse(f'{code} {msg.strip()}')

            if 'content-length' in headers:
                page = socket_file.read(int(
                    headers['content-length']))
            else:
                buffer = []
                try:
                    for line in socket_file:
                        buffer.append(line)
                except socket.timeout:
                    if not buffer:
                        raise TimeoutError

                page = b''.join(buffer)

        if self.args.output:
            with open(self.args.output, 'wb') as f:
                f.write(page)

            return

        if 'text' not in headers.get('content-type', ''):
            return page

        if headers.get('content-encoding', '') == 'gzip':
            page = gzip.decompress(page)

        encod = 'utf-8'
        if 'charset' in headers.get('content-type', ''):
            encod = re.match(r'.+charset=(.+)', headers['content-type'])[1]

        return page.decode(encod)
