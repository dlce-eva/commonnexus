"""
Utility functions used to implement `commonnexus` subcommands.
"""
import re
import sys
import enum
from typing import Union, Callable
import pathlib
import argparse

from commonnexus import Nexus

NEXUS = re.compile(r'(?:^|(?<=;|\s))(#nexus)', re.IGNORECASE | re.MULTILINE)
LambdaOrTupleType = Union[tuple[str, ...], Callable[[str], str]]


class Operation(enum.Enum):
    """Operations on character matrices or trees."""
    binarise = 1  # pylint: disable=invalid-name
    multistatise = 2  # pylint: disable=invalid-name
    convert = 3  # pylint: disable=invalid-name
    drop = 4  # pylint: disable=invalid-name
    drop_numbered = 5  # pylint: disable=invalid-name
    describe = 6  # pylint: disable=invalid-name


class ParserError(Exception):
    """Exception to be raised when CLI input validation fails."""


class NexusType:  # pylint: disable=too-few-public-methods
    """
    :class:`Ǹexus` as `Argument type <https://docs.python.org/3/library/argparse.html#type>`_

    Can create :class:`Ǹexus` instances from

    - file paths
    - string content
    - data read from `stdin`
    """
    def __init__(self, many: bool = False):
        self._many = many

    def __call__(self, string) -> Union[Nexus, list[Nexus]]:
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


def add_nexus(parser: argparse.ArgumentParser, many=False) -> None:
    """
    Adds (a) positional argument(s) `nexus` to the argument parser.

    :param parser:
    :param many:

    .. code-block:: python

        >>> import argparse
        >>> from commonnexus.cli_util import add_nexus
        >>> parser = argparse.ArgumentParser()
        >>> add_nexus(parser)
        >>> args = parser.parse_args(['#nexus begin block; end;'])
        >>> print(args.nexus.BLOCK)
        begin block; end;
        >>> parser = argparse.ArgumentParser()
        >>> add_nexus(parser, many=True)
        >>> args = parser.parse_args(['#nexus begin block; end;', '#nexus begin other; end;'])
        >>> len(args.nexus)
        2
    """
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


def add_flag(parser: argparse.ArgumentParser, name: str, help_: str) -> None:
    """Add a flag, i.e. a boolean option, defaulting to False."""
    parser.add_argument(f'--{name}', action='store_true', default=False, help=help_)


def lambda_or_tuple(s: str) -> LambdaOrTupleType:
    """Parse rename option - either a lambda function or a mapping 'old,new'."""
    if s.startswith('lambda'):
        return eval(s)  # pylint: disable=eval-used
    return tuple(s.split(',', maxsplit=1))


def add_rename(parser: argparse.ArgumentParser, what: str) -> None:
    """Add a 'rename' option."""
    parser.add_argument(
        '--rename',
        help=f"Rename a {what} specified as 'old,new' where 'old' is the current name or number "
             f"and 'new' is the new name or as Python lambda function accepting a {what} label as "
             f"input.",
        type=lambda_or_tuple,
        default=None)


def list_of_ranges(dstring: str) -> list[int]:
    """
    Converts a comma-separated list of 1-based ranges into a list of 1-based indices.

    :param dstring: A string

    :return: `list` of zero-based indices
    """
    def _int(v):
        try:
            return int(v)
        except ValueError as exc:  # pragma: no cover
            raise argparse.ArgumentTypeError(f"{v} is not an integer") from exc

    out = []
    if not dstring:
        return out
    for token in dstring.split(','):
        token = token.replace(':', '-')
        if '-' in token:
            start, stop = token.split("-")
            out.extend(list(range(_int(start), _int(stop) + 1)))
        else:
            out.append(_int(token))
    return sorted(out)


def validate_operations(args: argparse.Namespace) -> None:
    """Make sure, only one operation has been selected."""
    if sum(1 for op in Operation if getattr(args, op.name, False)) > 1:
        raise ParserError("Only one operation can be specified")
