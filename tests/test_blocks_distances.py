import decimal

import pytest

from commonnexus import Nexus


@pytest.mark.parametrize(
    'matrix',
    [
        """FORMAT TRIANGLE=UPPER;
            MATRIX
                taxon_1 0.0  1.0  2.0  4.0  7.0
                taxon_2      0.0  3.0  5.0  8.0
                taxon_3           0.0  6.0  9.0
                taxon_4                0.0 10.0
                taxon_5                     0.0;""",
        """FORMAT NODIAGONAL;
            MATRIX
                taxon_1
                taxon_2  1.0
                taxon_3  2.0  3.0
                taxon_4  4.0  5.0  6.0
                taxon_5  7.0  8.0  9.0 10.0;""",
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
    nex = Nexus("""#NEXUS
                BEGIN TAXA;
                    DIMENSIONS NTAX=5;
                    TAXLABELS taxon_1 taxon_2 taxon_3 taxon_4 taxon_5;
                END;
                BEGIN DISTANCES;
                {}
                END;
    """.format(matrix))
    dist = nex.DISTANCES
    assert dist.get_matrix()['taxon_4'] == dict(
        taxon_1=decimal.Decimal('4.0'),
        taxon_2=decimal.Decimal('5.0'),
        taxon_3=decimal.Decimal('6.0'),
        taxon_4=decimal.Decimal('0.0'),
        taxon_5=decimal.Decimal('10.0'),
    )
