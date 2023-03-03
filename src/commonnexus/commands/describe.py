import collections

from commonnexus.cli_util import add_nexus

# for binary matrices:
# - unique sites
# - list constant characters

def help():
    return "describe"


def add_flag(parser, name, help):
    parser.add_argument('--{}'.format(name), action='store_true', default=False, help=help)


def register(parser):
    add_nexus(parser)
    add_flag(
        parser,
        'binary-character-size',
        'List characters and number of taxa coded as 1 (for binary character matrices).')
    add_flag(
        parser,
        'binary-unique-characters',
        'List characters which have only one taxon coded as 1 (for binary character matrices).')
    add_flag(
        parser,
        'binary-constant-characters',
        'List characters which have all taxa coded the same (for binary character matrices).')


def get_binary_characters(nexus):
    assert nexus.characters and nexus.characters.is_binary()
    matrix = nexus.characters.get_matrix()
    characters = collections.OrderedDict()
    for i, sites in enumerate(matrix.values()):
        for char, state in sites.items():
            if i == 0:
                characters[char] = []
            characters[char].append(state)
    return characters


def run(args):
    args.log.info('NEXUS file with blocks {}\n'.format(', '.join(args.nexus.blocks)))

    if args.binary_character_size:
        args.log.info('Character set sizes (for binary matrix):')
        chars = get_binary_characters(args.nexus)
        for k, v in chars.items():
            print('{} {}'.format(k, sum(1 for vv in v if vv and '1' in vv)))

    if args.binary_unique_characters:
        args.log.info('Unique character sets (for binary matrix):')
        chars = get_binary_characters(args.nexus)
        for k, v in chars.items():
            if sum(1 for vv in v if vv and '1' in vv) == 1:
                print(k)

    if args.binary_constant_characters:
        args.log.info('Constant characters (for binary matrix):')
        chars = get_binary_characters(args.nexus)
        for k, v in chars.items():
            if len(set(v)) == 1:
                print(k)
