"""Regression Tests"""
import warnings

import pytest

from commonnexus import Nexus
from commonnexus.blocks import Characters


@pytest.fixture
def regression(fixture_dir):
    return fixture_dir / 'regression'


def test_UnquotedSymbols(regression):
    with warnings.catch_warnings(record=True) as w:
        nex = Nexus.from_file(regression / 'unquoted_symbols.nex')
        assert nex.DATA.FORMAT.symbols == ['0', '1']
        assert len(w) == 72, 'Expected 72 warnings, got %r' % w


def test_Morphobank(morphobank, regression):
    nex = Nexus.from_file(morphobank)
    assert len(nex.NOTES.texts) == 30
    notes = nex.NOTES.get_texts(character='Lateral ethmoid-lacrimal articulation, orientation')
    assert len(notes) == 1
    assert notes[0].text == 'Waldman, 1986'

    matrix = nex.characters.get_matrix(labeled_states=True)
    assert matrix['Sargocentron vexillarium']['Vomer, shape of tooth patch'] == 'Trapezoidal to ovate'

    m = nex.characters.get_matrix()
    nex = Nexus.from_blocks(
        Characters.from_data(m, statelabels=nex.characters.get_charstatelabels()[1]))
    assert nex.characters.get_matrix(labeled_states=True) == matrix

    nex = Nexus.from_file(regression / 'mbank_X29171_3-10-2023_150.nex')
    m = nex.characters.get_matrix(labeled_states=True)
    assert m['Proterosuchus fergusi']['Skull and lower jaws, interdental plates'] == \
           ('absent', 'present, small and well-spaced from each other')


def test_treebase(regression):
    nex = Nexus.from_file(regression / 'treebase-matrix-123.nex')
    assert len(nex.characters.get_matrix()) == 64
    nex = Nexus.from_file(regression / 'treebase-tree-1234.nex')
    assert set(nex.taxa ) == {n.name for n in nex.TREES.TREE.newick.walk() if n.is_leaf}


def test_WhitespaceInMatrix_regression(regression):
    """Regression: Test that leading whitespace in a data matrix is parsed ok"""
    nex = Nexus.from_file(regression / 'white_space_in_matrix.nex')
    matrix = nex.DATA.get_matrix()
    assert len(list(matrix.values())[0]) == 2
    assert list(matrix['Harry'].values()) == ['0', '0']
    assert list(matrix['Simon'].values()) == ['0', '1']
    assert list(matrix['Betty'].values()) == ['1', '0']
    assert list(matrix['Louise'].values()) == ['1', '1']


def test_RandomAPETrees_regression(regression):
    """Regression: Test that we can parse randomly generated APE/R trees"""
    nex = Nexus.from_file(regression / 'ape_random.trees')
    assert len(nex.TREES.trees) == 2
    assert nex.TREES.TREE.name == 'UNTITLED'


def test_BadCharsInTaxaName_trees(regression):
    bad_chars = Nexus.from_file(regression / 'bad_chars_in_taxaname.trees')
    assert bad_chars.TREES, 'No TREES block found'
    assert len(bad_chars.TREES.trees) == 1, 'Invalid number of TREEs found'

    # did we get the translation parsed properly.
    translated = bad_chars.TREES.translate(bad_chars.TREES.TREE)
    assert 'PALAUNGWA_De.Ang' in {n.name for n in translated.walk()}
    expected = '(MANGIC_Bugan,MANGIC_Paliu,MANGIC_Mang,PALAUNGWA_Danaw,PAL'
    assert expected in translated.newick


def test_DetranslateWithDash_trees(regression):
    nex = Nexus.from_file(regression / 'detranslate-with-dash.trees', hyphenminus_is_text=True)
    translated = nex.TREES.translate(nex.TREES.TREE)
    assert "(one,two,three,four-1,four_2)" in translated.newick


def test_BranchLengthsInIntegers_trees(regression):
    int_length = Nexus.from_file(regression / 'branchlengths-in-integers.trees')
    translated = int_length.TREES.translate(int_length.TREES.TREE)
    assert '(one:0.1,two:0.2,three:1,four:3,five:0.3)' in translated.newick


def test_Mesquite_taxa_block(regression):
    """Regression: Test that we can parse MESQUITE taxa blocks"""
    mesquite = Nexus.from_file(regression / 'mesquite_taxa_block.nex')
    assert all(taxon in mesquite.TAXA.TAXLABELS.labels.values() for taxon in ['A', 'B', 'C'])
    assert 'Untitled_Block_of_Taxa'.upper() == mesquite.TAXA.title
    assert 'Untitled_Block_of_Taxa'.upper() == mesquite.TAXA.links['TAXA']


def test_TreeHandler_Regression_Mesquite_attributes(regression):
    mesquite_branches = Nexus.from_file(regression / 'mesquite_formatted_branches.trees')
    assert mesquite_branches.TREES.title == 'Trees from "temp.trees"'.upper()
    assert mesquite_branches.TREES.links['TAXA'] == "Untitled_Block_of_Taxa".upper()
    assert mesquite_branches.TREES.TREE
    translated = mesquite_branches.TREES.translate(mesquite_branches.TREES.TREE)
    assert {'A', 'B', 'C'} == {n.name for n in translated.walk() if n.name}


def test_TaxaHandler_OneLine_block_find(regression):
    """Regression: Test that we can read taxalabels delimited by spaces not new lines."""
    taxlabels = Nexus.from_file(regression / 'taxlabels.nex')
    assert taxlabels.TAXA
    assert taxlabels.CHARACTERS
    matrix = taxlabels.CHARACTERS.get_matrix()
    for taxon in ['A', 'B', 'C']:
        assert taxon in matrix
        assert taxon in taxlabels.TAXA.TAXLABELS.labels.values()

    assert list(matrix["A"].values()) == ["1", "1", "1"]
    assert list(matrix["B"].values()) == ["0", "1", "1"]
    assert list(matrix["C"].values()) == ["0", "0", "1"]


