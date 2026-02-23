"""
Manipulate the CHARACTERS (or DATA) block of a NEXUS file.

Note: Only one option can be chosen at a time.
"""
import logging
import collections
import dataclasses

from commonnexus import Nexus
from commonnexus.blocks.characters import Characters, GAP
from commonnexus.tools.matrix import CharacterMatrix, DropSpec, DropChars
from commonnexus.tools.combine import combine
from commonnexus.cli_util import add_nexus, add_flag, validate_operations, list_of_ranges, Operation

BOOL_DROP_FIELDS = [f.name for f in dataclasses.fields(DropSpec) if f.type is bool]


#
# It's somewhat hacky to model operations as options rather than as sub(sub)commands, considering
# that only one can be chosen.
#
def register(parser):  # pylint: disable=missing-function-docstring
    add_nexus(parser)
    add_flag(
        parser,
        Operation.binarise.name,
        help_="Recode a matrix such that it only contains binary characters.")
    parser.add_argument(
        '--' + Operation.multistatise.name,
        metavar="GROUPKEY",
        default=None,
        help="Recode a matrix such that it only contains one multistate characters for each "
             "group of characters as determined by GROUPKEY, a Python lambda function accepting "
             "character label and returning a key (or a string to group all characters into one "
             "multistate character labeled with this string).")
    parser.add_argument(
        '--' + Operation.convert.name,
        choices=['fasta', 'phylip'],
        help="Convert a matrix to another sequence format.")
    parser.add_argument(
        '--' + Operation.drop.name,
        help="Drop specified characters from a matrix.",
        choices=BOOL_DROP_FIELDS)
    parser.add_argument(
        '--' + Operation.drop_numbered.name.replace('_', '-'),
        type=list_of_ranges,
        help="Drop characters specified by (ranges of) numbers from a matrix.")
    parser.add_argument(
        '--' + Operation.describe.name,
        help="",
        choices=['binary-setsize', 'binary-unique', 'binary-constant', 'states-distribution'])


def run(args):  # pylint: disable=missing-function-docstring
    validate_operations(args)
    new = None
    if args.binarise:
        if args.nexus.characters.FORMAT:  # pragma: no cover
            assert args.nexus.characters.FORMAT.datatype is None or \
                args.nexus.characters.FORMAT.datatype == 'STANDARD'
        _, statelabels = args.nexus.characters.get_charstatelabels()
        new = CharacterMatrix.binarised(args.nexus.characters.get_matrix(), statelabels=statelabels)
    elif args.multistatise:
        print(multistatise(args.multistatise, args.nexus))
        return
    elif args.drop:
        #
        # FIXME: drop unique - for binary matrices  pylint: disable=fixme
        #
        drop_spec = DropSpec()
        setattr(drop_spec, args.drop, True)
        new = CharacterMatrix.from_characters(args.nexus.characters.get_matrix(), drop=drop_spec)
    elif args.drop_numbered:
        m = CharacterMatrix(args.nexus.characters.get_matrix())
        drop_spec = DropSpec(
            chars=DropChars(
                chars=[c for i, c in enumerate(m.characters, start=1) if i in args.drop_numbered]))
        new = CharacterMatrix.from_characters(m, drop_spec)
    elif args.convert:
        m = CharacterMatrix(args.nexus.characters.get_matrix())
        print(getattr(m, 'to_' + args.convert)())
        return
    elif args.describe:
        describe(args.describe, args.nexus, args.log)
        return

    if new:
        args.nexus.replace_block(args.nexus.characters, Characters.from_data(new))
        print(args.nexus)
        return
    matrix = CharacterMatrix(args.nexus.characters.get_matrix())
    args.log.info(
        f'{args.nexus.characters.name} block '
        f'with {len(matrix.taxa)} taxa and {len(matrix.characters)} characters.')


def multistatise(groupkey_string: str, nexus: Nexus) -> Nexus:
    """Combine binary characters into multi-state characters."""
    if groupkey_string.startswith('lambda'):
        groupkey = eval(groupkey_string)  # pylint: disable=eval-used
    else:
        groupkey = lambda c: groupkey_string  # noqa: E731  pylint: disable=C3001
    charpartitions = collections.defaultdict(list)
    matrix = CharacterMatrix(nexus.characters.get_matrix())
    for char in matrix.characters:
        charpartitions[groupkey(char)].append(char)
    matrices = [
        (key, CharacterMatrix.from_characters(
            matrix, DropSpec(chars=DropChars(chars=chars, inverse=True))))
        for key, chars in charpartitions.items()]
    if len(matrices) == 1:
        new = CharacterMatrix.multistatised(matrices[0][1], multicharlabel=matrices[0][0])
        nexus.replace_block(nexus.characters, Characters.from_data(new))
        new = nexus
    else:
        ms = []
        for key, m in matrices:
            ms.append(CharacterMatrix.multistatised(m, multicharlabel=key))
        new = combine(*[Nexus.from_blocks(Characters.from_data(m)) for m in ms])
    return new


def describe(what: str, nexus: Nexus, log: logging.Logger) -> None:
    """Print some characteristics of the characters matrix to the screen."""
    m = CharacterMatrix(nexus.characters.get_matrix())
    chars = m.characters
    chars = collections.OrderedDict([(chars[i], col) for i, col in enumerate(m.iter_columns())])

    if what == 'binary-setsize':
        assert m.is_binary
        log.info('Character set sizes (for binary matrix):')
        for k, v in chars.items():
            print(f"{k} {sum(1 for vv in v if vv and '1' in vv)}")
    elif what == 'binary-unique':
        assert m.is_binary
        log.info('Unique character sets (for binary matrix):')
        for k, v in chars.items():
            if sum(1 for vv in v if vv and '1' in vv) == 1:
                print(k)
    elif what == 'binary-constant':
        assert m.is_binary
        log.info('Constant characters (for binary matrix):')
        for k, v in chars.items():
            if len(set(v)) == 1:
                print(k)
    elif what == 'states-distribution':
        log.info('State distribution\nchar\tstate\tcount')
        for char, states in chars.items():
            states = collections.Counter(
                [frozenset(v) if isinstance(v, set) else v for v in states])
            for k, v in states.most_common():
                state_symbol = '?' if k is None else ('-' if k == GAP else k)
                print(f'{char}\t{state_symbol}\t{v}')
