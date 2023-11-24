import logging

import pytest

from commonnexus import Nexus, Block
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
                '#NEXUS begin distances; matrix t1 0 t2 1 0 t3 2 1 0; end;',
                lambda n: len(n.taxa) == 3),
        (
                "#NEXUS BEGIN AssuMP[co[mm]ent]TiONS; ENDblock;",
                lambda n: 'ASSUMPTIONS' in n.blocks and n.comments[0] == 'co[mm]ent'),
        (
            "#NEXUS begin block; cmd [comment]; end;",
            lambda n: n.BLOCK.CMD.comments == ['comment'],
        ),
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
                lambda n: [nn.name for nn in n.TREES.TREE.newick.walk() if nn.is_leaf] == ['a', 'b']),
        # Test on "real" Nexus files:
        (
                'ape_random.trees',
                lambda n: n.comments[0] == 'R-package APE, Mon Apr  4 13:30:05 2011' and 'TAXA' in n.blocks),
        (
                'quoted_tree_name.nex',
                lambda n: n.TREES.TREE.name.startswith('Transformed') and n.TREES.TREE.newick),
        (
                'regression/detranslate-beast-2.trees',
                lambda n: str(n.TREES.TREE).startswith('TREE1 = [&R] ((((4[&length')),
        (
                'regression/example.trees',
                lambda n: str(n.blocks['TREES'][0].commands['TREE'][2]).endswith('David:0.3086497606)')
        )
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
    assert str(n).strip() == nex.strip(), 'Round-tripping failed!'


@pytest.mark.parametrize(
    'spec,labels,resolved',
    [
        ('2', 't1 t2', ['t2']),
        ('2 - 4', 't1 t2 t3 t4', ['t2', 't3', 't4']),
        ('1 3 - 4', 't1 t2 t3 t4', ['t1', 't3', 't4']),
        ('2 - .', 't1 t2 t3 t4', ['t2', 't3', 't4']),
    ]
)
def test_Nexus_resolve_set_spec(nexus, spec, labels, resolved):
    nex = nexus(TAXA="DIMENSIONS NTAX={}; TAXLABELS {};".format(len(labels.split()), labels))
    assert nex.resolve_set_spec('TAXON', spec.split()) == resolved


def test_Nexus_modification():
    nex = Nexus.from_blocks(Block.from_commands([('CMD', 'stuff')]))
    assert str(nex.BLOCK.CMD) == 'stuff'
    assert nex.BLOCK.OTHER is None
    nex.append_command(nex.BLOCK, 'other')
    assert nex.BLOCK.OTHER
    nex.remove_block(nex.BLOCK)
    assert nex.BLOCK is None


def test_Nexus_replace_block():
    nex = Nexus("""#nexus
    BEGIN TAXA;
        TAXLABELS Scarabaeus Drosophila Aranaeus;
    END;
    BEGIN T[c]rees;
        TRANSLATE beetle Scarabaeus, fly Drosophila, spider Aranaeus;
        TREE tree1 = ((beetle,fly),spider);
        TREE tree2 = ((1,2),3);
        TREE tree3 = ((Scarabaeus,Drosophila),Aranaeus);
    END;""")
    trees = []
    for tree in nex.TREES.trees:
        trees.append(nex.TREES.translate(tree).newick)
    nex.replace_block(
        nex.TREES, [('TREE', 'tree{} = {}'.format(i + 1, n)) for i, n in enumerate(trees)])
    assert str(nex) == """#NEXUS
    BEGIN TAXA;
        TAXLABELS Scarabaeus Drosophila Aranaeus;
    END;
BEGIN TREES;
TREE tree1 = ((Scarabaeus,Drosophila),Aranaeus);
TREE tree2 = ((Scarabaeus,Drosophila),Aranaeus);
TREE tree3 = ((Scarabaeus,Drosophila),Aranaeus);
END;"""


def test_Nexus_validate(caplog):
    nex = Nexus('#NEXUS begin trees; tree t = (a,b)c; translate 1 a, 2 b, 3 c; end;')
    assert not nex.validate(logging.getLogger(__name__))
    assert len(caplog.records) == 1


def test_Config(fixture_dir):
    nex = Nexus.from_file(fixture_dir / 'christophchamp_basic.nex')
    assert nex.TREES.TREE.name == 'basic bush'


def test_encoding_guesser(fixture_dir, tmp_path):
    nex = Nexus.from_file(fixture_dir / 'encoding.nex')
    assert nex.cfg.encoding == 'latin1'
    o = tmp_path / 'test.nex'
    nex.to_file(o)
    assert o.read_text(encoding='latin1') == str(nex)


def test_Booleans_With_Values(fixture_dir):
    nex = Nexus.from_file(fixture_dir / 'christophchamp_dna.nex')
    assert nex.DATA.FORMAT.interleave
    assert len(nex.DATA.get_matrix()['Cow']) == 705


def test_Mesquite_multitaxa(fixture_dir):
    nex = Nexus.from_file(fixture_dir / 'multitaxa_mesquite.nex')
    assert [char.get_matrix() for char in nex.blocks['CHARACTERS']]


def test_comments():
    nex = Nexus('#NEXUS\n[comment]')
    assert nex.comments == ['comment']
    nex.append_block(Block.from_commands([], name='b', comment='block comment'))
    assert nex.comments == ['comment', 'block comment']

    with pytest.raises(ValueError):
        nex = Nexus('#NEXUS\n[comment]]')
        nex.validate()

    with pytest.raises(ValueError):
        nex = Nexus('#NEXUS\nBEGIN b; end;[comment]]')
        nex.validate()
