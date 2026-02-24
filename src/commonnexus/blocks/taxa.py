"""
Functionality related to reading and writing NEXUS TAXA blocks.
"""
from typing import TYPE_CHECKING, Union, Optional
import collections
from collections.abc import Sequence

from commonnexus.tokenizer import iter_words_and_punctuation, Word, TokenOrString
from .base import Block, Payload

if TYPE_CHECKING:  # pragma: no cover
    from commonnexus.nexus import Nexus

# Taxon labels are ordered and have a 1-based index. `TaxLabelsType` maps this index to the string
# label.
TaxlabelsType = collections.OrderedDict[int, TokenOrString]


class Dimensions(Payload):
    """
    The NTAX subcommand of the DIMENSIONS command indicates the number of taxa. The NEXUS standard
    does not impose limits on number of taxa; a limit may be imposed by particular computer
    programs.

    :ivar int ntax: The number of taxa.
    """
    def __init__(self, tokens, nexus=None):
        super().__init__(tokens, nexus=nexus)
        text = [t.text for t in tokens if not t.is_whitespace]
        assert text[0].upper() == 'NTAX' and text[1] == '='
        self.ntax: int = int(text[2])

    def format(self, *args, **kw):
        raise NotImplementedError()  # pragma: no cover


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

    :ivar TaxlabelsType labels: Mapping of taxon number to taxon label.

    The taxon number is the number of a taxon, as defined by its position in a TAXLABELS
    command. [...] For example, the third taxon listed in TAXLABELS is taxon number 3.
    """
    def __init__(self, tokens, nexus=None):
        super().__init__(tokens, nexus=nexus)
        self.labels: TaxlabelsType = collections.OrderedDict(
            (n, w) for n, w in enumerate(iter_words_and_punctuation(tokens, nexus=nexus), start=1))
        assert len(self.labels) == len(set(self.labels.values())), 'Duplicates in TAXLABELS'
        assert not set(str(n) for n in self.labels).intersection(self.labels.values()), \
            'Numbers as labels'

    def format(self, *args, **kw):
        raise NotImplementedError()  # pragma: no cover


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

    @classmethod
    def from_data(  # pylint: disable=too-many-arguments,arguments-differ
            cls,
            labels: Sequence,
            comment: Optional[str] = None,
            nexus: Optional["Nexus"] = None,
            *,
            TITLE: Optional[str] = None,
            ID: Optional[str] = None,
            LINK: Optional[Union[str, tuple[str, str]]] = None,
    ) -> 'Block':
        return cls.from_commands([
            ('DIMENSIONS', f'NTAX={len(labels)}'),
            ('TAXLABELS', ' '.join(Word(w).as_nexus_string() for w in labels)),
        ], nexus=nexus, TITLE=TITLE, ID=ID, LINK=LINK, comment=comment)
