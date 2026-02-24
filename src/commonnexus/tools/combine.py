"""
Combine data from multiple NEXUS files and put it in a new one.

The following blocks can be handled:

 - TAXA: Taxa are identified across NEXUS files based on label (not number).
 - CHARACTERS/DATA: Characters are aggregated across NEXUS files (with character labels prefixed,
   for disambiguation).
 - TREES: Trees are (translated and) aggregated across NEXUS files.

"""
import collections

from commonnexus import Nexus
from commonnexus.blocks import Taxa, Trees, Characters
from commonnexus.blocks.characters import StateMatrix

SUPPORTED_BLOCKS = {'TAXA', 'CHARACTERS', 'DATA', 'TREES'}


def combine(*nexus: Nexus, **kw) -> Nexus:
    """
    :param nexus: `Nexus` objects to be combined.
    :return: A new `Nexus` object with the combined data.
    """
    # Make sure we are only dealing with blocks (and datatypes) that we know how to handle.
    for nex in nexus:
        if not kw.get('drop_unsupported', False):
            assert set(nex.blocks).issubset(SUPPORTED_BLOCKS), \
                f"Only {SUPPORTED_BLOCKS} blocks are supported."
        for block in SUPPORTED_BLOCKS:
            assert len(nex.blocks.get(block, [])) <= 1

    # Determine the superset of taxa, preserving the order in which they appear.
    seen = set()
    seen_add = seen.add
    taxa = [
        taxon for nex in nexus for taxon in (nex.taxa or [])
        if not (taxon in seen or seen_add(taxon))]

    # Create a super-matrix, with all taxa and all characters.
    matrices, last_datatype = collections.OrderedDict(), None
    for i, nex in enumerate(nexus, start=1):
        if nex.characters:
            datatype = nex.characters.FORMAT.datatype if nex.characters.FORMAT else 'STANDARD'
            if last_datatype and last_datatype != datatype:
                raise ValueError(
                    'Only CHARACTER or DATA blocks of the same datatype can be combined!')
            last_datatype = datatype
            matrices[i] = nex.characters.get_matrix()

    matrix = merged_matrix(matrices, taxa)

    # Add all translated trees.
    trees = []
    for i, nex in enumerate(nexus, start=1):
        if nex.TREES:
            for tree in nex.TREES.trees:
                nwk = nex.TREES.translate(tree) if nex.TREES.TRANSLATE else tree.newick
                trees.append((f'{i}.{tree.name}', nwk, tree.rooted))

    nex = Nexus()
    if taxa:
        nex.append_block(Taxa.from_data(taxa))
    if matrix:
        nex.append_block(Characters.from_data(matrix))
    if trees:
        nex.append_block(Trees.from_data(*trees))

    return nex


def merged_matrix(
        matrices: collections.OrderedDict[int, StateMatrix],
        taxa: list[str],
) -> StateMatrix:
    """Merge matrices."""
    matrix = collections.OrderedDict()
    if matrices:
        for taxon in taxa:
            row = collections.OrderedDict()
            for i, m in matrices.items():
                charlabels = list(list(m.values())[0].keys())
                if taxon in m:
                    for charlabel, val in m[taxon].items():
                        row['{}.{}'.format(i, charlabel)] = val  # pylint: disable=C0209
                else:
                    for charlabel in charlabels:
                        row['{}.{}'.format(i, charlabel)] = None  # pylint: disable=C0209
            matrix[taxon] = row
    return matrix
