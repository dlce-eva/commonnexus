"""
Manipulate a TREES block in a NEXUS file.

Note: Only one option can be chosen at a time.
"""
import enum
import random

from commonnexus.blocks import Trees
from commonnexus.cli_util import (
    add_nexus, add_flag, list_of_ranges, validate_operations, add_rename, LambdaOrTupleType,
)


class Ops(enum.Enum):
    """Available operations, aka subsubcommands."""
    drop = 1  # pylint: disable=invalid-name
    sample = 2  # pylint: disable=invalid-name
    random = 3  # pylint: disable=invalid-name
    strip_comments = 4  # pylint: disable=invalid-name
    rename = 5  # pylint: disable=invalid-name


def register(parser):  # pylint: disable=missing-function-docstring
    add_nexus(parser)
    parser.add_argument(
        "--drop",
        default=[],
        type=list_of_ranges,
        help="Remove the trees specified as comma-separated ranges of 1-based indices, "
             "e.g. '1', '1-5', '1,20-30'")
    parser.add_argument(
        "--sample",
        type=int,
        metavar='N',
        default=0,
        help="Resample the trees every Nth tree")
    parser.add_argument(
        "--random",
        type=int,
        metavar='N',
        default=0,
        help="Randomly sample N trees from the treefile")
    parser.add_argument(
        '--random-seed',
        help="Set random seed (to a number) to allow for reproducible random sampling.",
        type=lambda s: random.seed(int(s)))
    parser.add_argument(
        "--strip-comments",
        action="store_true",
        default=False,
        help="Remove comments from the trees")
    add_rename(parser, 'tree')
    add_flag(parser, 'describe', 'list 1-based index, names and rooting of trees')


def run(args):  # pylint: disable=missing-function-docstring
    validate_operations(args)
    if args.describe:
        args.log.info('Trees\nindex\tname\trooted')
        for i, tree in enumerate(args.nexus.TREES.trees, start=1):
            print('{}\t{}\t{}'.format(i, tree.name, tree.rooted))  # pylint: disable=C0209
        return

    trees = [cmd for cmd in args.nexus.TREES if cmd.name == 'TREE']
    if args.drop:
        drop(args.drop, args.nexus, trees)
    elif args.sample:
        sample(args.sample, args.nexus, trees)
    elif args.random:
        random_(args.random, args.nexus, trees)
    elif args.strip_comments:
        strip_comments(args.nexus)
    elif args.rename:
        rename(args.rename, args.nexus)

    print(args.nexus)


def drop(what, nexus, trees):  # pylint: disable=missing-function-docstring
    for i, tree in enumerate(trees, start=1):
        if i in what:
            nexus.remove(tree)


def sample(num, nexus, trees):  # pylint: disable=missing-function-docstring
    for i, tree in enumerate(trees, start=1):
        if i % num != 0:
            nexus.remove(tree)


def random_(num, nexus, trees):  # pylint: disable=missing-function-docstring
    sampled = random.sample(trees, num)
    for tree in trees:
        if tree not in sampled:
            nexus.remove(tree)


def strip_comments(nexus):  # pylint: disable=missing-function-docstring
    trees = []
    for tree in nexus.TREES.trees:
        trees.append((tree.name, tree.newick.strip_comments(), tree.rooted))
    labels = nexus.TREES.TRANSLATE.mapping if nexus.TREES.TRANSLATE else {}
    nexus.replace_block(nexus.TREES, Trees.from_data(*trees, **labels))


def rename(what: LambdaOrTupleType, nexus):  # pylint: disable=missing-function-docstring
    trees = []
    for number, tree in enumerate(nexus.TREES.trees, start=1):
        tname = tree.name
        if callable(what):
            tname = what(tree.name)
        elif what[0] == str(number) or what[0] == tree.name:
            tname = what[1]
        trees.append((tname, tree.newick, tree.rooted))
    labels = nexus.TREES.TRANSLATE.mapping if nexus.TREES.TRANSLATE else {}
    nexus.replace_block(nexus.TREES, Trees.from_data(*trees, **labels))
