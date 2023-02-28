from commonnexus import Nexus
from commonnexus.blocks import Block


def test_Block_with_nexus():
    nex = Nexus('#nexus')
    nex.append_block(Block.from_commands(
        [('cmd', "'long name'"), 'cmd2', ('cmd3', '', 'comment')], nexus=nex))
    assert len(nex.BLOCK.CMD._tokens) == 1
    assert nex.BLOCK.CMD2
    assert '[comment]' in str(nex)

    nex = Nexus(hyphenminus_is_text=True)
    nex.append_block(Block.from_commands([], TITLE="the title", ID='012def', nexus=nex))
    assert nex.BLOCK.title == 'the title'.upper()
    assert nex.BLOCK.id == '012def'

    nex = Nexus()
    nex.append_block(Block.from_commands([], LINK="taxa = above", nexus=nex))
    assert 'TAXA' in nex.BLOCK.links
    assert 'LINK taxa = above;' in str(nex)

    nex = Nexus()
    nex.append_block(Block.from_commands([], LINK=("taxa", "above"), nexus=nex))
    assert 'TAXA' in nex.BLOCK.links
