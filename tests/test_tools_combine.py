import pytest

from commonnexus.tools.combine import combine


@pytest.fixture
def nex1(nexus):
    return nexus(DATA="""
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="12" gap=-;
            Matrix
            Harry              1
            Simon              2
            ;""")


@pytest.fixture
def nex2(nexus):
    return nexus(DATA="""
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="34" gap=-;
            Matrix
            Harry              3
            Simon              4
            ;""")


@pytest.fixture
def nex3(nexus):
    return nexus(DATA="""
            Dimensions ntax=3 nchar=2;
            Format datatype=standard symbols="3459" gap=-;
            Matrix
            Betty              39
            Boris              49
            Simon              59
            ;""")


@pytest.fixture
def nex4(nexus):
    return nexus(DATA="""
            Dimensions ntax=3 nchar=1;
            Format datatype=DNA symbols="atcg" gap=-;
            Matrix
            Betty              t
            Boris              t
            Simon              t
            ;""")


def test_combine_simple(nex1, nex2):
    matrix = combine(nex1, nex2).characters.get_matrix()
    assert matrix['Harry'] == {'1.1': '1', '2.1': '3'}
    assert matrix['Simon'] == {'1.1': '2', '2.1': '4'}


def test_combine_error(nex1, nex4):
    with pytest.raises(ValueError):
        combine(nex1, nex4)


def test_combine_missing(nex1, nex3, nexus):
    matrix = combine(nex1, nexus(), nex3).characters.get_matrix()
    assert matrix['Harry'] == {'1.1': '1', '3.1': None, '3.2': None}
    assert matrix['Simon'] == {'1.1': '2', '3.1': '5', '3.2': '9'}
    assert matrix['Betty'] == {'1.1': None, '3.1': '3', '3.2': '9'}
    assert matrix['Boris'] == {'1.1': None, '3.1': '4', '3.2': '9'}


def test_combine_iterated(nex1):
    res = combine(combine(nex1))
    assert len(res.taxa) == 2  # Taxa are merged.
    assert '1.1.1' in res.characters.get_matrix()['Simon']  # Charlabels are prefixed.


def test_combine_with_character_labels(nexus):
    n1 = nexus(
        TAXA="DIMENSIONS NTAX=3; TAXLABELS Tax1 Tax2 Tax3;",
        DATA="""
            DIMENSIONS NCHAR=3;
            FORMAT DATATYPE=STANDARD MISSING=0 GAP=-  SYMBOLS="123";
            CHARSTATELABELS
                1 char1,
                2 char2,
                3 char3
        ;
        MATRIX
        1         123
        2         123
        3         123
        ;
        """)
    n2 = nexus(DATA="""
            DIMENSIONS NTAX=3 NCHAR=3;
            FORMAT DATATYPE=STANDARD MISSING=0 GAP=-  SYMBOLS="456";
            CHARSTATELABELS
                1 char1,
                2 char2,
                3 char3
        ;
        MATRIX
        Tax1         456
        Tax2         456
        Tax3         456
        ;
        """)
    newnex = combine(n1, n2)
    assert len(newnex.taxa) == 3, "Taxa not merged using taxlabels"
    row = list(newnex.characters.get_matrix().values())[0]
    assert len(row) == 6, "Characters not aggregated"
    assert '1.char1' in row and ('2.char1' in row), "charlabels not prefixed"
    assert '1.char2' in row
    assert row == {
        '1.char1': '1',
        '1.char2': '2',
        '1.char3': '3',
        '2.char1': '4',
        '2.char2': '5',
        '2.char3': '6'}


def test_combine_trees(nexus):
    nex1 = nexus(TREES="translate 1 a, 2 b, 3 c; tree 1 = (1,2,3);")
    nex2 = nexus(TREES="""
            tree 2 = (b,a[comment],c);
            tree 3 = (b,c,a);""")

    newnex = combine(nex1, nex2)
    assert len(newnex.TREES.trees) == 3, "not all trees aggregated"
    assert newnex.taxa == ['a', 'b', 'c'], "trees not properly translated"
    assert newnex.TREES.trees[0].name == '1.1', "tree name not prefixed"
    assert '[comment]' in newnex.TREES.trees[1].newick.newick, "comment in newick lost"
