import re

URL_RE = re.compile(r'(\w+)://([\w\-.]+):?(\d+)?(/.+)?')


proto_port = {'http': 80,
              'https': 443}


def parse_url(url):
    match = URL_RE.match(url)
    proto = match and match[1]
    host = match and match[2]
    default_port = proto_port.get(proto, 80)
    port = (match and match[3]) or default_port
    path = (match and match[4]) or '/'
    parsed = {'proto': proto,
              'host': host,
              'port': port,
              'path': path}

    return parsed


def parse_response_start_line(line):
    return line.split(' ', maxsplit=2)


def get_headers(headers_file):
    headers = []
    if not headers_file:
        return headers

    with open(headers_file) as f:
        for line in f:
            if re.match(r'[\w-]+: .+', line.strip()):
                headers.append(line.strip())
    return headers
