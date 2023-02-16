"""
Normalise a NEXUS file by

- converting all CHARACTERS/DATA matrices to non-transposed, non-interleaved representation with
  taxon labels (and resolved EQUATEs), extracting taxon labels into a TAXA block.
- converting all DISTANCES matrices to non-interleaved matrices with diagonal and both triangles
  and taxon labels,
- translating all TREEs in all TREES blocks (such that the TRANSLATE command becomes superfluous).
"""


def normalise(nexus):
    raise NotImplementedError()
