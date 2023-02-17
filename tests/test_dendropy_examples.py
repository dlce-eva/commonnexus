import pytest

from commonnexus import Nexus


@pytest.mark.dendropy
def test_dendropy_suite(dendropyexample):
    n = Nexus(dendropyexample, ignore_unsupported=True)
    assert str(n).strip() == dendropyexample.strip()
    for name, blocks in n.blocks.items():
        for block in blocks:
            _ = block.commands
