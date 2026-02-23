"""
Manipulate the list of TAXA used in a NEXUS file.
"""
import collections
import typing

from commonnexus.cli_util import add_nexus, add_flag, ParserError, add_rename
from commonnexus.blocks import Data, Characters, Trees, Taxa, Distances
from commonnexus.blocks.characters import GAP


def register(parser):  # pylint: disable=missing-function-docstring
    add_nexus(parser)
    parser.add_argument(
        '--drop',
        help="Comma-separated list of taxon labels or numbers to remove from the NEXUS. This will "
             "remove the taxa from the TAXA block, the relevant rows from a CHARACTERS (or DATA) "
             "matrix, and prune the specified taxa from any TREE in a TREES block.",
        type=lambda s: s.split(','),
        default=[])
    add_rename(parser, 'taxon')
    parser.add_argument(
        '--describe',
        help="Describe a named taxon, i.e. aggregate the data for the taxon in a NEXUS file.",
        default=None)
    add_flag(parser, 'check', 'Check whether taxa labels in a NEXUS file are used consistently.')


def run(args):  # pylint: disable=missing-function-docstring
    taxa = collections.OrderedDict(
        [(str(i), taxon) for i, taxon in enumerate(args.nexus.taxa, start=1)])

    if args.drop or args.rename:
        if args.drop:
            drop(args.drop, args.nexus, taxa, args.log)

        if args.rename:
            rename(args.rename, args.nexus, taxa, args.log)

        args.nexus.validate(args.log)
        print(args.nexus)
        return

    if args.check:
        check(args.nexus, taxa, args.log)
        return

    if args.describe:
        describe(args.describe, args.nexus, taxa)
        return

    args.log.info('Taxa:\nnumber\tlabel')
    for i, taxon in taxa.items():
        print('{}\t{}'.format(i, taxon))  # pylint: disable=consider-using-f-string


def rename_in_characters(nexus, mapping):  # pylint: disable=missing-function-docstring
    matrix = nexus.characters.get_matrix()
    if set(matrix).intersection(mapping):
        matrix = collections.OrderedDict(
            [(mapping.get(k, k), v) for k, v in matrix.items()])
        nexus.replace_block(nexus.characters, Characters.from_data(matrix))


def rename_in_distances(nexus, mapping):  # pylint: disable=missing-function-docstring
    matrix = collections.OrderedDict()
    for tax, dists in nexus.DISTANCES.get_matrix().items():
        matrix[mapping.get(tax, tax)] = collections.OrderedDict([
            (mapping.get(k, k), v) for k, v in dists.items()])
    nexus.replace_block(nexus.DISTANCES, Distances.from_data(matrix))


def rename_in_trees(nexus, mapping):  # pylint: disable=missing-function-docstring
    labels = {}
    if nexus.TREES.TRANSLATE:
        labels = collections.OrderedDict([
            (k, mapping.get(v, v))
            for k, v in nexus.TREES.TRANSLATE.mapping.items()])
    trees = []
    for tree in nexus.TREES.trees:
        trees.append((tree.name, tree.newick.rename(**mapping), tree.rooted))
    nexus.replace_block(nexus.TREES, Trees.from_data(*trees, **labels))


def rename(what, nexus, taxa, log) -> None:  # pylint: disable=missing-function-docstring
    mapping = {}
    if callable(what):
        for number, label in taxa.items():
            new = what(label)
            if new != label:
                taxa[number] = mapping[number] = mapping[label] = new
    else:
        old, new = what
        for number, label in taxa.items():
            if old in (number, label):
                taxa[number] = mapping[number] = mapping[old] = new
                break
        else:
            raise ParserError(f'No taxon matching {old} found')  # pragma: no cover

    for attr, renamer in [
        (nexus.characters, rename_in_characters),
        (nexus.DISTANCES, rename_in_distances),
        (nexus.TREES, rename_in_trees),
    ]:
        if attr:
            renamer(nexus, mapping)

    if nexus.NOTES:  # pragma: no cover
        log.warning('Changing taxon sets in NOTES block is not supported.')

    if nexus.TAXA:
        nexus.replace_block(nexus.TAXA, Taxa.from_data(taxa.values()))
    else:
        nexus.append_block(Taxa.from_data(taxa.values()))


def drop_in_characters(nexus, to_drop):  # pylint: disable=missing-function-docstring
    matrix = nexus.characters.get_matrix()
    for taxon in list(matrix.keys()):
        if taxon in to_drop or (taxon in to_drop.values()):
            del matrix[taxon]
    characters = (Data if nexus.characters.name == 'DATA' else Characters) \
        .from_data(matrix)
    nexus.replace_block(nexus.characters, characters)


