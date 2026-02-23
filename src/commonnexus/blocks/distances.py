"""
Functionality related to reading and writing NEXUS DISTANCES blocks.
"""
import typing
import decimal
import warnings
import itertools
import collections
import dataclasses

from commonnexus.tokenizer import iter_words_and_punctuation, iter_lines, Word, Token, TokenOrString
from commonnexus.util import do_until_stopiteration
from .base import Block, Payload, PayloadTokensType
from . import characters
from . import taxa

if typing.TYPE_CHECKING:  # pragma: no cover
    from commonnexus import Nexus

ODict = typing.OrderedDict
DistanceType = typing.Union[None, decimal.Decimal]
DistanceMatrix = ODict[str, ODict[str, DistanceType]]


class Dimensions(characters.Dimensions):
    """
    The NTAX subcommand of this command is needed to process the matrix when some defined taxa are
    omitted from the distance matrix. The NCHAR subcommand is optional and can be used to indicate
    the number of characters for those analyses that need to know how many characters (if any) were
    used to calculate the distances. NCHAR is not required for successful reading of the matrix.
    As for the CHARACTERS and UNALIGNED block, taxa can be defined in a DISTANCES block if NEWTAXA
    precedes the NTAXA subcommand in the DIMENSIONS command. It is advised that new taxa not be
    defined in a DISTANCES block, for the reasons discussed in the description of the DATA block.
    NEWTAXA, if present, must be appear before the NTAX subcommand.

    :ivar bool newtaxa:
    :ivar typing.Optional[int] nchar:
    :ivar int ntax:
    """
    def check(self) -> None:
        assert (not self.newtaxa) or self.ntax

    def format(self, *args, **kw):
        raise NotImplementedError()  # pragma: no cover


class Format(Payload):
    """
    This command specifies the formatting of the MATRIX. The [NO]LABELS and MISSING subcommands are
    as described in the CHARACTERS block.

    1. TRIANGLE = {LOWER | UPPER | BOTH}. This subcommand specifies whether only the lower left
       half of the matrix is present, or only the upper right, or both halves. Below is one example
       of an upper triangular matrix and one of a matrix with both halves included.

       .. code-block::

            BEGIN DISTANCES;
                FORMAT TRIANGLE=UPPER;
                MATRIX
                    taxon_1 0.0  1.0  2.0  4.0  7.0
                    taxon_2      0.0  3.0  5.0  8.0
                    taxon_3           0.0  6.0  9.0
                    taxon_4                0.0 10.0
                    taxon_5                     0.0;
            END;

       .. code-block::

            BEGIN DISTANCES;
                FORMAT TRIANGLE = BOTH;
                MATRIX
                    taxon_1  0    1.0  2.0  4.0  7.0
                    taxon_2  1.0  0    3.0  5.0  8.0
                    taxon_3  2.0  3.0  0    6.0  9.0
                    taxon_4  4.0  5.0  6.0  0   10.0
                    taxon_5  7.0  8.0  9.0 10.0  0;
            END;

    2. DIAGONAL. If DIAGONAL is turned off, the diagonal elements are not included:

       .. code-block::

            FORMAT NODIAGONAL;
            MATRIX
                taxon_1
                taxon_2  1.0
                taxon_3  2.0  3.0
                taxon_4  4.0  5.0  6.0
                taxon_5  7.0  8.0  9.0 10.0;

       If TRIANGLE is not BOTH and DIAGONAL is turned off, then there will be one row that contains
       only the name of a taxon. This row is required. If TRIANGLE=BOTH, then the diagonal must be
       included.
    3. INTERLEAVE. As in the CHARACTERS block, this subcommand indicates sections in the matrix,
       although interleaved matrices take a slightly different form for distance matrices:

       .. code-block::

            taxon_1  0
            taxon_2  1  0
            taxon_3  2  3  0
            taxon_4  4  5  6
            taxon_5  7  8  9
            taxon_6 11 12 13
            taxon_4  0
            taxon_5 10  0
            taxon_6 14 15  0;

       As in the CHARACTERS block, newline characters in interleaved matrices are significant, in
       that they indicate a switch to a new taxon.
    """
    def __init__(self, tokens: PayloadTokensType, nexus: 'Nexus' = None) -> None:
        super().__init__(tokens, nexus=nexus)
        self.missing = '?'
        self.labels = True
        self.interleave = False
        self.diagonal = True
        self.triangle = 'LOWER'

        if tokens is None:
            return

        words = iter_words_and_punctuation(self._tokens, nexus=nexus)

        def word_after_equals():
            n = next(words)
            assert n.text == '='
            res = next(words)
            return res if isinstance(res, str) else res.text

        def consume():
            word = next(words)
            subcommand = None
            if isinstance(word, str):
                subcommand = word.upper()
            if subcommand in ['TRIANGLE', 'MISSING']:
                setattr(self, subcommand.lower(), word_after_equals())
            elif subcommand in ['INTERLEAVE']:
                setattr(self, subcommand.lower(), True)
            elif subcommand in ['NOLABELS', 'LABELS', 'NODIAGONAL', 'DIAGONAL']:
                setattr(self, subcommand.replace('NO', '').lower(), 'NO' not in subcommand)

        do_until_stopiteration(consume)
        self.triangle = self.triangle.upper()

    def required_cols(
            self,
            rows: ODict,
            ntax: int,
            row_index: typing.Optional[int] = None,
    ) -> int:
        """
        The number of required entries for a distance matrix row depends on TRIANGLE, DIAGONAL and
        the row index.
        """
        if self.triangle == 'BOTH':  # Each row has entries for all taxa.
            ncols = ntax
        elif self.triangle == 'LOWER':  # Each row has one more entry than the previous one.
            if row_index is not None:
                ncols = row_index
            else:
                ncols = 1 if not rows else \
                    len(list(rows.values())[-1]) + (2 if self.diagonal is False else 1)
        else:  # Each row has one entry less than the previous row.
            if row_index is not None:
                ncols = ntax - row_index + 1
            else:
                ncols = ntax - len(list(rows.values()))

        if not self.diagonal:
            # And if the diagonal is missing, we expect one entry less in all cases.
            ncols -= 1
        return ncols

    def format(self, *args, **kw):
        raise NotImplementedError()  # pragma: no cover


