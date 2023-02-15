from commonnexus import Nexus, Config
from commonnexus.blocks import Block


def test_Block_with_nexus():
    nex = Nexus('#nexus', config=Config(quote='"'))
    nex.append_block(Block.from_commands([('cmd', '"long name"')], nexus=nex))
    assert len(nex.BLOCK.CMD._tokens) == 1
