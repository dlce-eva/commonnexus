import pytest


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
