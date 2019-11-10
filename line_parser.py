import re


class LineParser:
    def __init__(self, line):
        line_re = re.compile(r'(\w+)://([a-zA-Z0-9.:]+)(/.+)?')

        match = line_re.match(line)

        self.proto = match[1]
        self.host = match[2]
        self.path = match[3] if match[3] is not None else '/'
