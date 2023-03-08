import pytest

from commonnexus import Nexus
from commonnexus.blocks import Block


@pytest.mark.parametrize(
    'cmds,kw,expect',
    [
        ([('cmd', "'long name'"), 'cmd2', ('cmd3', '', 'comment')], {},
         lambda b, n: len(b.CMD._tokens) == 1 and b.CMD2 and '[comment]' in n),
        ([], dict(TITLE="the title", ID='012def'),
         lambda b, n: b.title == 'the title'.upper() and b.id == '012def'),
        ([], dict(LINK="taxa = above"),
         lambda b, n: 'TAXA' in b.links and 'LINK taxa = above;' in n),
        ([], dict(LINK=("taxa", "above")),
         lambda b, n: 'TAXA' in b.links),
    ]
)
def test_Block_with_nexus(cmds, kw, expect):
    nex = Nexus()
    nex.append_block(Block.from_commands(cmds, nexus=nex, **kw))
    assert expect(nex.BLOCK, str(nex))


def test_Block_as_string():
    assert str(Block.from_commands([])) == '\nBEGIN BLOCK;\nEND;'
