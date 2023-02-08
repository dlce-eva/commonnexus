"""
The TAXA block specifies information
about taxa.
BEGIN TAXA;
DIMENSIONS NT AX=number-of-taxa;
TAXLABELS taxon-name [ taxon-name
. . . ] ;
END;

DIMENSIONS must appear before TAX-
LABELS. Only one of each command is
allowed per block.
DIMENSIONS.—The NTAX subcommand
of the DIMENSIONS command indicates the
number of taxa. The NEXUS standard
does not impose limits on number of taxa;
a limit may be imposed by particular com-
puter programs.
TAXLABELS.—This command defines
taxa, specifies their names, and determines
their order:
TAXLABELS Fungus I n s e c t Mammal;
Taxon names are single NEXUS words.
They must not correspond to another tax-
on name or number; thus, 1 is not a valid
name for the second taxon listed. The stan-
dard defines no limit to their length, al-
though individual programs might impose
restrictions.
Taxa may also be defined in the CHAR-
ACTERS, UNALIGNED, and DISTANCES blocks
if the NEWTAXA token is included in the
DIMENSIONS command; see the descrip-
tions of those blocks for details.
"""
from .base import Block


class Taxa(Block):
    pass
