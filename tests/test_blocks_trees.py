from commonnexus import Nexus


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
    assert nex.TREES.TREE.newick_string == '((beetle,fly),spider)'
    node = nex.TREES.translate(nex.TREES.TREE)
    assert node.newick == '((Scarabaeus,Drosophila),Aranaeus)'

    tree = nex.TREES.commands['TREE'][1]
    assert tree.newick_string == '((1,2),3)'
    assert nex.TREES.translate(tree).newick == '((Scarabaeus,Drosophila),Aranaeus)'
