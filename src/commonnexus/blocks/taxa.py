import typing
import collections

from commonnexus.tokenizer import iter_words_and_punctuation
from .base import Block, Payload


class Dimensions(Payload):
    """
    The NTAX subcommand of the DIMENSIONS command indicates the number of taxa. The NEXUS standard
    does not impose limits on number of taxa; a limit may be imposed by particular computer
    programs.

    :ivar int ntax: The number of taxa.
    """
    def __init__(self, tokens):
        super().__init__(tokens)
        text = [t.text for t in tokens if not t.is_whitespace]
        assert text[0].upper() == 'NTAX' and text[1] == '='
        self.ntax = int(text[2])


class Taxlabels(Payload):
    """
    This command defines taxa, specifies their names, and determines their order:

    .. code-block::

        TAXLABELS Fungus Insect Mammal;

    Taxon names are single NEXUS words. They must not correspond to another taxon name or number;
    thus, 1 is not a valid name for the second taxon listed. The standard defines no limit to
    their length, although individual programs might impose restrictions.

    Taxa may also be defined in the CHARACTERS, UNALIGNED, and DISTANCES blocks if the NEWTAXA
    token is included in the DIMENSIONS command; see the descriptions of those blocks for details.

    :ivar typing.Dict[int, str] labels: Mapping of taxon number to taxon label.

    The taxon number is the number of a taxon, as defined by its position in a TAXLABELS
    command. [...] For example, the third taxon listed in TAXLABELS is taxon number 3.
    """
    def __init__(self, tokens):
        super().__init__(tokens)
        self.labels = collections.OrderedDict(
            [(n, w) for n, w in enumerate(iter_words_and_punctuation(tokens), start=1)])
        assert len(self.labels) == len(set(self.labels.values())), 'Duplicates in TAXLABELS'
        assert not set(str(n) for n in self.labels).intersection(self.labels.values()), 'TAXLABELS'


class Taxa(Block):
    """
    The :class:`TAXA block <Taxa>` specifies information about taxa.

    .. code-block::

        BEGIN TAXA;
            DIMENSIONS NTAX=number-of-taxa;
            TAXLABELS taxon-name [taxon-name ...];
        END;

    :class:`DIMENSIONS <Dimensions>` must appear before :class:`TAXLABELS <Taxlabels>`.
    Only one of each command is allowed per block.
    """
    __commands__ = [Dimensions, Taxlabels]
    # optional: TITLE and LINK
