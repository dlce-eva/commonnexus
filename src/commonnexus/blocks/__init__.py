"""
> The eight primary public blocks are TAXA, CHARACTERS, UNALIGNED, DISTANCES, SETS, ASSUMPTIONS,
> CODONS, TREES, and NOTES.
"""
from .base import Block
from .assumptions import Assumptions
from .characters import Characters
from .codons import Codons
from .distances import Distances
from .notes import Notes
from .sets import Sets
from .taxa import Taxa
from .trees import Trees
from .unaligned import Unaligned
