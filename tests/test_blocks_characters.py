import pytest

from commonnexus import Nexus
from commonnexus.blocks.characters import GAP


def test_Chars_1():
    nex = Nexus("""#nexus
BEGIN TAXA;
    DIMENSIONS  NTAX=3;
    TAXLABELS A B C;
END;
BEGIN CHARACTERS;
    DIMENSIONS  NCHAR=3;
    FORMAT MISSING=? GAP=- SYMBOLS="AB C" EQUATE="x=(AB)y={BC} z=C" NOLABELS;
    CHARSTATELABELS 1  CHAR_A/astate,  2  CHAR_B,  3  CHAR_C/_ bstate cstate;
    MATRIX xBC ABC A(A B)C;
END;""")
    assert nex.CHARACTERS.DIMENSIONS.nchar == 3
    assert nex.CHARACTERS.FORMAT.gap == '-'
    assert nex.CHARACTERS.FORMAT.symbols == list('ABC')
    assert nex.CHARACTERS.FORMAT.equate == dict(x=('A', 'B'), y={'B', 'C'}, z='C')
    assert nex.CHARACTERS.CHARSTATELABELS.characters[-1].name == 'CHAR_C'
    assert nex.CHARACTERS.CHARSTATELABELS.characters[-1].states == ['_', 'bstate', 'cstate']
    matrix = nex.CHARACTERS.get_matrix(labeled_states=True)
    assert matrix['A']['CHAR_A'] == ('astate', 'B')
    assert matrix['C']['CHAR_C'] == 'cstate'
    assert matrix['C']['CHAR_B'] == ('A', 'B')


@pytest.mark.parametrize(
    'taxa,characters,expect',
    [
        (
            None,
            """DIMENSIONS NCHAR=3; MATRIX t1 001 t2 101 t3 100;""",
            lambda m: list(m['t1'].values()) == ['0', '0', '1'],
        ),
        (  # With interleaved matrices newlines are important:
            "DIMENSIONS  NTAX=3; TAXLABELS A B C;",
            """DIMENSIONS  NCHAR=3;
FORMAT INTERLEAVE NOLABELS SYMBOLS="ABC";
CHARSTATELABELS 1  CHAR_A,  2  CHAR_B,  3  CHAR_C;
MATRIX
                   AB
                   AB
                   AB
                   C
                   C
                   C
;""",
            lambda m: list(m['A'].values()) == ['A', 'B', 'C'] and m['C']['CHAR_C'] == 'C',
        ),
        (
            None,
            'DIMENSIONS NCHAR=9; FORMAT labels=left SYMBOLS="-+x"; MATRIX t1 (-+){-+}+---+-- t2 +x-++--+x t3 -++++--+x;',
            lambda m: list(m['t1'].values()) == [('-', '+'), {'-', '+'}, '+', '-', '-', '-', '+', '-', '-'],
        ),
        (  # Test MISSING, GAP and MATCHCHAR
            None,
            'DIMENSIONS NCHAR=3; FORMAT MISSING=u GAP=_ MATCHCHAR=.; MATRIX t1 U_0 t2 11. t3 ...;',
            lambda m: [list(r.values()) for r in m.values()] == [[None, GAP, '0'], ['1', '1', '0'], [None, GAP, '0']],
        ),
        (  # Test RESPECTCASE
            None,
            'DIMENSIONS NCHAR=3; FORMAT RESPECTCASE SYMBOLS="ABC" MISSING=c GAP=a MATCHCHAR=b; MATRIX t1 cCa t2 AbB;',
            lambda m: [list(r.values()) for r in m.values()] == [[None, 'C', GAP], ['A', 'C', 'B']],
        ),
        (
            None,
            'DIMENSIONS NCHAR=3; FORMAT DATATYPE=DNA; MATRIX t1 RTA;',
            lambda m: list(m['t1'].values()) == [{'A', 'G'}, 'T', 'A'],
        ),
        (  # From the docuentation of MATCHCHAR:
            None,
            'DIMENSIONS NCHAR = 7; FORMAT DATATYPE=DNA MATCHCHAR = .; MATRIX taxon_1 GACCTTA taxon_2 ...T..C taxon_3 ..T.C..;',
            lambda m: ''.join(m['taxon_2'].values()) == 'GACTTTC',
        ),
    ]
)
def test_Characters_get_matrix(characters, taxa, expect):
    nex = Nexus("""#NEXUS
{}
BEGIN CHARACTERS;
{}
END;""".format('BEGIN TAXA;\n{}\nEND;'.format(taxa) if taxa else '', characters))
    matrix = nex.CHARACTERS.get_matrix()
    #print(matrix)
    assert expect(matrix)