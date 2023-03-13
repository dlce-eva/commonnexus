import io
import shlex
import logging

import pytest

from commonnexus.__main__ import main as cli
from commonnexus import Nexus


@pytest.fixture
def main():
    def f(args):
        return cli(
            shlex.split(args) if isinstance(args, str) else args, log=logging.getLogger(__name__))
    return f


@pytest.fixture
def mainnexus(main, capsys):
    def f(args):
        main(args)
        out = capsys.readouterr()[0]
        return Nexus(out)
    return f


def test_help(main, capsys):
    assert main('') == 1
    out, _ = capsys.readouterr()
    assert 'commonnexus' in out

    with pytest.raises(SystemExit):
        main('help normalise')
    out, _ = capsys.readouterr()
    assert 'normalise' in out

    main('help')


def test_split(main, tmp_path, fixture_dir, caplog):
    with caplog.at_level(logging.INFO):
        main('split --stem test --outdir {} {}'.format(
            tmp_path, fixture_dir / 'multitaxa_mesquite.nex'))
    assert len(caplog.records) == 10
    for rec in caplog.records:
        _, _, fname = rec.message.partition('written to ')
        assert tmp_path.joinpath(fname).exists()


def test_normalise(main, capsys, mocker):
    main('normalise "#nexus begin block; end;"')
    out, _ = capsys.readouterr()
    assert out.strip() == "#NEXUS\nBEGIN block;\nEND;"
    # Make sure reading from stdin works:
    mocker.patch('commonnexus.cli_util.sys.stdin', io.StringIO('#nexus begin block; end;'))
    main('normalise -')
    out, _ = capsys.readouterr()
    assert out.strip() == "#NEXUS\nBEGIN block;\nEND;"


def test_combine(main, capsys, fixture_dir):
    nex = "#nexus begin data; dimensions nchar=1; matrix t1 1 t2 0 t3 1; end;"
    main('combine "{0}{0}" "{0}"'.format(nex))
    out, _ = capsys.readouterr()
    assert '111' in out and '000' in out
    # Combine non-STANDARD datatype from file:
    main('combine {0} {0}'.format(fixture_dir / 'christophchamp_basic.nex'))
    out, _ = capsys.readouterr()
    assert 'MA-LLMA-LL' in out

    main('combine "#nexus begin block; end;" --drop-unsupported')
    out, _ = capsys.readouterr()
    assert out.strip() == '#NEXUS'


def test_taxa(main, mainnexus, capsys, fixture_dir, tmp_path, caplog, morphobank):
    main('taxa {}'.format(fixture_dir / 'christophchamp_basic.nex'))
    out, _ = capsys.readouterr()
    assert len([l for l in out.split('\n') if l.strip()]) == 4

    out = mainnexus('taxa --drop A {}'.format(fixture_dir / 'christophchamp_basic.nex'))
    assert out.taxa == ['B', 'C', 'D']

    out = mainnexus('taxa --rename A,X {}'.format(fixture_dir / 'christophchamp_basic.nex'))
    assert out.taxa == ['X', 'B', 'C', 'D']

    out = mainnexus('taxa --rename "lambda l: chr(ord(l) + 4)" {}'.format(
        fixture_dir / 'christophchamp_basic.nex'))
    assert out.taxa == ['E', 'F', 'G', 'H']

    nex = tmp_path.joinpath('test.nex')
    nex.write_text(str(out), encoding='utf8')
    main('taxa --check {}'.format(str(nex)))
    assert not caplog.records

    nex = tmp_path / 'test.nex'
    nex.write_text("""#nexus
begin taxa; dimensions ntax=4; taxlabels A B C D; end;
begin distances;
matrix A 0 B 1 0 C 2 1 0 D 3 2 1 0;
end;""", encoding='utf8')
    out = mainnexus('taxa --rename A,X {}'.format(nex))
    assert out.taxa == ['X', 'B', 'C', 'D']
    assert 'X' in out.DISTANCES.get_matrix()

    out = mainnexus('taxa --drop A {}'.format(nex))
    assert out.taxa == ['B', 'C', 'D']
    assert list(out.DISTANCES.get_matrix()) == ['B', 'C', 'D']

    nex = tmp_path / 'test.nex'
    nex.write_text("""#nexus
    begin taxa; dimensions ntax=4; taxlabels A B C D; end;
    begin trees; translate 1 A, 2 B, 3 C, 4 D;
    tree 1 = (1,2,3,4);
    end;""", encoding='utf8')
    out = mainnexus('taxa --rename A,X {}'.format(nex))
    assert out.taxa == ['X', 'B', 'C', 'D']
    assert 'X' in out.TREES.TRANSLATE.mapping.values()

    out = mainnexus('taxa --drop A {}'.format(nex))
    assert out.taxa == ['B', 'C', 'D']
    assert not out.TREES.TRANSLATE

    out = mainnexus('taxa --rename A,X "#nexus begin distances; matrix A 0 B 1 0 C 2 1 0; end;"')
    assert 'X' in out.taxa
    out = mainnexus('taxa --drop A "#nexus begin distances; matrix A 0 B 1 0 C 2 1 0; end;"')
    assert list(out.DISTANCES.get_matrix()) == ['B', 'C']

    main('taxa --describe 1 {}'.format(morphobank))
    out, _ = capsys.readouterr()
    assert 'Waldman' in out


