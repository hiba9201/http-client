import argparse


class ArgsParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Python3.7 implementation of http client. ' +
                        'Read "README.md" for more information')
        self.parser.add_argument('url', nargs=1, type=str, help=
                                 'Url for request')
