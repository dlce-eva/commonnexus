import pytest

from commonnexus import Nexus
from commonnexus.blocks.trees import Trees


def test_Trees():
    nex = Nexus("""#nexus
BEGIN TAXA;
    TAXLABELS Scarabaeus Drosophila Aranaeus;
END;
BEGIN Trees;
    TRANSLATE beetle Scarabaeus, fly Drosophila, spider Aranaeus;
    TREE tree1 = ((beetle,fly),spider);
    TREE tree2 = ((1,2),3);
    TREE tree3 = ((Scarabaeus,Drosophila),Aranaeus);
END;
""")
    assert nex.TREES.TRANSLATE.mapping['spider'] == 'Aranaeus'
    assert nex.TREES.TREE.newick.newick == '((beetle,fly),spider)'
    node = nex.TREES.translate(nex.TREES.TREE)
    assert node.newick == '((Scarabaeus,Drosophila),Aranaeus)'

    tree = nex.TREES.commands['TREE'][1]
    assert nex.TREES.translate(tree).newick == '((Scarabaeus,Drosophila),Aranaeus)'


def test_Trees_complex_newick():
    nex = Nexus("""#nexus
BEGIN TAXA;
    TAXLABELS A B 'And C';
END;
BEGIN Trees;
    TREE tree = (A[commentA]:1.1,B[commentB]:2.2)'And C'[comment C]:3.3;
END;
""")
    nodes = {n.name: n for n in nex.TREES.TREE.newick.walk()}
    assert nodes['A'].comment == 'commentA' and nodes['A'].length == pytest.approx(1.1)
    assert nodes['B'].comment == 'commentB' and nodes['B'].length == pytest.approx(2.2)
    assert nodes["'And C'"].comment == 'comment C' and nodes["'And C'"].length == pytest.approx(3.3)


def test_Trees_from_data():
    nex = Nexus("""#nexus
BEGIN TAXA;
    TAXLABELS A B C;
END;""")
    nex.append_block(Trees.from_data(('the tree', '(X,Y)Z', False), A='X', B='Y', C='Z'))
    assert str(nex) == """#NEXUS
BEGIN TAXA;
    TAXLABELS A B C;
END;
BEGIN TREES;
TRANSLATE A X,
B Y,
C Z;
TREE 'the tree' = [&U] (A,B)C;
END;"""
