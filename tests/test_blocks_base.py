from commonnexus import Nexus
from commonnexus.blocks import Block


def test_Block_with_nexus():
    nex = Nexus('#nexus')
    nex.append_block(Block.from_commands([('cmd', "'long name'")], nexus=nex))
    assert len(nex.BLOCK.CMD._tokens) == 1

    nex = Nexus(hyphenminus_is_text=True)
    nex.append_block(Block.from_commands([('TITLE', "the-title")], nexus=nex))
    assert nex.BLOCK.TITLE.title == 'the-title'.upper()
