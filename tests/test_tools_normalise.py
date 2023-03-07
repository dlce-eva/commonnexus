from commonnexus import Nexus
from commonnexus.tools.normalise import normalise


def test_normalise(nexus):
    nex = nexus(
        CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;",
        DISTANCES="FORMAT NODIAGONAL; MATRIX 't 1' t2  1.0 t3 2.0 3.0;",
        TREES="TRANSLATE a 't 1', b t2, c t3; TREE 1 = (a,b\n,c);")
    res = str(normalise(nex))
    assert res == """#NEXUS
BEGIN TAXA;
\tDIMENSIONS NTAX=3;
\tTAXLABELS 't 1' t2 t3;
END;
BEGIN CHARACTERS;
\tDIMENSIONS NCHAR=3;
\tFORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
\tMATRIX 
    't 1' 100
    t2    010
    t3    001;
END;
BEGIN DISTANCES;
\tDIMENSIONS NTAX=3;
\tFORMAT TRIANGLE=BOTH MISSING=?;
\tMATRIX 
    't 1' 0 1.0 2.0
    t2    1.0 0 3.0
    t3    2.0 3.0 0;
END;
BEGIN TREES;
\tTREE 1 = ('t 1',t2,t3);
END;"""
    res = normalise(Nexus(res))
    assert res.characters.get_matrix()
    assert res.DISTANCES.get_matrix()

    res.remove_block(res.TAXA)
    res.remove_block(res.CHARACTERS)
    res = normalise(res)
    assert res.TAXA


def test_normalise_stripcomments():
    res = normalise(Nexus('#nexus beg[c]in bl[&c]ock; cmd; end[c];'), strip_comments=True)
    assert '[c]' not in str(res)
    assert '[&c]' in str(res)
    assert res.BLOCK
