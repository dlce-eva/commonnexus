import pytest

from commonnexus import Nexus
from commonnexus.tools import normalise


def test_normalise(nexus):
    nex = nexus(CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;")
    res = str(normalise(nex))
    assert res == """#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=3;
TAXLABELS 't 1' t2 t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
    't 1' 100
    t2    010
    t3    001;
END;"""
    assert normalise(Nexus(res))
