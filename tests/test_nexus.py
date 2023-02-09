import logging

import pytest

from commonnexus import Nexus
from commonnexus.tokenizer import TokenType


@pytest.mark.parametrize(
    'nex,expect',
    [
        (
                """#NEXUS
    BEGIN TREES;
    TREE best = (fish , (frog,
    (snake, mouse))) ;
    END;""",
                lambda n: sum(sum(1 for t in c if t.type != TokenType.WHITESPACE) for c in n) == 22),
        (
                '#NEXUS begin trees; tree ; end;',
                lambda n: len(n.blocks['TREES']) == 1),
        (
                "#NEXUS BEGIN AssuMP[co[mm]ent]TiONS; ENDblock;",
                lambda n: 'ASSUMPTIONS' in n.blocks and n.comments[0].text == 'co[mm]ent'),
        # Commands cannot contain semicolons, except as terminators, unless the semicolons are
        # contained within a comment or within a quoted token consisting of more than one text
        # character.
        (
                "#NEXUS begin block; cmd [;] stuff; end;",
                lambda n: next(n.blocks['BLOCK'][0][1].iter_payload_tokens(TokenType.WORD)).text == 'stuff'),
        (
                "#NEXUS begin block; cmd 'a;b' stuff; end;",
                lambda n: next(n.blocks['BLOCK'][0][1].iter_payload_tokens(TokenType.WORD)).text == 'stuff'),
        (
                "#NEXUS begin block; cmd '[ab]' stuff; end;",
                lambda n: not n.comments),
        # Single quotes in quoted words must be doubled:
        (
                "#NEXUS begin block; cmd 'a''b' stuff; end;",
                lambda n: "a'b" in [t.text for t in n.blocks['BLOCK'][0][1].iter_payload_tokens()]),
        (
                "#NEXUS begin block; cmd first\tline \t\n second line; end;",
                lambda n: n.BLOCK.commands['CMD'][0].lines == ['first\tline', 'second line']),
        # Leave newick payload untouched.
        (
                '#NEXUS begin trees; stuff (a[&comment]:1,b:2)c:3; end trees;',
                lambda n: str(n.TREES.commands['STUFF'][0]) == '(a[&comment]:1,b:2)c:3'),
        (
                '#NEXUS begin trees; tree t = (a[&comment]:1,b:2)c:3; end trees;',
                lambda n: [nn.name for nn in n.TREES.TREE.newick_node.walk() if nn.is_leaf] == ['a', 'b']),
        # Test on "real" Nexus files:
        (
                'ape_random.trees',
                lambda n: n.comments[0].text == 'R-package APE, Mon Apr  4 13:30:05 2011'),
        #(
        #        'regression/detranslate-beast-2.trees',
        #        lambda n: str(n.TREES.TREE).startswith('TREE1 = [&R] ((((4[&length')),
        #(
        #        'examples/example.trees',
        #        lambda n: str(n.blocks['TREES'][0].commands['TREE'][2]).endswith('David:0.3086497606)')
        #)
    ]
)
def test_Nexus(nex, expect, fixture_dir):
    if nex.startswith('#'):
        n = Nexus(nex)
    else:
        p = fixture_dir / nex
        n = Nexus.from_file(p)
        nex = p.read_text(encoding='utf8')
    assert expect(n)
    assert str(n) == nex


def test_Nexus_modification():
    nex = Nexus()
    with pytest.raises(AttributeError):
        _ = nex.BLOCK
    nex.append_block('BLOCK', [('cmd', 'stuff')])
    assert str(nex.BLOCK.CMD) == 'stuff'
    with pytest.raises(AttributeError):
        _ = nex.BLOCK.OTHER
    nex.append_command(nex.BLOCK, 'other')
    assert nex.BLOCK.OTHER
    nex.remove_block(nex.BLOCK)
    with pytest.raises(AttributeError):
        _ = nex.BLOCK


def test_Nexus_replace_block():
    nex = Nexus("""#nexus
    BEGIN TAXA;
        TAXLABELS Scarabaeus Drosophila Aranaeus;
    END;
    BEGIN Trees;
        TRANSLATE beetle Scarabaeus, fly Drosophila, spider Aranaeus;
        TREE tree1 = ((beetle,fly),spider);
        TREE tree2 = ((1,2),3);
        TREE tree3 = ((Scarabaeus,Drosophila),Aranaeus);
    END;""")
    trees = []
    for tree in nex.TREES.commands['TREE']:
        trees.append(nex.TREES.translated(tree).newick)
    nex.replace_block(
        nex.TREES, [('TREE', 'tree{} = {}'.format(i + 1, n)) for i, n in enumerate(trees)])
    assert str(nex) == """#NEXUS
    BEGIN TAXA;
        TAXLABELS Scarabaeus Drosophila Aranaeus;
    END;
    BEGIN Trees;
TREE tree1 = ((Scarabaeus,Drosophila),Aranaeus);
TREE tree2 = ((Scarabaeus,Drosophila),Aranaeus);
TREE tree3 = ((Scarabaeus,Drosophila),Aranaeus);
    END;"""


def test_Nexus_validate(caplog):
    nex = Nexus('#NEXUS begin trees; tree t = (a,b)c; translate 1 a, 2 b, 3 c; end;')
    assert not nex.validate(logging.getLogger(__name__))
    assert len(caplog.records) == 1


"""
#NEXUS
BEGIN TAXA;
DIMENSIONS NTAX = 4 ;
TAXLABELS fish frog snake mouse;
END;
BEGIN CHARACTERS;
DIMENSIONS NCHAR=2 0;
FORMAT DATATYPE = DNA;
MATRIX
fish ACATA GAGGG TACCT CTAAG
frog ACTTA GAGGC TACCT CTACG
snake ACTCA CTGGG TACCT TTGCG
mouse ACTCA GACGG TACCT TTGCG;
END;
BEGIN TREES;
TREE best = (fish,(frog,
(snake, mouse))) ;
END; 


PICTURE TAXON=1 FORMAT=GIF ENCODE=UUENCODE SOURCE=INLINE
PICTURE=
'begin 644 tree.GIF
e n d ' ;

"""