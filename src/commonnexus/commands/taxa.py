"""
Manipulate the list of TAXA used in a NEXUS file.
"""
import warnings
import collections

from commonnexus.cli_util import add_nexus, add_flag, ParserError
from commonnexus.blocks import Data, Characters, Trees, Taxa, Distances


def register(parser):
    add_nexus(parser)
    parser.add_argument(
        '--drop',
        help="Comma-separated list of taxon labels or numbers to remove from the NEXUS. This will "
             "remove the taxa from the TAXA block, the relevant rows from a CHARACTERS (or DATA) "
             "matrix, and prune the specified taxa from any TREE in a TREES block.",
        type=lambda s: s.split(','),
        default=[])
    parser.add_argument(
        '--rename',
        help="Rename a taxon specified as 'old,new' where 'old' is the current name or number and "
             "'new' is the new name.",
        type=lambda s: s.split(','),
        default=None)
    add_flag(parser, 'check', 'Check whether taxa labels in a NEXUS file are used consistently.')


def run(args):
    taxa = collections.OrderedDict(
        [(str(i), taxon) for i, taxon in enumerate(args.nexus.taxa, start=1)])

    if args.drop or args.rename:
        if args.drop:
            to_drop, to_keep = collections.OrderedDict(), []
            for k, v in taxa.items():
                if k in args.drop or (v in args.drop):
                    to_drop[k] = v
                else:
                    to_keep.append(v)

            if args.nexus.characters:
                matrix = args.nexus.characters.get_matrix()
                for taxon in list(matrix.keys()):
                    if taxon in to_drop or (taxon in to_drop.values()):
                        del matrix[taxon]
                characters = (Data if args.nexus.characters.name == 'DATA' else Characters).from_data(
                    matrix)
                args.nexus.replace_block(args.nexus.characters, characters)
            if args.nexus.TREES:
                trees = []
                for tree in args.nexus.TREES.trees:
                    if args.nexus.TREES.TRANSLATE:
                        nwk = args.nexus.TREES.translate(tree)
                    else:
                        nwk = tree.newick
                    nwk.prune_by_names(list(to_drop) + list(to_drop.values()))
                    trees.append((tree.name, nwk, tree.rooted))
                args.nexus.replace_block(args.nexus.TREES, Trees.from_data(*trees))

            if args.nexus.DISTANCES:
                matrix = args.nexus.DISTANCES.get_matrix()
                for taxon in list(matrix.keys()):
                    if taxon in to_drop or (taxon in to_drop.values()):
                        del matrix[taxon]  # pragma: no cover

                for dists in matrix.values():
                    for taxon in list(dists.keys()):
                        if taxon in to_drop or (taxon in to_drop.values()):
                            del dists[taxon]  # pragma: no cover

                args.nexus.replace_block(args.nexus.DISTANCES, Distances.from_data(matrix))

            if args.nexus.TAXA:
                args.nexus.replace_block(args.nexus.TAXA, Taxa.from_data(to_keep))
            else:
                args.nexus.append_block(Taxa.from_data(to_keep))

        if args.rename:
            assert len(args.rename) == 2
            old, new = args.rename
            for number, label in taxa.items():
                if old == number or old == label:
                    break
            else:
                raise ParserError('No taxon matching {} found'.format(old))  # pragma: no cover

            taxa[number] = new
            if args.nexus.characters:
                matrix = args.nexus.characters.get_matrix()
                if number in matrix or label in matrix:
                    matrix = collections.OrderedDict([
                        (new if k == number or k == label else k, v) for k, v in matrix.items()])
                    args.nexus.replace_block(args.nexus.characters, Characters.from_data(matrix))
            if args.nexus.DISTANCES:
                matrix = collections.OrderedDict()
                for tax, dists in args.nexus.DISTANCES.get_matrix().items():
                    matrix[new if tax == number or tax == label else tax] = collections.OrderedDict([
                        (new if k == number or k == label else k, v) for k, v in dists.items()])
                args.nexus.replace_block(args.nexus.DISTANCES, Distances.from_data(matrix))
            if args.nexus.TREES:
                labels = {}
                if args.nexus.TREES.TRANSLATE:
                    labels = collections.OrderedDict(
                        [(k, new if v == number or v == label else v)
                         for k, v in args.nexus.TREES.TRANSLATE.mapping.items()])
                trees = []
                for tree in args.nexus.TREES.trees:
                    trees.append((
                        tree.name, tree.newick.rename(**{number: new, label: new}), tree.rooted))
                args.nexus.replace_block(args.nexus.TREES, Trees.from_data(*trees, **labels))
            if args.nexus.TAXA:
                args.nexus.replace_block(args.nexus.TAXA, Taxa.from_data(taxa.values()))
            else:
                args.nexus.append_block(Taxa.from_data(taxa.values()))

        args.nexus.validate(args.log)
        print(args.nexus)
        return

    if args.check:
        if args.nexus.characters:
            mtaxa = list(args.nexus.characters.get_matrix())
            if len(set(mtaxa).intersection(set(taxa).union(taxa.values()))) < len(taxa):
                args.log.warning('Not all taxa appear in characters matrix')
        if args.nexus.DISTANCES:
            args.nexus.DISTANCES.get_matrix()
        if args.nexus.TREES:
            if args.nexus.TREES.TRANSLATE:
                if not set(args.nexus.TREES.TRANSLATE.mapping.values())\
                        .issubset(set(taxa.values())):
                    args.log.error('Invalid taxa labels in TREES TRANSLATE.')
            for tree in args.nexus.TREES.trees:
                nwk = args.nexus.TREES.translate(tree)
                leafnames = {n.name for n in nwk.walk() if n.name and n.is_leaf}
                if not leafnames.issubset(taxa.values()):
                    args.log.error('Invalid taxa labels as leaf name in TREE.')
                names = {n.name for n in nwk.walk() if n.name and not n.is_leaf}
                if not names.issubset(taxa.values()):
                    args.log.warning('Invalid taxa labels as inner node name in TREE.')
        return

    args.log.info('Taxa:\nnumber\tlabel')
    for i, taxon in taxa.items():
        print('{}\t{}'.format(i, taxon))
