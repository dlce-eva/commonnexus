# pylint: disable=missing-module-docstring
from commonnexus.tools import normalise
from commonnexus.cli_util import add_nexus, add_flag


def help():  # pylint: disable=missing-function-docstring,redefined-builtin
    return normalise.__doc__


def register(parser):  # pylint: disable=missing-function-docstring
    add_nexus(parser)
    add_flag(parser, 'strip-comments', 'Remove non-command comments.')


def run(args):  # pylint: disable=missing-function-docstring
    print(normalise.normalise(args.nexus, strip_comments=args.strip_comments))
