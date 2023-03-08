import pytest

from commonnexus import Nexus
from commonnexus.command import Command


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


def test_serialization():
    cmd = Command.from_name_and_payload('CMD', 'do stuff')
    assert str(cmd) == '\nCMD do stuff;'
