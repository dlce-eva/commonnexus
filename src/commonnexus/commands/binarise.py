"""
Recode a CHARACTERS (or DATA) matrix such that it only contains binary characters.
"""
from commonnexus.blocks.characters import Characters
from commonnexus.tools.matrix import CharacterMatrix
from commonnexus.cli_util import add_nexus


def help():
    return __doc__


def register(parser):
    add_nexus(parser)


def run(args):
    if args.nexus.characters:
        if args.nexus.characters.FORMAT:  # pragma: no cover
            assert args.nexus.characters.FORMAT.datatype is None or \
                args.nexus.characters.FORMAT.datatype == 'STANDARD'

    args.nexus.replace_block(
        args.nexus.characters,
        Characters.from_data(CharacterMatrix.binarised(args.nexus.characters.get_matrix())))
    print(args.nexus)
