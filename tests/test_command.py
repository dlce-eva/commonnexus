import pytest

from commonnexus import Nexus


@pytest.mark.parametrize(
    'cmd,normalised',
    [
        (' cmd;', '\n\tCMD;'),
        (' [c] cmd;', '\n[c]\n\tCMD;'),
        (' cm[c]d;', '\n\tCMD[c];'),
    ]
)
def test_command(cmd, normalised):
    nex = Nexus('#nexus{}'.format(cmd))
    assert str(Nexus([c.with_normalised_whitespace() for c in nex])) == '#NEXUS' + normalised