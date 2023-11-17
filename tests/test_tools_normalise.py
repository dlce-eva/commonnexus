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
DIMENSIONS NTAX=3;
TAXLABELS 't 1' t2 t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
't 1' 100
t2    010
t3    001
;
END;
BEGIN DISTANCES;
DIMENSIONS NTAX=3;
FORMAT TRIANGLE=BOTH MISSING=?;
MATRIX 
't 1' 0 1.0 2.0
t2    1.0 0 3.0
t3    2.0 3.0 0
;
END;
BEGIN TREES;
TREE 1 = ('t 1',t2,t3);
END;"""
    res = normalise(Nexus(res))
    assert res.characters.get_matrix()
    assert res.DISTANCES.get_matrix()

    res.remove_block(res.TAXA)
    res.remove_block(res.CHARACTERS)
    res = normalise(res)
    assert res.TAXA


def test_normalise_remove_taxon(nexus):
    nex = nexus(
        CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;",
        DISTANCES="FORMAT NODIAGONAL; MATRIX 't 1' t2  1.0 t3 2.0 3.0;",
        TREES="TRANSLATE a 't 1', b t2, c t3; TREE 1 = (a,b\n,c);")
    res = str(normalise(nex, remove_taxa={'t2'}))
    assert res == """#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=2;
TAXLABELS 't 1' t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
't 1' 100
t3    001
;
END;
BEGIN DISTANCES;
DIMENSIONS NTAX=2;
FORMAT TRIANGLE=BOTH MISSING=?;
MATRIX 
't 1' 0 2.0
t3    2.0 0
;
END;
BEGIN TREES;
TREE 1 = ('t 1',t3);
END;"""


def test_normalise_rename_taxon1(nexus):
    nex = nexus(
        CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;",
        DISTANCES="FORMAT NODIAGONAL; MATRIX 't 1' t2  1.0 t3 2.0 3.0;",
        TREES="TRANSLATE a 't 1', b t2, c t3; TREE 1 = (a,b\n,c);")
    res = str(normalise(nex, rename_taxa={'t 1': 't1'}))
    assert res == """#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=3;
TAXLABELS t1 t2 t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
t1 100
t2 010
t3 001
;
END;
BEGIN DISTANCES;
DIMENSIONS NTAX=3;
FORMAT TRIANGLE=BOTH MISSING=?;
MATRIX 
t1 0 1.0 2.0
t2 1.0 0 3.0
t3 2.0 3.0 0
;
END;
BEGIN TREES;
TREE 1 = (t1,t2,t3);
END;"""


def test_normalise_rename_taxon2(nexus):
    nex = nexus(
        CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;",
        DISTANCES="FORMAT NODIAGONAL; MATRIX 't 1' t2  1.0 t3 2.0 3.0;",
        TREES="TRANSLATE a 't 1', b t2, c t3; TREE 1 = (a,b\n,c);")
    res = str(normalise(nex, rename_taxa=lambda t: t.replace(' ', '_')))
    assert res == """#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=3;
TAXLABELS t_1 t2 t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
t_1 100
t2  010
t3  001
;
END;
BEGIN DISTANCES;
DIMENSIONS NTAX=3;
FORMAT TRIANGLE=BOTH MISSING=?;
MATRIX 
t_1 0 1.0 2.0
t2  1.0 0 3.0
t3  2.0 3.0 0
;
END;
BEGIN TREES;
TREE 1 = (t_1,t2,t3);
END;"""


def test_normalise_rename_taxon3(nexus):
    nex = nexus(
        CHARACTERS="DIMENSIONS NCHAR=3; MATRIX 't 1' 100 t2 010 t3 001;",
        DISTANCES="FORMAT NODIAGONAL; MATRIX 't 1' t2  1.0 t3 2.0 3.0;",
        TREES="TRANSLATE a 't 1', b t2, c t3; TREE 1 = (a,b\n,c);")
    res = str(normalise(nex, rename_taxa=lambda t: t.replace(' ', ':')))
    assert res == """#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=3;
TAXLABELS 't:1' t2 t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
't:1' 100
t2    010
t3    001
;
END;
BEGIN DISTANCES;
DIMENSIONS NTAX=3;
FORMAT TRIANGLE=BOTH MISSING=?;
MATRIX 
't:1' 0 1.0 2.0
t2    1.0 0 3.0
t3    2.0 3.0 0
;
END;
BEGIN TREES;
TREE 1 = ('t:1',t2,t3);
END;"""


def test_normalise_stripcomments():
    res = normalise(Nexus('#nexus beg[c]in bl[&c]ock; cmd; end[c];'), strip_comments=True)
    assert '[c]' not in str(res)
    assert '[&c]' in str(res)
    assert res.BLOCK
