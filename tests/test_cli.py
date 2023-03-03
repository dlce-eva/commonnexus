import io
import shlex
import logging

import pytest

from commonnexus.__main__ import main as cli


@pytest.fixture
def main():
    def f(args):
        return cli(
            shlex.split(args) if isinstance(args, str) else args, log=logging.getLogger(__name__))
    return f


def test_help(main, capsys):
    assert main('') == 1
    out, _ = capsys.readouterr()
    assert 'commonnexus' in out


def test_normalise(main, capsys, mocker):
    main('normalise "#nexus begin block; end;"')
    out, _ = capsys.readouterr()
    assert out.strip() == "#NEXUS begin block; end;"
    # Make sure reading from stdin works:
    mocker.patch('commonnexus.cli_util.sys.stdin', io.StringIO('#nexus begin block; end;'))
    main('normalise -')
    out, _ = capsys.readouterr()
    assert out.strip() == "#NEXUS begin block; end;"


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
