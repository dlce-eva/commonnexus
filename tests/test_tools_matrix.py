import pytest

from commonnexus.tools.matrix import CharacterMatrix


def test_multistatise(nexus):
    nex = nexus(DATA="""
        Dimensions ntax=4 nchar=4;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              0000
        Simon              0100
        Betty              0010
        Louise             1001
        ;""")
    res = CharacterMatrix.multistatised(nex.DATA.get_matrix())
    res = {k: v['1'] for k, v in res.items()}
    assert res == dict(Harry=None, Simon='B', Betty='C', Louise=('A', 'D'))


def test_multistatise_with_all_zero_taxa(nexus):
    """Include taxa that have no entries"""
    nex = nexus(DATA="""
        DIMENSIONS  NTAX=15 NCHAR=7;
        FORMAT DATATYPE=STANDARD MISSING=? GAP=- INTERLEAVE=YES;
    MATRIX

    Gertrude                0000001
    Debbie                  0001000
    Zarathrustra            0000000
    Christie                0010000
    Benny                   0100000
    Bertha                  0100000
    Craig                   0010000
    Fannie-May              0000010
    Charles                 0010000
    Annik                   1000000
    Frank                   0000010
    Amber                   1000000
    Andreea                 1000000
    Edward                  0000100
    Donald                  0001000
    ;""")
    m = CharacterMatrix(nex.DATA.get_matrix())
    assert 'AAAAAAB' in m.to_fasta()
    assert CharacterMatrix.from_fasta(m.to_fasta())['Amber']['1'] == 'B'
    msnex = CharacterMatrix.multistatised(m)

    for taxon, sites in msnex.items():
        if taxon[0] == 'Z':
            continue  # will check later

        # first letter of taxa name is the expected character state
        assert taxon[0] == sites['1'], "%s should be %s not %s" % (taxon, taxon[0], sites[0])
    # deal with completely missing taxa
    assert 'Zarathrustra' in msnex
    assert msnex['Zarathrustra']['1'] is None
    assert '> Donald' in msnex.to_fasta()
    assert 'Donald    ' in msnex.to_phylip()


def test_CharacterMatrix(nexus):
    nex = nexus(DATA="""
DIMENSIONS NCHAR=5;
FORMAT DATATYPE=STANDARD MISSING=x GAP=y;
MATRIX
t1 1y01(01)
t2 10{01}yx;
""")
    matrix = CharacterMatrix(nex.characters.get_matrix())
    assert matrix.has_missing
    assert matrix.has_gaps
    assert matrix.has_polymorphic
    assert matrix.has_uncertain
    m = CharacterMatrix.from_characters(matrix, drop_uncertain=True, drop_polymorphic=True)
    assert len(m.characters) == 3
    assert m.to_fasta()
    m = CharacterMatrix.from_characters(matrix, drop_statesets=[{'1'}])
    assert len(m.characters) == 4

    with pytest.raises(Exception):
        matrix.to_fasta()

    with pytest.raises(Exception):
        matrix.to_phylip()


def test_CharacterMatrix_from_fasta():
    with pytest.raises(AssertionError):
        CharacterMatrix.from_fasta('> t1\nABB\n> t2\nAB')


def test_CharMatrix_binarise(nexus):
    matrix = CharacterMatrix.binarised(nexus(
        TAXA="DIMENSIONS NTAX=3; TAXLABELS Maori Dutch Latin;",
        CHARACTERS="""
    Dimensions ntax=3 nchar=3;
    Format datatype=standard symbols="1234567" gap=- transpose nolabels equate="x=(12)";
    Charstatelabels
        1 char1, 2 char2, 3 char3;
    Matrix x23 4-5 67? ;""").characters.get_matrix())
    assert matrix['Maori'] == {
        'char1_1': '1', 'char1_2': '0', 'char1_3': '0',
        'char2_1': '1', 'char2_2': '0',
        'char3_1': '1', 'char3_2': '0',
    }
