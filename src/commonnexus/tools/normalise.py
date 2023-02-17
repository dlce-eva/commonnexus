"""
Normalise a NEXUS file by

- converting CHARACTERS/DATA matrices to non-transposed, non-interleaved representation with
  taxon labels (and resolved EQUATEs), extracting taxon labels into a TAXA block.
- converting a DISTANCES matrix to non-interleaved matrices with diagonal and both triangles
  and taxon labels,
- translating all TREEs in a TREES block (such that the TRANSLATE command becomes superfluous).
"""
from commonnexus.blocks.characters import Characters, Data
from commonnexus.blocks.taxa import Taxa


def normalise(nexus, data_to_characters=False):
    taxlabels = None
    characters = nexus.DATA or nexus.CHARACTERS
    if characters:
        matrix = characters.get_matrix()
        taxlabels = list(matrix.keys())
        cls = Data if characters.name == 'DATA' and not data_to_characters else Characters
        nexus.replace_block(characters, cls.from_data(matrix))

    if taxlabels:
        if nexus.TAXA:
            assert nexus.TAXA.DIMENSIONS.ntax == len(taxlabels)
            assert set(nexus.TAXA.TAXLABELS.labels.values()) == set(taxlabels)
        else:
            nexus.prepend_block(Taxa.from_data(taxlabels))
    return nexus