class Taxlabels(taxa.Taxlabels):
    """
    This command allows specification of the names and ordering of the taxa. It serves to define
    taxa and is allowed only if the NEWTAXA token is included in the DIMENSIONS statement.
    """
    def format(self, *args, **kw):
        raise NotImplementedError()  # pragma: no cover


class Matrix(Payload):
    """
    This command contains the distance data.

    .. note::

        Since reading the matrix data only makes sense if information from other commands - in
        particular :class:`FORMAT <Format>` - is considered, the ``Matrix`` object does not have
        any attributes for data access. Instead, the matrix data can be read via
        :meth:`Distances.get_matrix`.
    """
    def format(self, *args, **kw):
        raise NotImplementedError()  # pragma: no cover


@dataclasses.dataclass
class DistanceMatrixRow:
    """Helper class for parsing NEXUS distance matrix lines."""
    # A row label may be `None`, a 1-based row index or a string label.
    label: typing.Union[None, int, str] = None
    entries: typing.List[DistanceType] = dataclasses.field(default_factory=list)


class Distances(Block):
    """
    This block contains distance matrices. Taxa are usually not defined in a DISTANCES block; if
    they are not, this block must be preceded by a block that defines taxon labels and ordering
    (e.g., TAXA).
    The syntax of the block is as follows:

    .. rst-class:: nexus

        | BEGIN DISTANCES;
        |   [:class:`DIMENSIONS <Dimensions>` [NEWTAXA] NTAX=num-taxa NCHAR=num-characters;]
        |   [:class:`FORMAT <Format>`
        |     [TRIANGLE={LOWER | UPPER | BOTH}]
        |     [[NO]DIAGONAL]
        |     [[NO]LABELS]
        |     [MISSING=SYMBOL]
        |     [INTERLEAVE]
        |   ;]
        |   [:class:`TAXLABELS <Taxlabels>` taxon-name [taxon-name...];]
        |   :class:`MATRIX <Matrix>` distance-matrix;
        | END;

    Commands must appear in the order listed. Only one of each command is allowed per block.
    """
    __commands__ = [Dimensions, Format, Taxlabels, Matrix]

    @property
    def matrix_format(self) -> Format:
        """The FORMAT command to use with this block."""
        return self.FORMAT or Format(None)

    def _get_ntax_and_labels(self) -> typing.Tuple[int, taxa.TaxlabelsType]:
        ntax, taxlabels = None, collections.OrderedDict()
        if self.DIMENSIONS:
            ntax = self.DIMENSIONS.ntax
        if self.TAXLABELS:
            taxlabels = self.TAXLABELS.labels
            ntax = self.DIMENSIONS.ntax
        elif self.nexus.TAXA:
            taxlabels = self.nexus.TAXA.TAXLABELS.labels
            ntax = self.nexus.TAXA.DIMENSIONS.ntax
        return ntax, taxlabels

    def get_matrix(self) -> DistanceMatrix:
        """
        :return: A full distance matrix encoded as nested ordered dictionaries.

        .. code-block:: python

            >>> from commonnexus import Nexus
            >>> nex = Nexus('''#NEXUS
            ... BEGIN DISTANCES;
            ...     DIMENSIONS NEWTAXA NTAX=5;
            ...     TAXLABELS taxon_1 taxon_2 taxon_3 taxon_4 taxon_5;
            ...     FORMAT TRIANGLE=UPPER;
            ...     MATRIX
            ...         taxon_1 0.0  1.0  2.0  4.0  7.0
            ...         taxon_2      0.0  3.0  5.0  8.0
            ...         taxon_3           0.0  6.0  9.0
            ...         taxon_4                0.0 10.0
            ...         taxon_5                     0.0;
            ... END;''')
            >>> nex.DISTANCES.get_matrix()['taxon_3']['taxon_1']
            Decimal('2.0')
        """
        ntax, taxlabels = self._get_ntax_and_labels()
        raw = self._parse_matrix(
            list(iter_lines(self.MATRIX._tokens))  # pylint: disable=protected-access
            if self.matrix_format.interleave
            else [self.MATRIX._tokens],  # pylint: disable=protected-access
            ntax,
            taxlabels
        )
        if self.matrix_format.labels is False:
            assert taxlabels
        elif not taxlabels:
            taxlabels = collections.OrderedDict(enumerate(raw, start=1))

        # We pad the result rows with None columns on the left as necessary, to make lookup by
        # column index work.
        if self.matrix_format.triangle == 'UPPER':
            for i, key in enumerate(raw):
                raw[key] = [None] * (i if self.matrix_format.diagonal else i + 1) + raw[key]
            if self.matrix_format.diagonal is False and self.matrix_format.labels is False:
                assert (ntax) not in raw, str(raw.keys())
                raw[ntax] = [None]
        elif self.matrix_format.triangle == 'BOTH' and not self.matrix_format.diagonal:
            for i, key in enumerate(raw):
                raw[key].insert(i, None)

        # Match matrix rows to expected taxa:
        validtaxa = set(str(k) for k in taxlabels).union(taxlabels.values())
        restaxa = {str(k): k for k in raw}
        if not set(restaxa).issubset(validtaxa):
            warnings.warn('Pruning undeclared taxa from DISTANCES matrix.')
            for taxon in set(restaxa) - validtaxa:
                del raw[restaxa[taxon]]

        if len(raw) < len(taxlabels):
            # Not all taxa appear in the matrix. Prune expected taxa to make lookup work.
            for k in list(taxlabels.keys()):
                if (str(k) not in restaxa) and (taxlabels[k] not in restaxa):
                    del taxlabels[k]
            taxlabels = collections.OrderedDict(
                (i, label) for i, label in enumerate(taxlabels.values(), start=1))

        # Now we replace the row-index keys in res with string labels.
        raw = {taxlabels.get(k, k): v for k, v in raw.items()}
        assert set(raw.keys()).issubset(taxlabels.values()), "Unmatched taxa in DISTANCES matrix."

        # Now populate a complete matrix with the data read from the tokens:
        return self._populated_matrix(raw, taxlabels)

    def _populated_matrix(
            self,
            res: ODict[TokenOrString, typing.List[DistanceType]],
            taxlabels: taxa.TaxlabelsType,
    ) -> DistanceMatrix:
        # Now populate a complete matrix with the data read from the tokens:
        matrix: DistanceMatrix = collections.OrderedDict([
            (label, collections.OrderedDict([(ll, None) for ll in taxlabels.values()]))
            for label in taxlabels.values()])
        for (na, la), (nb, lb) in itertools.combinations_with_replacement(taxlabels.items(), r=2):
            if na == nb and self.matrix_format.diagonal is False:
                matrix[la][lb] = 0
                continue
            if self.matrix_format.triangle == 'BOTH':  # We might have assymetric distances.
                matrix[la][lb] = res[la][nb - 1]
                matrix[lb][la] = res[lb][na - 1]
            else:
                val = res[la][nb - 1] if self.matrix_format.triangle == 'UPPER' else res[lb][na - 1]
                if nb != na:
                    matrix[la][lb] = matrix[lb][la] = val
                else:
                    matrix[la][lb] = val
        return matrix

    def _parse_matrix(
            self,
            lines: typing.List[typing.Iterable[Token]],
            ntax: int,
            taxlabels: taxa.TaxlabelsType,
    ) -> ODict[int, typing.List[DistanceType]]:
        res = collections.OrderedDict()
        row = DistanceMatrixRow()
        # Now read the matrix data:
        for line in lines:
            if ((not self.matrix_format.labels)
                    and self.matrix_format.required_cols(res, ntax) == 0
                    and 1 not in res):
                # NODIAGONAL NOLABELS TRIANGLE=LOWER
                res[1] = []

            row = self._parse_matrix_line(line, row, res, ntax)
            if self.matrix_format.interleave:
                # We collected a row of entries, now append them to the correct taxon.
                # If we have a label, that's easy.
                if not row.label:
                    self._set_label_for_interleaved_matrix_row(row, res, ntax, taxlabels)
                if row.label not in res:
                    res[row.label] = []
                res[row.label].extend(row.entries)
                row = DistanceMatrixRow()
        return res

    def _set_label_for_interleaved_matrix_row(
            self,
            row: DistanceMatrixRow,
            res: ODict[int, typing.List[DistanceType]],
            ntax: int,
            taxlabels: taxa.TaxlabelsType) -> None:
        """Sets the label attribute of row, if a matching label is found."""
        for ri in taxlabels:
            if ri not in res:
                # First pass must go through all taxa!
                row.label = ri
                break
        if not row.label:
            # The next label to append entries to is the next one still in need of
            # entries!
            for row_index in res:
                if len(res[row_index]) < self.matrix_format.required_cols(
                        res, ntax, row_index=row_index):
                    row.label = row_index
                    break

    def _parse_matrix_line(
            self,
            line: typing.Iterable[Token],
            row: DistanceMatrixRow,
            res: ODict[int, typing.List[DistanceType]],
            ntax: int,
    ) -> DistanceMatrixRow:
        """Parse a single line of a NEXUS DISTANCE matrix."""
        words = iter_words_and_punctuation(line, nexus=self.nexus)
        while 1:
            try:
                t = next(words)
                if (self.matrix_format.labels is not False) and row.label is None:
                    assert isinstance(t, str)
                    row.label = t
                    if (not self.matrix_format.diagonal
                            and not self.matrix_format.interleave
                            and self.matrix_format.triangle == 'LOWER'
                            and not res):
                        # We're done with this row after the label.
                        res[row.label] = []
                        row.label = None
                    continue
                row.entries.append(
                    None if t == self.matrix_format.missing else decimal.Decimal(t))
                if (not self.matrix_format.interleave
                        and (len(row.entries) == self.matrix_format.required_cols(res, ntax))):
                    # We have read the last expected distance value for a row.
                    res[row.label or (len(res) + 1)] = row.entries
                    row = DistanceMatrixRow()
            except StopIteration:
                break
        return row

    @classmethod
    def from_data(  # pylint: disable=too-many-arguments,arguments-differ
            cls,
            matrix: typing.OrderedDict[str, typing.OrderedDict[
                str, typing.Union[None, float, int, decimal.Decimal]]],
            taxlabels: bool = False,
            comment: typing.Optional[str] = None,
            nexus: typing.Optional["Nexus"] = None,
            *,
            TITLE: typing.Optional[str] = None,
            ID: typing.Optional[str] = None,
            LINK: typing.Optional[typing.Union[str, typing.Tuple[str, str]]] = None,
    ) -> 'Block':
        """
        Create a DISTANCES block from the distance matrix `matrix`.

        :param matrix: The distance matrix as dict mapping taxon labels to dicts mapping taxon \
        labels to numbers. A "full" matrix is expected here, just like it is returned from \
        :meth:`Distances.get_matrix`.
        :param taxlabels: Whether to include a TAXLABELS command.
        """
        dimensions = f'NTAX={len(matrix)}'
        if taxlabels:
            dimensions = f'NEWTAXA NTAX={len(matrix)} {dimensions}'
        cmds = [
            # DIMENSIONS: necessary if not all taxa are present in the matrix!
            ('DIMENSIONS', dimensions),
            ('FORMAT', 'TRIANGLE=BOTH MISSING=?'),
        ]
        maxlen, tlabels = 0, {}
        for taxon in matrix:  # We compute maximum taxon label length for pretty printing.
            tlabels[taxon] = Word(taxon).as_nexus_string()
            maxlen = max([maxlen, len(tlabels[taxon])])

        if taxlabels:
            cmds.append(('TAXLABELS', ' '.join(tlabels.values())))

        mrows = []
        for taxon, dists in matrix.items():
            mrows.append(' '.join(
                [tlabels[taxon].ljust(maxlen)] +  # noqa: W504
                ['?' if v is None else str(v) for v in dists.values()]))
        cmds.append(('MATRIX', ''.join('\n' + row for row in mrows) + '\n'))
        return cls.from_commands(cmds, nexus=nexus, TITLE=TITLE, LINK=LINK, ID=ID, comment=comment)
