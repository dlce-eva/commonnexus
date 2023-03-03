from commonnexus.tools import normalise
from commonnexus.cli_util import add_nexus


def help():
    return normalise.__doc__


def register(parser):
    add_nexus(parser)


def run(args):
    print(normalise.normalise(args.nexus))