def test_taxa_check(main, caplog, tmp_path):
    nex = tmp_path / 'test.nex'
    nex.write_text("""#nexus
    begin taxa; dimensions ntax=3; taxlabels A B C; end;
    begin distances;
    matrix A 0 X 1 0;
    end;""", encoding='utf8')
    with pytest.warns(UserWarning, match='undeclared taxa'):
        main('taxa --check {}'.format(nex))

    nex = tmp_path / 'test.nex'
    nex.write_text("""#nexus
begin taxa; dimensions ntax=4; taxlabels A B C D; end;
begin data;
dimensions nchar=1;
matrix A 1 B 0 C 0 X 0;
end;""", encoding='utf8')
    with pytest.warns(UserWarning, match='undeclared taxa'):
        main('taxa --check {}'.format(nex))
    assert len(caplog.records) == 1
    caplog.clear()

    nex = tmp_path / 'test.nex'
    nex.write_text("""#nexus
begin taxa; dimensions ntax=4; taxlabels A B C D; end;
begin trees;
translate 1 A, 2 B, 3 C, 4 X;
tree 1 = ((Y,A,B)Z);
end;""", encoding='utf8')
    with pytest.warns(UserWarning):
        main('taxa --check {}'.format(nex))
    assert len(caplog.records) == 3


@pytest.mark.parametrize(
    'inchar,matrix,op,args,outchar',
    [
        (1, 't1 a t2 b t3 c', 'binarise', '', 3),
        (2, 't1 10 t2 01 t3 00', 'multistatise', 'k', 1),
        (4, 't1 1001 t2 0111 t3 0010', 'multistatise', '"lambda c: str(int(c)%2)"', 2),
        (2, 't1 10 t2 11 t3 10', 'drop', 'constant', 1),
        (2, 't1 10 t2 11 t3 10', 'drop-numbered', '2', 1),
    ]
)
def test_characters(mainnexus, inchar, matrix, op, args, outchar):
    nex = "#nexus begin data; dimensions nchar={}; matrix {}; end;".format(inchar, matrix)
    res = mainnexus('characters --{} {} "{}"'.format(op, args or '', nex))
    assert res.characters.DIMENSIONS.nchar == outchar


def test_characters_binarise(mainnexus, morphobank):
    """Make sure state labels are used to create charlabels of binarised characters."""
    res = mainnexus('characters --binarise {}'.format(morphobank))
    assert "'Spine of urohyal shape_fused to form single spine'" in str(res)


@pytest.mark.parametrize(
    'inchar,matrix,what,nlines',
    [
        (3, 't1 100 t2 110 t3 101', 'binary-setsize', 3),
        (3, 't1 100 t2 010 t3 001', 'binary-unique', 3),
        (2, 't1 10 t2 11 t3 10', 'binary-constant', 1),
        (3, 't1 100 t2 110 t3 101', 'states-distribution', 5),
    ]
)
def test_characters_describe(main, inchar, matrix, what, nlines, capsys):
    nex = "#nexus begin data; dimensions nchar={}; matrix {}; end;".format(inchar, matrix)
    main('characters --describe {} "{}"'.format(what, nex))
    out, _ = capsys.readouterr()
    lines = [l for l in out.split('\n') if l.strip()]
    assert len(lines) == nlines


def test_characters_convert(main, capsys, fixture_dir):
    cli(['characters', str(fixture_dir / 'christophchamp_basic.nex')])
    main('characters --convert fasta {}'.format(fixture_dir / 'christophchamp_basic.nex'))
    out, _ = capsys.readouterr()
    assert out == """> A
MA-LL
> B
MA-LE
> C
MEATY
> D
ME-TE
"""


@pytest.mark.parametrize(
    'op,args,ntrees',
    [
        ('drop', '1-10', 90),
        ('drop', '1,10', 98),
        ('sample', '10', 10),
        ('random', '5', 5),
    ]
)
def test_trees(op, ntrees, args, mainnexus, tmp_path, nexus):
    trees = tmp_path / 'trees.nex'
    trees.write_text(
        str(nexus(TREES="\n".join('TREE {} = (a,b,c)d;'.format(i + 1) for i in range(100)))))
    nex = mainnexus('trees --{} {} {}'.format(op, args or '', trees))
    assert len(nex.TREES.trees) == ntrees


def test_trees_strip_comments(mainnexus):
    nex = mainnexus('trees --strip-comments "#nexus begin trees; tree 1 = (a[c],b); end;"')
    assert '[c]' not in str(nex)
    assert '(a,b)' in str(nex)


def test_trees_describe(main, capsys):
    main('trees --describe "#nexus begin trees; tree the_tree = (a[c],b); end;"')
    out, _ = capsys.readouterr()
    assert 'the_tree' in out


def test_trees_rename(main, capsys):
    main('trees --rename x,y "#nexus begin trees; tree x = (a[c],b); end;"')
    out, _ = capsys.readouterr()
    assert 'y' in out

    main("""trees --rename "lambda x: '{}1'.format(x[0])" "#nexus begin trees; translate a x, b y, c z; tree xy = (a[c],b); end;" """)
    out, _ = capsys.readouterr()
    assert 'x1' in out
