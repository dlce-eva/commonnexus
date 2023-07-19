import decimal

import pytest

from commonnexus import Nexus
from commonnexus.blocks.distances import Distances


@pytest.mark.parametrize(
    'matrix',
    [
        """FORMAT TRIANGLE=UPpER NOlABELS;
            MATRIX
                0.0  1.0  2.0  4.0  7.0
                     0.0  3.0  5.0  8.0
                          0.0  6.0  9.0
                               0.0 10.0
                                    0.0;""",
        """FORMAT TRIANGLE=UPpER NOlABELS INTERLEAVE;
            MATRIX
                0.0  1.0  2.0
                0.0  3.0  5.0
                0.0  6.0  9.0
                0.0 10.0
                0.0
                4.0  7.0
                8.0;""",
        """FORMAT TRIANGLE=UPPER;
            MATRIX
                taxon_1 0.0  1.0  2.0  4.0  7.0
                taxon_2      0.0  3.0  5.0  8.0
                taxon_3           0.0  6.0  9.0
                taxon_4                0.0 10.0
                taxon_5                     0.0;""",
        """FORMAT NODIAGONAL NOLabels TRIANGLE=UPPER;
            MATRIX
                1.0  2.0  4.0  7.0
                     3.0  5.0  8.0
                          6.0  9.0
                              10.0;""",
        """FORMAT INTERLEAVE;
            MATRIX
                taxon_1  0.0
                taxon_2  1.0  0.0
                taxon_3  2.0  3.0  0.0
                taxon_4  4.0  5.0  6.0
                taxon_5  7.0  8.0  9.0
                taxon_4  0.0
                taxon_5 10.0  0.0;""",
        """FORMAT NOLABELS INTERLEAVE;
            MATRIX
                0.0
                1.0  0.0
                2.0  3.0  0.0
                4.0  5.0  6.0
                7.0  8.0  9.0
                0.0
                10.0  0.0;""",
        """FORMAT NOLABELS NODIAGONAL INTERLEAVE;
            MATRIX
                1.0
                2.0  3.0
                4.0  5.0  6.0
                7.0  8.0  9.0
                10.0;""",
        """MATRIX
                taxon_1  0.0
                taxon_2  1.0  0.0
                taxon_3  2.0  3.0  0.0
                taxon_4  4.0  5.0  6.0  0.0
                taxon_5  7.0  8.0  9.0 10.0  0.0;""",
        """FORMAT NODIAGONAL;
            MATRIX
                taxon_1
                taxon_2  1.0
                taxon_3  2.0  3.0
                taxon_4  4.0  5.0  6.0
                taxon_5  7.0  8.0  9.0 10.0;""",
        """FORMAT NODIAGONAL NOLABELS;
            MATRIX
                1.0
                2.0  3.0
                4.0  5.0  6.0
                7.0  8.0  9.0 10.0;""",
        """FORMAT NOdiagonal TRIANGLE=BOTH;
            MATRIX
                taxon_1    1.0  2.0  4.0  7.0
                taxon_2  1.0    3.0  5.0  8.0
                taxon_3  2.0  3.0    6.0  9.0
                taxon_4  4.0  5.0  6.0   10.0
                taxon_5  7.0  8.0  9.0 10.0;"""
        """FORMAT TRIANGLE=BOTH;
            MATRIX
                taxon_1  0    1.0  2.0  4.0  7.0
                taxon_2  1.0  0    3.0  5.0  8.0
                taxon_3  2.0  3.0  0    6.0  9.0
                taxon_4  4.0  5.0  6.0  0   10.0
                taxon_5  7.0  8.0  9.0 10.0  0;"""
    ]
)
def test_Distances_get_matrix(matrix):
    for fmt in [
        """\
BEGIN TAXA;
    DIMENSIONS NTAX=5;
    TAXLABELS taxon_1 taxon_2 taxon_3 taxon_4 taxon_5;
END;
BEGIN DISTANCES;
    {}
END;""",
        """\
BEGIN DISTANCES;
    DIMENSIONS NEWTAXA NTAX=5;
    TAXLABELS taxon_1 taxon_2 taxon_3 taxon_4 taxon_5;
    {}
END;"""]:
        dist = Nexus("#NEXUS\n{}".format(fmt.format(matrix))).DISTANCES
        m = dist.get_matrix()
        assert m['taxon_4'] == dict(
            taxon_1=decimal.Decimal('4.0'),
            taxon_2=decimal.Decimal('5.0'),
            taxon_3=decimal.Decimal('6.0'),
            taxon_4=decimal.Decimal('0.0'),
            taxon_5=decimal.Decimal('10.0'),
        )
        nex = Nexus()
        nex.append_block(Distances.from_data(m, nexus=nex))
        assert m == nex.DISTANCES.get_matrix()


def test_minimal():
    dist = Nexus('#nexus begin distances; matrix t1 0 t2 1 0 t3 1 2 0; end;').DISTANCES
    assert [int(e) for e in dist.get_matrix()['t1'].values()] == [0, 1, 1]


def test_missing():
    nex = Nexus('#nexus begin distances; format missing=x; matrix t1 0 t2 x 0 t3 1 2 0; end;')
    assert [None if e is None else int(e)
            for e in nex.DISTANCES.get_matrix()['t1'].values()] == [0, None, 1]


def test_incomplete(nexus):
    nex = nexus(
        TAXA="DIMENSIONS ntax=4; taxlabels A B C D;",
        DISTANCES='matrix A 0 C 1 0 D 2 1 0;')
    matrix = nex.DISTANCES.get_matrix()
    assert 'B' not in matrix
    assert matrix['D'] == dict(A=2, C=1, D=0)


def test_splitstree(fixture_dir):
    nex = Nexus.from_file(fixture_dir / 'woodmouse.nxs')
    assert nex.DISTANCES
    assert nex.DISTANCES.get_matrix()['No305']['No1208S'] == decimal.Decimal('0.018828452')


def test_Distances_from_data():
    nex = Nexus()
    nex.append_block(Distances.from_data({'t1': {'t1': 0}}, taxlabels=True))
    assert str(nex) == """#NEXUS
BEGIN DISTANCES;
DIMENSIONS NEWTAXA NTAX=1 NTAX=1;
FORMAT TRIANGLE=BOTH MISSING=?;
TAXLABELS t1;
MATRIX 
t1 0
;
END;"""

    nex = Nexus()
    nex.append_block(Distances.from_data({'t 1': {'t 1': 0}}, taxlabels=True, nexus=nex))
    assert str(nex) == """#NEXUS
BEGIN DISTANCES;
DIMENSIONS NEWTAXA NTAX=1 NTAX=1;
FORMAT TRIANGLE=BOTH MISSING=?;
TAXLABELS 't 1';
MATRIX 
't 1' 0
;
END;"""
