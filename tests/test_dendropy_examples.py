import pytest

from commonnexus import Nexus


@pytest.mark.dendropy
def test_dendropy_suite(dendropyexample):
    n = Nexus(dendropyexample, ignore_unsupported=True)
    assert str(n).strip() == dendropyexample.strip()
    for name, blocks in n.blocks.items():
        for block in blocks:
            _ = block.commands  # We have to access `commands` to actually parse command payloads.
    if n.characters:
        if n.characters.FORMAT and n.characters.FORMAT.datatype == 'CONTINUOUS':
            pass
        else:
            _ = n.characters.get_matrix()
    if n.TREES:
        for tree in n.TREES.trees:
            _ = tree.newick
    assert not n.DISTANCES
