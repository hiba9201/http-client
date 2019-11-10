import socket
import re


class Network:
    def __init__(self, host, protocol):
        self.sock = socket.socket()
        self.host = host
        self.proto = protocol
        self.addr = ('', 80)

    def try_getaddrinfo(self):
        try:
            self.addr = socket.getaddrinfo(self.host, self.proto,
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
        self.sock.send(f"GET {path} HTTP/1.1 \r\n".encode('utf-8'))
        self.sock.send(b"Accept: */* \r\n")
        self.sock.send(b"Accept-Language: " +
                       b"ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7 \r\n")
        self.sock.send(b"User-Agent: Mozilla/5.0 (Windows NT 6.1) " +
                       b"AppleWebKit/537.36 (KHTML, like Gecko) " +
                       b"Chrome/54.0.2840.71 Safari/537.36 \r\n")
        self.sock.send(b'Connection: keep-alive \r\n')
        self.sock.send(f'Host: {self.host} \r\n'.encode('utf-8'))
        self.sock.send(b"\r\n")

    @staticmethod
    def get_content_start(header_with_content):
        try:
            content_index = header_with_content.lower().index(
                '<!doctype')
        except ValueError:
            try:
                content_index = header_with_content.lower().index(
                    '<html')
            except ValueError:
                content_index = 0

        return content_index

    def recv_request(self):
        data = b''
        recv_data = self.sock.recv(1024)

        content_len_search = re.search(r'Content-Length: (\d+)',
                                       recv_data.decode('utf-8'))

        content_index = Network.get_content_start(recv_data.decode('utf-8'))
        if content_len_search is not None:
            content_length = int(content_len_search[1])

            if content_length == 0:
                content_index = len(recv_data)
            else:
                content_length += content_index - len(recv_data)
        else:
            content_length = 65535

        data += (recv_data[content_index:]
                 + self.recv_length_bytes(content_length))

        return data.decode('utf-8')

    def recv_length_bytes(self, length):
        recv_count = 0
        data = b''

        while recv_count < length:
            recv_data = self.sock.recv(length)
            recv_count += len(recv_data)
            data += recv_data

        return data
