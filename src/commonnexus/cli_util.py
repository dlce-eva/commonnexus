"""

"""
import re
import sys
import pathlib

from commonnexus import Nexus

NEXUS = re.compile(r'(?:^|(?<=;|\s))(#nexus)', re.IGNORECASE | re.MULTILINE)


class NexusType:
    def __init__(self, many=False):
        self._many = many

    def __call__(self, string):
        if pathlib.Path(string).exists():
            nex = Nexus.from_file(string)
            return [nex] if self._many else nex
        if string == '-':
            string = sys.stdin.read()

        if self._many:
            res = []
            chunks = NEXUS.split(string)
            for i in range(1, len(chunks), 2):
                res.append(Nexus(chunks[i] + chunks[i + 1]))
            return res
        return Nexus(string)


def add_nexus(parser, many=False):
    if many:
        parser.add_argument(
            'nexus',
            help='NEXUS content specified as file path or string or "-" to read from stdin. Note '
                 'that "-" can only be used once. Content from a string or stdin will be split '
                 'into individual NEXUS "files" using the "#NEXUS" token as separator.',
            nargs='+',
            type=NexusType(many=True))
    else:
        parser.add_argument(
            'nexus',
            type=NexusType())
