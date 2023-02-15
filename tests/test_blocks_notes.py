from commonnexus import Nexus


def test_Notes():
    nex = Nexus("""#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=5;
TAXLABELS t1 't2 x' t3 t4 t5;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
CHARSTATELABELS 1 c1/c1.0 c1.1, 2 c2, 3 c3;
END;
BEGIN NOTES;
TEXT SOURCE=INLINE TAXON=(1-3) CHARACTER=1 STATE=1 TEXT= 'these taxa from the far north';
END;""")
    assert nex.NOTES.TEXT.taxons == ['t1', "t2 x", 't3']
    assert nex.NOTES.TEXT.characters == ['c1']
    assert nex.NOTES.TEXT.states == {'c1': ['c1.0']}


def test_Notes_2():
    nex = Nexus("""#NEXUS
BEGIN TREES;
TREE 'the tree' = (,):2;
END;
BEGIN CHARACTERS;
DIMENSIONS NEWTAXA NTAX=5 NCHAR=3;
TAXLABELS t1 't2 x' t3 t4 t5;
CHARSTATELABELS 1 c1/c1.0 c1.1, 2 c2, 3 c3;
END;
BEGIN NOTES;
TEXT SOURCE=INLINE TAXON=(1 3) TREE=1 TEXT= 'these taxa from the far north';
END;""")
    assert nex.NOTES.TEXT.taxons == ['t1', 't3']
    assert nex.NOTES.TEXT.trees == ['the tree']


def test_Notes_3():
    nex = Nexus("""#NEXUS
BEGIN CHARACTERS;
DIMENSIONS NEWTAXA NTAX=5 NCHAR=3;
END;
BEGIN NOTES;
TEXT SOURCE=INLINE TAXON=(1 3) TEXT= 'these taxa from the far north';
END;""")
    assert nex.NOTES.TEXT.taxons == ['1', '3']