def drop_in_trees(nexus, to_drop):  # pylint: disable=missing-function-docstring
    trees = []
    for tree in nexus.TREES.trees:
        if nexus.TREES.TRANSLATE:
            nwk = nexus.TREES.translate(tree)
        else:
            nwk = tree.newick
        nwk.prune_by_names(list(to_drop) + list(to_drop.values()))
        trees.append((tree.name, nwk, tree.rooted))
    nexus.replace_block(nexus.TREES, Trees.from_data(*trees))


def drop_in_distances(nexus, to_drop):  # pylint: disable=missing-function-docstring
    matrix = nexus.DISTANCES.get_matrix()
    for taxon in list(matrix.keys()):
        if taxon in to_drop or (taxon in to_drop.values()):
            del matrix[taxon]  # pragma: no cover

    for dists in matrix.values():
        for taxon in list(dists.keys()):
            if taxon in to_drop or (taxon in to_drop.values()):
                del dists[taxon]  # pragma: no cover

    nexus.replace_block(nexus.DISTANCES, Distances.from_data(matrix))


def drop(what, nexus, taxa, log) -> None:  # pylint: disable=missing-function-docstring
    to_drop, to_keep = collections.OrderedDict(), []
    for k, v in taxa.items():
        if k in what or (v in what):
            to_drop[k] = v
        else:
            to_keep.append(v)

    if nexus.characters:
        drop_in_characters(nexus, to_drop)

    if nexus.TREES:
        drop_in_trees(nexus, to_drop)

    if nexus.DISTANCES:
        drop_in_distances(nexus, to_drop)

    if nexus.NOTES:  # pragma: no cover
        log.warning('Changing taxon sets in NOTES block is not supported.')

    if nexus.TAXA:
        nexus.replace_block(nexus.TAXA, Taxa.from_data(to_keep))
    else:
        nexus.append_block(Taxa.from_data(to_keep))


def check(nexus, taxa, log):  # pylint: disable=missing-function-docstring
    if nexus.characters:
        mtaxa = list(nexus.characters.get_matrix())
        if len(set(mtaxa).intersection(set(taxa).union(taxa.values()))) < len(taxa):
            log.warning('Not all taxa appear in characters matrix')
    if nexus.DISTANCES:
        nexus.DISTANCES.get_matrix()
    if nexus.TREES:
        if nexus.TREES.TRANSLATE:
            if not set(nexus.TREES.TRANSLATE.mapping.values()) \
                    .issubset(set(taxa.values())):
                log.error('Invalid taxa labels in TREES TRANSLATE.')
        for tree in nexus.TREES.trees:
            nwk = nexus.TREES.translate(tree)
            leafnames = {n.name for n in nwk.walk() if n.name and n.is_leaf}
            if not leafnames.issubset(taxa.values()):
                log.error('Invalid taxa labels as leaf name in TREE.')
            names = {n.name for n in nwk.walk() if n.name and not n.is_leaf}
            if not names.issubset(taxa.values()):
                log.warning('Invalid taxa labels as inner node name in TREE.')


def describe(what: str, nexus, taxa: typing.Dict):  # pylint: disable=missing-function-docstring
    for num, name in taxa.items():
        if what in (num, name):
            break
    else:
        raise ValueError('Taxon not found')  # pragma: no cover
    print(f'# {name}\n')
    charnotes = collections.defaultdict(list)
    if nexus.NOTES:
        for text in nexus.NOTES.texts:
            for char in text.characters or []:
                charnotes[char].append(text.text)
    if nexus.characters:
        m = nexus.characters.get_matrix(labeled_states=True)
        print('Character | State | Notes')
        print('--- | --- | ---')
        for char, state in m[name].items():
            notes = '/'.join(charnotes.get(char, []))
            state_symbol = '?' if state is None else ('-' if state == GAP else state)
            print(f'{char} | {state_symbol} | {notes}')
    if nexus.TREES:
        print(f'\n## Tree {nexus.TREES.TREE.name}\n')
        tree = nexus.TREES.translate(nexus.TREES.TREE)
        print('```')
        print(tree.ascii_art())
        print('```')
    if nexus.NOTES:
        for i, text in enumerate(nexus.NOTES.get_texts(taxon=name)):
            if i == 0:
                print('\n## Notes\n')
                print('Character | Note')
                print('--- | ---')
            char = '/'.join(text.characters or [])
            print(f'{char} | {text.text.strip()}')
