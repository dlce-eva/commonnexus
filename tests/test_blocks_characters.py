import warnings

import pytest

from commonnexus import Nexus, Config
from commonnexus.blocks.characters import GAP, Characters


def test_Eliminate(nexus):
    nex = nexus(CHARACTERS='ELIMINATE 1-3;', config=Config(ignore_unsupported=False))
    with pytest.raises(NotImplementedError):
        _ = nex.CHARACTERS.commands
    _ = nexus(CHARACTERS='ELIMINATE 1-3;').CHARACTERS.ELIMINATE


def test_Chars_1(nexus):
    nex = nexus(
        TAXA="DIMENSIONS  NTAX=3; TAXLABELS A B C;",
        CHARACTERS="""\
DIMENSIONS  NCHAR=3;
FORMAT MISSING=? GAP=- SYMBOLS="AB C" EQUATE="x=(AB)y={BC} z=C" NOLABELS;
CHARSTATELABELS 1  CHAR_A/astate,  2  CHAR_B,  3  CHAR_C/_ bstate cstate;
MATRIX xBC ABC A(A B)C;""")
    assert nex.CHARACTERS.validate()
    assert nex.CHARACTERS.DIMENSIONS.nchar == 3
    assert nex.CHARACTERS.FORMAT.gap == '-'
    assert nex.CHARACTERS.FORMAT.symbols == list('ABC')
    assert nex.CHARACTERS.FORMAT.equate == dict(X=('A', 'B'), Y={'B', 'C'}, Z='C')
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
        (
            None,
            "DIMENSIONS NCHAR=3; CHARLABELS c1 c2 c3; MATRIX t1 001 t2 101 t3 100;",
            lambda m: m['t1']['c1'] == '0',
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
        (  # No RESPECTCASE directive, characters are returned as specified in SYMBOLS.
            None,
            'DIMENSIONS NCHAR=3; FORMAT SYMBOLS="ab"; MATRIX t1 aAb t2 BbB;',
            lambda m: [list(r.values()) for r in m.values()] == [['a', 'a', 'b'], ['b', 'b', 'b']],
        ),
        (
            None,
            'DIMENSIONS NCHAR=3; FORMAT DATATYPE=DNA; MATRIX t1 RTA;',
            lambda m: list(m['t1'].values()) == [{'A', 'G'}, 'T', 'A'],
        ),
        (
            None,
            'DIMENSIONS NCHAR=3; FORMAT DATATYPE=NUCLEOTIDE; MATRIX t1 UTA;',
            lambda m: list(m['t1'].values()) == ['T', 'T', 'A'],
        ),
        (
            None,
            'DIMENSIONS NCHAR=3; FORMAT DATATYPE=PROTEIN; MATRIX t1 ABZ;',
            lambda m: list(m['t1'].values()) == ['A', {'D', 'N'}, {'E', 'Q'}],
        ),
        (  # From the documentation of MATCHCHAR:
            None,
            'DIMENSIONS NCHAR = 7; FORMAT DATATYPE=DNA MATCHCHAR = .; MATRIX taxon_1 GACCTTA taxon_2 ...T..C taxon_3 ..T.C..;',
            lambda m: ''.join(m['taxon_2'].values()) == 'GACTTTC',
        ),
        (
            None,
            'dimensions nchar=3; matrix *T 101 OtherT 010;',
            lambda m: '*T' in m,
        ),
        (  # comma-separated polymorphic states.
            None,
           'dimensions nchar=3; matrix t1 (1,0)01 t2 {0,1}10;',
            lambda m: m['t1']['1'] == ('1', '0') and m['t2']['1'] == {'1', '0'},
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
    assert expect(matrix)


def test_NoDefaultMatchChar():
    nex = Nexus("""#nexus
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT SYMBOLS=".+";
MATRIX t1 ..+ t2 ++. t3 +++;
END;""", no_default_matchchar=True)
    matrix = nex.characters.get_matrix()
    assert matrix['t1'] == {'1': '.', '2': '.', '3': '+'}


def test_Characters_Statelabels():
    nex = Nexus("""#nexus
BEGIN CHARACTERS;
DIMENSIONS NEWTAXA NTAX=3 NCHAR=3;
TAXLABELS t1 t2 t3;
STATELABELS 1 absent present, 2 x y;
MATRIX t1 100 t2 010 t3 001;
END;""")
    matrix = nex.CHARACTERS.get_matrix(labeled_states=True)
    print(matrix)
    assert matrix['t1']['1'] == 'present'
    assert matrix['t1']['2'] == 'x'


def test_Characters_from_data_invalid():
    with pytest.raises(ValueError):  # The MISSING marker is used as value in the matrix.
        _ = Characters.from_data({'t1': {'c1': '?'}})


def test_Characters_from_data(nexus):
    nex = nexus(
        TAXA="DIMENSIONS NTAX=3; TAXLABELS t1 t2 t3;",
        CHARACTERS="""
DIMENSIONS NCHAR=3;
FORMAT TRANSPOSE NOLABELS;
MATRIX {01}00 (01)10 001;""")
    assert nex.characters.is_binary()
    matrix = nex.CHARACTERS.get_matrix()
    nex.replace_block(nex.CHARACTERS, Characters.from_data(matrix))
    assert str(nex) == """#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX=3; TAXLABELS t1 t2 t3;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=3;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
MATRIX 
t1 {01}(01)0
t2 010
t3 001
;
END;"""
    assert nex.characters.get_matrix() == matrix

    nex = Nexus('#nexus')
    matrix = {'t1': {'1': '0', '2': '1'}, 't2': {'1': '1', '2': '0'}}
    nex.append_block(Characters.from_data(matrix, taxlabels=True))
    assert str(nex) == """#NEXUS
BEGIN CHARACTERS;
DIMENSIONS NEWTAXA NTAX=2 NCHAR=2;
FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
TAXLABELS t1 t2;
MATRIX 
t1 01
t2 10
;
END;"""
    assert nex.characters.get_matrix() == matrix

    nex = Nexus('#nexus')
    matrix = {'t1': {'1': 'a', '2': 'B'}, 't2': {'1': 'A', '2': 'b'}}
    nex.append_block(Characters.from_data(matrix, taxlabels=True))
    assert str(nex) == """#NEXUS
BEGIN CHARACTERS;
DIMENSIONS NEWTAXA NTAX=2 NCHAR=2;
FORMAT DATATYPE=STANDARD RESPECTCASE MISSING=? GAP=- SYMBOLS="ABab";
TAXLABELS t1 t2;
MATRIX 
t1 aB
t2 Ab
;
END;"""
    assert nex.characters.get_matrix() == matrix


@pytest.mark.parametrize(
    'commands',
    [
        """
DIMENSIONS NEWTAXA NTAX=3 NCHAR=3;
TAXLABELS t1 t2 t3;
FORMAT TOKENS;
MATRIX t1 1 0 0 t2 0 1 0 t3 0 0 1; 
        """,
        """
DIMENSIONS NEWTAXA NTAX=3 NCHAR=3;
TAXLABELS t1 t2 t3;
FORMAT DATATYPE=CONTINUOUS;
MATRIX t1 100 t2 010 t3 001; 
        """,
        """
DIMENSIONS NEWTAXA NTAX=3 NCHAR=3;
TAXLABELS t1 t2 t3;
FORMAT STATESFORMAT=COUNT;
MATRIX t1 100 t2 010 t3 001; 
        """,
        """
DIMENSIONS NEWTAXA NTAX=3 NCHAR=3;
TAXLABELS t1 t2 t3;
FORMAT ITEMS=SAMPLESIZE;
MATRIX t1 100 t2 010 t3 001; 
        """
    ]
)
def test_Characters_not_implemented(commands, nexus):
    nex = nexus(CHARACTERS=commands, config=Config(ignore_unsupported=False))
    with pytest.raises(NotImplementedError):
        _ = nex.CHARACTERS.commands


def test_Characters_validate(nexus):
    nex = nexus(CHARACTERS="DIMENSIONS NCHAR=1; TAXLABELS t1; MATRIX t1 1;")
    with pytest.raises(ValueError):
        nex.CHARACTERS.validate()


def test_Data_with_Options(nexus):
    nex = nexus(DATA="DIMENSIONS NCHAR=1; OPTIONS GAPMODE=missing; MATRIX t1 1;")
    assert nex.characters.OPTIONS.gapmode == 'missing'


def test_Data_with_duplicate_charlabels(nexus):
    with warnings.catch_warnings(record=True) as w:
        nex = nexus(DATA="DIMENSIONS NCHAR=2; CHARLABELS x x; MATRIX t1 1 1;")
        nex.characters.get_matrix()
        assert len(w) == 1, 'Expected 1 warning, got %r' % w


def test_Data_with_mixed_charlabels(nexus):
    nex = nexus(DATA="DIMENSIONS NCHAR=2; CHARSTATELABELS 1 x, 2 ; MATRIX t1 1 1;")
    m = nex.characters.get_matrix()
    assert '2' in m['t1'], 'unspecified character label'
