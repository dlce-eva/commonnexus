import pytest

from commonnexus import Nexus
from commonnexus.tools import normalise


def test_normalise(nexus):
    nex = nexus(
        CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;",
        DISTANCES="FORMAT NODIAGONAL; MATRIX 't 1' t2  1.0 t3 2.0 3.0;",
        TREES="TRANSLATE a 't 1', b t2, c t3; TREE 1 = (a,b,c);")
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
END;
BEGIN DISTANCES;
DIMENSIONS NTAX=3;
FORMAT TRIANGLE=BOTH MISSING=?;
MATRIX 
    't 1' 0 1.0 2.0
    t2    1.0 0 3.0
    t3    2.0 3.0 0;
END;
BEGIN TREES;
TREE 1 = ('t 1',t2,t3);
END;"""
    res = normalise(Nexus(res))
    assert res.get_character_matrix()
    assert res.DISTANCES.get_matrix()
