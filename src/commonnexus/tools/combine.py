"""
We can handle
- TAXA
- CHARACTERS/DATA
- TREES
- DISTANCES?
"""
import collections

from commonnexus import Nexus
from commonnexus.blocks import Taxa, Trees, Characters

SUPPORTED_BLOCKS = {'TAXA', 'CHARACTERS', 'DATA', 'TREES'}


def combine(*nexus):
    # Make sure we are only dealing with blocks (and datatypes) that we know how to handle.
    for nex in nexus:
        assert set(nex.blocks).issubset(SUPPORTED_BLOCKS)
        for block in SUPPORTED_BLOCKS:
            assert len(nex.blocks.get(block, [])) <= 1
        if (nex.DATA or nex.CHARACTERS) and (nex.DATA or nex.CHARACTERS).FORMAT:
            assert (nex.DATA or nex.CHARACTERS).FORMAT.datatype == 'STANDARD'

    # Determine the superset of taxa.
    taxa = []
    for i, nex in enumerate(nexus, start=1):
        for taxon in (nex.get_taxa() or []):
            if taxon not in taxa:
                taxa.append(taxon)

    # Create a super-matrix, with all taxa and all characters.
    matrices = []
    charlabels = collections.defaultdict(list)
    for i, nex in enumerate(nexus, start=1):
        if nex.has_matrix():
            matrices.append(nex.get_matrix())
            for chars in matrices[-1].values():
                for charlabel in chars:
                    charlabels[i] = charlabel
                break
    matrix = collections.OrderedDict()
    if matrices:
        for taxon in taxa:
            row = collections.OrderedDict()
            for i, m in enumerate(matrices, start=1):
                if taxon in m:
                    for charlabel, val in m[taxon].items():
                        row['{}.{}'.format(i, charlabel)] = val
                else:
                    for charlabel in charlabels[i]:
                        row['{}.{}'.format(i, charlabel)] = None
            matrix[taxon] = row

    # Add all translated trees.
    trees = []
    for i, nex in enumerate(nexus, start=1):
        if nex.TREES:
            for tree in nex.TREES.commands['TREE']:
                nwk = nex.TREES.translate(tree) if nex.TREES.TRANSLATE else tree.newick
                trees.append(('{}.{}'.format(i, tree.name), nwk, tree.rooted))

    nex = Nexus()
    nex.append_block(Taxa.from_data(taxa))
    if matrix:
        nex.append_block(Characters.from_data(matrix))
    if trees:
        nex.append_block(Trees.from_data(*trees))

    return nex
