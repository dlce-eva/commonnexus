import pytest

from commonnexus.tools import normalise


def test_normalise(nexus):
    nex = nexus(TAXA="DIMENSIONS NTAX=3;")
    with pytest.raises(NotImplementedError):
        normalise(nex)
