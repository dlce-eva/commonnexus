

def test_Taxa(nexus):
    nex = nexus(TAXA="""
DIMENSIONS ntax=4;
TAXLABELS
[1] 'John'
[2] 'Paul'
[3] 'George'
[4] 'Ringo'
;""")
    assert nex.TAXA.DIMENSIONS.ntax == 4
    assert list(nex.TAXA.TAXLABELS.labels.values()) == ['John', 'Paul', 'George', 'Ringo']
