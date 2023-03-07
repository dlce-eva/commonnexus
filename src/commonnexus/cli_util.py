"""

"""
import re
import sys
import pathlib
import argparse

from commonnexus import Nexus

NEXUS = re.compile(r'(?:^|(?<=;|\s))(#nexus)', re.IGNORECASE | re.MULTILINE)


class ParserError(Exception):
    pass


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


def add_flag(parser, name, help):
    parser.add_argument('--{}'.format(name), action='store_true', default=False, help=help)


def list_of_ranges(dstring):
    """
    Converts a comma-separated list of 1-based ranges into a list of 1-based indices.

    :param dstring: A string

    :return: `list` of zero-based indices
    """
    def _int(v):
        try:
            return int(v)
        except ValueError:  # pragma: no cover
            raise argparse.ArgumentTypeError("%r is not an integer" % v)

    out = []
    for token in dstring.split(','):
        token = token.replace(':', '-')
        if '-' in token:
            start, stop = token.split("-")
            out.extend([x for x in range(_int(start), _int(stop) + 1)])
        else:
            out.append(_int(token))
    return sorted(out)


def validate_operations(ops, args):
    if sum(1 for op in ops if getattr(args, op.name)) > 1:
        raise ParserError("Only one operation can be specified")  # pragma: no cover
