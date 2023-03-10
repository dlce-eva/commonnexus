import pytest

from commonnexus.blocks.notes import Notes


@pytest.mark.parametrize(
    'spec,expect',
    [
        (dict(
            TAXA="DIMENSIONS NTAX=5; TAXLABELS t1 't2 x' t3 t4 t5;",
            CHARACTERS="DIMENSIONS NCHAR=3; CHARSTATELABELS 1 c1/c1.0 c1.1, 2 c2, 3 c3;",
            NOTES="TEXT SOURCE=INLINE TAXON=(1-3) CHARACTER=1 STATE=1 TEXT= 'these taxa from north';"),
         lambda n: n.TEXT.taxons == ['t1', "t2 x", 't3'] and n.TEXT.characters == ['c1'] and n.TEXT.states == {'c1': ['c1.1']}),
        (dict(
            TREES="TREE 'the tree' = (,):2;",
            CHARACTERS="""
DIMENSIONS NEWTAXA NTAX=5 NCHAR=3;
TAXLABELS t1 't2 x' t3 t4 t5;
CHARSTATELABELS 1 c1/c1.0 c1.1, 2 c2, 3 c3;""",
            NOTES="TEXT SOURCE=INLINE TAXON=(1 3) TREE=1 TEXT= 'these taxa from the far north';"),
         lambda n: n.TEXT.taxons == ['t1', 't3'] and n.TEXT.trees == ['the tree']),
        (dict(
            CHARACTERS="DIMENSIONS NEWTAXA NTAX=5 NCHAR=3;",
            NOTES="TEXT SOURCE=INLINE TAXON=(1 3) TEXT= 'these taxa from the far north';"),
         lambda n: n.TEXT.taxons == ['1', '3']),
    ]
)
def test_Notes_(nexus, spec, expect):
    nex = nexus(**spec)
    assert expect(nex.NOTES)


def test_Notes_from_data(nexus):
    nex = nexus(TAXA="DIMENSIONS NTAX=5; TAXLABELS A B C D E;")
    nex.append_block(Notes.from_data([dict(taxons=['A', 'D'], text='Some stuff')], nexus=nex))
    assert "TEXT TAXON=(1 4)" in str(nex) and "TEXT='Some stuff'" in str(nex)

    nex = nexus(DATA="DIMENSIONS NCHAR=3; CHARLABELS X Y Z; MATRIX t1 101 t2 010 t3 001;")
    nex.append_block(Notes.from_data([dict(characters=['Y', 'Z'], text='Some stuff')], nexus=nex))
    assert "TEXT CHARACTER=(2 3)" in str(nex) and "TEXT='Some stuff'" in str(nex)

    nex = nexus(TREES="TREE x = (a,b); TREE y = (a,b); TREE z = (a,b);")
    nex.append_block(Notes.from_data([dict(trees=['x', 'z'], text='Some stuff')], nexus=nex))
    assert "TEXT TREE=(1 3)" in str(nex) and "TEXT='Some stuff'" in str(nex)
