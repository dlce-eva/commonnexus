import pytest

from commonnexus import Nexus
from commonnexus.blocks.trees import Trees


def test_Trees(nexus):
    nex = nexus(
        TAXA="TAXLABELS Scarabaeus Drosophila Aranaeus;",
        TREES="""\
    TRANSLATE beetle Scarabaeus, fly Drosophila, spider Aranaeus;
    TREE tree1 = [&R] ((beetle,fly),spider);
    TREE tr[comment]ee-2 = ((1,2),3);
    TREE tree3 = ((Scarabaeus,Drosophila),Aranaeus);"""
    )
    assert nex.TREES.TRANSLATE.mapping['spider'] == 'Aranaeus'
    assert nex.TREES.TREE.newick.newick == '((beetle,fly),spider)'
    assert nex.TREES.TREE.rooted
    node = nex.TREES.translate(nex.TREES.TREE)
    assert node.newick == '((Scarabaeus,Drosophila),Aranaeus)'
    tree = nex.TREES.trees[1]
    assert tree.name == 'tree-2'
    assert nex.TREES.translate(tree).newick == '((Scarabaeus,Drosophila),Aranaeus)'


def test_Tree_translate_with_taxa_from_linked_block(nexus):
    nex = nexus(
        TAXA="TITLE x; TAXLABELS A B C;",
        TREES="LINK TAXA=x; TREE t = (1,2)3;"
    )
    assert nex.TREES.translate(nex.TREES.TREE).newick == '(A,B)C'


def test_Trees_complex_newick():
    s = """#nexus
BEGIN TAXA;
    TAXLABELS A B 'And C';
END;
BEGIN Trees;
    TREE tree = (A[commentA]:1.1,B[commentB]:2.2,X-1)'And C'[comment C]:3.3;
END;
"""
    nex = Nexus(s)
    nodes = {n.name: n for n in nex.TREES.TREE.newick.walk()}
    assert nodes['A'].comment == 'commentA' and nodes['A'].length == pytest.approx(1.1)
    assert nodes['B'].comment == 'commentB' and nodes['B'].length == pytest.approx(2.2)
    assert nodes["'And C'"].comment == 'comment C' and nodes["'And C'"].length == pytest.approx(3.3)

    nex = Nexus(s, validate_newick=True)
    nodes = {n.name: n for n in nex.TREES.TREE.newick.walk()}
    assert nodes['A'].comment == 'commentA' and nodes['A'].length == pytest.approx(1.1)
    assert nodes['B'].comment == 'commentB' and nodes['B'].length == pytest.approx(2.2)
    assert nodes["'And C'"].comment == 'comment C' and nodes["'And C'"].length == pytest.approx(3.3)


def test_Trees_from_data(nexus):
    nex = nexus(TAXA="TAXLABELS A B C;")
    nex.append_block(Trees.from_data(('the tree', '(X,Y)Z', False), A='X', B='Y', C='Z'))
    assert str(nex) == """#NEXUS
BEGIN TAXA;
TAXLABELS A B C;
END;
BEGIN TREES;
\tTRANSLATE A X,
B Y,
C Z;
\tTREE 'the tree' = [&U] (A,B)C;
END;"""


@pytest.mark.parametrize(
    'trees',
    [
        "INVALID;",
        "TRANSLATE; TRANSLATE;"
    ]
)
def test_Trees_validate(nexus, trees):
    with pytest.raises(ValueError):
        _ = nexus(TREES=trees).validate()
