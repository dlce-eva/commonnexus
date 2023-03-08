"""
Manipulate the CHARACTERS (or DATA) block of a NEXUS file.

Note: Only one option can be chosen at a time.
"""
import collections
from enum import Enum

from commonnexus.blocks.characters import Characters, GAP
from commonnexus.tools.matrix import CharacterMatrix
from commonnexus.cli_util import add_nexus, add_flag, validate_operations


class Ops(Enum):
    binarise = 1
    multistatise = 2
    convert = 3
    drop = 4
    describe = 5


def register(parser):
    add_nexus(parser)
    add_flag(
        parser,
        Ops.binarise.name,
        help="Recode a matrix such that it only contains binary characters.")
    add_flag(
        parser,
        Ops.multistatise.name,
        help="Recode a matrix such that it only contains one multistate character.")
    parser.add_argument(
        '--' + Ops.convert.name,
        choices=['fasta', 'phylip'],
        help="Convert a matrix to another sequence format.")
    parser.add_argument(
        '--' + Ops.drop.name,
        help="Drop specified characters from a matrix.",
        choices='constant polymorphic uncertain missing gapped'.split())
    parser.add_argument(
        '--' + Ops.describe.name,
        help="",
        choices=['binary-setsize', 'binary-unique', 'binary-constant', 'states-distribution'])


def run(args):
    validate_operations(Ops, args)
    new = None
    if args.binarise:
        if args.nexus.characters:
            if args.nexus.characters.FORMAT:  # pragma: no cover
                assert args.nexus.characters.FORMAT.datatype is None or \
                       args.nexus.characters.FORMAT.datatype == 'STANDARD'
        new = CharacterMatrix.binarised(args.nexus.characters.get_matrix())
    elif args.multistatise:
        new = CharacterMatrix.multistatised(args.nexus.characters.get_matrix())
    elif args.drop:
        #
        # FIXME: drop unique - for binary matrices
        #
        kw = {'drop_{}'.format(args.drop): True}
        new = CharacterMatrix.from_characters(args.nexus.characters.get_matrix(), **kw)
    elif args.convert:
        m = CharacterMatrix(args.nexus.characters.get_matrix())
        print(getattr(m, 'to_' + args.convert)())
        return
    elif args.describe:
        m = CharacterMatrix(args.nexus.characters.get_matrix())
        chars = m.characters
        chars = collections.OrderedDict([(chars[i], col) for i, col in enumerate(m.iter_columns())])

        if args.describe == 'binary-setsize':
            assert m.is_binary
            args.log.info('Character set sizes (for binary matrix):')
            for k, v in chars.items():
                print('{} {}'.format(k, sum(1 for vv in v if vv and '1' in vv)))
        elif args.describe == 'binary-unique':
            assert m.is_binary
            args.log.info('Unique character sets (for binary matrix):')
            for k, v in chars.items():
                if sum(1 for vv in v if vv and '1' in vv) == 1:
                    print(k)
        elif args.describe == 'binary-constant':
            assert m.is_binary
            args.log.info('Constant characters (for binary matrix):')
            for k, v in chars.items():
                if len(set(v)) == 1:
                    print(k)
        elif args.describe == 'states-distribution':
            args.log.info('State distribution\nchar\tstate\tcount')
            for char, states in chars.items():
                states = collections.Counter(
                    [frozenset(v) if isinstance(v, set) else v for v in states])
                for k, v in states.most_common():
                    print('{}\t{}\t{}'.format(
                        char, '?' if k is None else ('-' if k == GAP else k), v))
        return

    if new:
        args.nexus.replace_block(args.nexus.characters, Characters.from_data(new))
        print(args.nexus)
        return
    matrix = CharacterMatrix(args.nexus.characters.get_matrix())
    args.log.info('{} block with {} taxa and {} characters.'.format(
        args.nexus.characters.name, len(matrix.taxa), len(matrix.characters)))