def test_GlottologTree_block_find(regression):
    """Regression: Test that we can read glottolog tree format."""
    glottolog = Nexus.from_file(regression / 'glottolog.trees')
    assert glottolog.TAXA
    assert glottolog.TREES
    for i in range(2, 6):
        taxon = 'abun125%d' % i
        assert taxon in glottolog.TAXA.TAXLABELS.labels.values()

    assert len(glottolog.TAXA.TAXLABELS.labels) == 4
    assert glottolog.TREES.TREE


def test_TreeHandler_MrBayes(regression):
    """
    Test reading of treefile generated by a 2003-era MrBayes which, for some reason, have
    a tab between "tree\t<name>=(...)"
    """
    nex = Nexus.from_file(regression / 'mrbayes.trees')
    assert nex.TREES.TREE.name == 'tree.2500000.34524.300436'


def test_DataHandler_trailing_comma():
    """Trailing comma in charstatelabels creates an empty character at N+1"""
    nex = Nexus("""#NEXUS
        BEGIN DATA;
            DIMENSIONS NTAX=3 NCHAR=1;
            FORMAT MISSING=? GAP=- SYMBOLS="01";
            CHARSTATELABELS
            1 ALL,
        ;

        MATRIX
        A        1
        B        0
        C        0
        ;
        END;
        """)
    with warnings.catch_warnings(record=True) as w:
        assert nex.DATA.CHARSTATELABELS
        assert len(w) == 1, 'Expected 1 warning, got %r' % w
        assert issubclass(w[0].category, UserWarning)
        assert len(nex.DATA.CHARSTATELABELS.characters) == 1

    
def test_TreeHandler_Taxon_with_asterisk(regression):
    """
    Test reading of treefile that contains a taxon with an asterisk in it.
    """
    nex = Nexus.from_file(regression / 'tree_with_asterisk_in_taxa.trees', asterisk_is_text=True)
    assert nex.TREES.TREE
    assert len(nex.TAXA.TAXLABELS.labels) == 38
    assert "*R35" in nex.TAXA.TAXLABELS.labels.values()
    translated = nex.TREES.translate(nex.TREES.TREE)
    assert "*R35" in {n.name for n in translated.walk()}


def test_TreeHandler_TranslateBlockMismatch(regression):
    """
    Test that a warning is generated when a tree has un-translatable nodes.
    """
    nex = Nexus.from_file(regression / 'tree_translate_mismatch.trees')
    with pytest.warns(UserWarning):
        _ = nex.TREES.translate(nex.TREES.TREE)


def test_TreeHandler_TranslateBlockWithComments(regression):
    """
    Test reading of treefile that contains no translate block, so taxa are 
    identified from parsing the first tree. If the tree contains comments of the
    form "x(y)" then these used to get parsed incorrectly (as extra taxa).
    """
    nex = Nexus.from_file(regression / 'tree_default_translate_with_comments.trees')
    assert nex.TREES.TREE
    taxa = set(nex.TAXA.TAXLABELS.labels.values())
    for node in nex.TREES.TREE.newick.walk():
        if node.name:
            assert node.name in taxa


def test_TreeHandler_BeastTranslate(regression):
    """
    Test handling of BEAST Translate Block
    """
    nex = Nexus.from_file(regression / 'detranslate-beast.trees')
    assert nex.TREES.TREE
    assert len(nex.TREES.TRANSLATE.mapping) == 19
    translated = nex.TREES.translate(nex.TREES.TREE)
    leafs = {n.name for n in translated.walk() if n.is_leaf}
    assert len(leafs) == 19
    assert "B" in leafs


def test_TreeHandler_BeastTranslate_2(regression):
    """
    Test handling of BEAST Translate Block in Phlorest.
    """
    nex = Nexus.from_file(regression / 'detranslate-beast-2.trees')
    assert nex.TREES.TREE
    assert len(nex.TREES.TRANSLATE.mapping) == 10
    translated = nex.TREES.translate(nex.TREES.TREE)
    leafs = {n.name for n in translated.walk() if n.is_leaf}
    assert len(leafs) == 10
    assert "B" in leafs


def test_TreeHandler_BeastTranslate_3(regression):
    """
    Test handling of BEAST Translate Block in Phlorest. Again.
    """
    nex = Nexus.from_file(regression / 'tree_detranslate_chang.trees')
    assert nex.TREES.TREE
    translated = nex.TREES.translate(nex.TREES.TREE)
    leafs = {n.name for n in translated.walk() if n.is_leaf}
    assert len(leafs) == 52
    assert "Old_Church_Slavic" in leafs


def test_Edictor(regression):
    """
    Test handling of EDICTOR Nexus files
    """
    nex = Nexus.from_file(regression / 'edictor.nex')
    assert nex.DATA
    assert nex.CHARACTERS
    
    assert nex.DATA.DIMENSIONS.nchar == 4
    assert nex.DATA.DIMENSIONS.ntax == 3

    #assert nex.blocks['characters'].nchar == 4
    #assert nex.blocks['characters'].ntaxa == 0
    #assert repr(nex.blocks['characters']), 'repr of characters block failed'
    
    #assert len(nex.data.charlabels) == 4
    #assert nex.data.nchar == 4
    
    #assert nex.data.charlabels == nex.characters.charlabels
