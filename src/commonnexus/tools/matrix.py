"""
Tools to manipulate matrices as returned by
:meth:`commonnexus.blocks.characters.Characters.get_matrix`.
"""
import string
from typing import Union, Optional
import textwrap
import collections
import dataclasses
from collections.abc import Iterable, Generator

from commonnexus.blocks.characters import GAP, State, StateMatrix

HashableState = Union[None, str, frozenset[str], tuple[str]]


@dataclasses.dataclass
class DropChars:
    """Specification of sites by character label in a matrix to be dropped."""
    chars: Optional[Iterable[str]] = dataclasses.field(default_factory=set)
    inverse: bool = False


@dataclasses.dataclass
class DropSpec:
    """Specification of sites in a matrix to be dropped."""
    chars: DropChars = dataclasses.field(default_factory=DropChars)
    uncertain: bool = False
    polymorphic: bool = False
    missing: bool = False
    gapped: bool = False
    constant: bool = False


class CharacterMatrix(collections.OrderedDict):
    """
    A wrapper for the nested ordered dicts returned by
    :meth:`commonnexus.blocks.characters.Characters.get_matrix`, providing
    simpler access to some properties of the data and some conversion functionality.
    """
    def iter_rows(self) -> Generator[list[State], None, None]:
        """Iterate lists of states per taxon."""
        for row in self.values():
            yield list(row.values())

    def iter_columns(self) -> Generator[list[State], None, None]:
        """Iterate lists of states per character."""
        for char in self.characters:
            yield [self[taxon][char] for taxon in self.taxa]

    @property
    def taxa(self) -> list[str]:
        """The list of taxa (labels or numbers) in a matrix."""
        return list(self.keys())

    @property
    def characters(self) -> Union[list[str], None]:
        """The list of characters (labels or numbers) in a matrix."""
        for row in self.values():
            return list(row.keys())
        return None  # pragma: no cover

    @property
    def distinct_states(self) -> set[HashableState]:
        """
        The set of distinct states in a matrix (including missing and gap, if found).
        """
        res = set()
        for r in self.values():
            for v in r.values():
                res.add(frozenset(v) if isinstance(v, set) else v)
        return res

    @property
    def has_missing(self) -> bool:
        """Whether the matrix has missing states."""
        return None in self.distinct_states

    @property
    def has_gaps(self) -> bool:
        """Whether the matrix has gapped states."""
        return GAP in self.distinct_states

    @property
    def has_uncertain(self) -> bool:
        """Whether the matrix has uncertain states."""
        for s in self.distinct_states:
            if isinstance(s, frozenset):
                return True
        return False

    @property
    def has_polymorphic(self) -> bool:
        """Whether the matrix has polymorphic states."""
        for s in self.distinct_states:
            if isinstance(s, tuple):
                return True
        return False

    @property
    def symbols(self) -> set[Union[str, frozenset[str], Union[str]]]:
        """The set of state symbols, excluding missing and gapped."""
        res = set()
        for s in self.distinct_states:
            if (s is not None) and (s != GAP):
                res |= set(s)
        return res

    @property
    def is_binary(self) -> bool:
        """Whether the matrix has only two states."""
        return self.symbols.issubset({'0', '1'}) and not self.has_gaps

    @classmethod
    def binarised(
            cls,
            matrix: StateMatrix,
            statelabels: Optional[dict[str, dict[str, str]]] = None,
    ) -> 'CharacterMatrix':
        """Matrix with multistate characters split into binary characters."""
        statelabels = statelabels or {}
        matrix = cls(matrix)
        charstates = collections.defaultdict(set)
        for i, col in enumerate(matrix.iter_columns()):
            for v in col:
                if v is not None and v != GAP:
                    charstates[matrix.characters[i]] |= set(v)
        charstates = {k: sorted(v, key=str) for k, v in charstates.items()}
        new = collections.OrderedDict()

        for taxon, row in matrix.items():
            new[taxon] = collections.OrderedDict()
            for char, value in row.items():
                #
                # FIXME: don't binarise what's already binary!  pylint: disable=fixme
                #
                for i, state in enumerate(charstates[char], start=1):
                    if value is None:
                        v = None
                    elif value == GAP:
                        v = GAP
                    else:
                        v = ({'1'} if isinstance(value, set) else '1') if state in value else '0'
                    statelabel = statelabels.get(char, {}).get(state) or state
                    new[taxon][f'{char}_{statelabel}'] = v
        return cls(new)

    @classmethod
    def multistatised(
            cls, matrix: StateMatrix, multicharlabel: Optional[str] = None) -> 'CharacterMatrix':
        """
        Convert character data of the form 0010000 to a single multi-state character.
        This kind of data may be obtained from coding wordlist data as "word belongs to cognate set"
        vectors.

        If 26..52 characters are given, RESPECTCASE is added to FORMAT, and A-Za-z is used as symbol
        set.
        """
        matrix = cls(matrix)
        available_states = list(string.ascii_uppercase + string.ascii_lowercase)
        assert matrix.is_binary, "All state symbols must be 0, 1 or None (missing)"
        assert len(matrix.characters) <= len(available_states), \
            "Too many characters to multistatise"

        multicharlabel = multicharlabel or '1'
        # Seed the resulting matrix with `None`, i.e. "missing" values.
        multistate_matrix = cls(
            [(t, collections.OrderedDict([(multicharlabel, None)])) for t in matrix])
        for i, charlabel in enumerate(matrix.characters):
            for taxon in matrix:
                if matrix[taxon][charlabel] == '1':
                    if multistate_matrix[taxon][multicharlabel]:
                        multistate_matrix[taxon][multicharlabel] = tuple(
                            list(multistate_matrix[taxon][multicharlabel]) + [available_states[i]])
                    else:
                        multistate_matrix[taxon][multicharlabel] = available_states[i]
        return multistate_matrix

    @classmethod
    def from_characters(cls, matrix: StateMatrix, drop: DropSpec = DropSpec()) -> 'CharacterMatrix':
        """
        :param chars:
        :param inverse:
        :return: A **new** matrix constructed as copy, omitting specified characters.
        """
        matrix = cls(matrix)
        taxa, characters = matrix.taxa, matrix.characters
        res = cls([(t, collections.OrderedDict()) for t in matrix])
        for i, col in enumerate(matrix.iter_columns()):
            char = characters[i]
            if drop.chars.chars and (not drop.chars.inverse) and (char in drop.chars.chars):
                continue
            if drop.chars.chars and drop.chars.inverse and (char not in drop.chars.chars):
                continue
            if drop.uncertain and any(isinstance(v, set) for v in col):
                continue
            if drop.polymorphic and any(isinstance(v, tuple) for v in col):
                continue
            if drop.missing and any(v is None for v in col):
                continue
            if drop.gapped and any(v == GAP for v in col):
                continue
            if drop.constant and \
                    len(set(frozenset(v) if isinstance(v, set) else v for v in col)) == 1:
                continue
            for j, v in enumerate(col):
                res[taxa[j]][char] = v
        return res

    def to_phylip(self) -> str:
        """Convert to phylip format"""
        def phylip_name(s):
            res = ''
            for c in s:
                if c in string.printable and (c not in '()[]:;,'):
                    res += c
                if len(res) >= 10:
                    break
            return res.ljust(10)

        if self.has_uncertain or self.has_polymorphic:
            raise ValueError('Cannot convert matrix with uncertain or polymorphic states.')
        if self.has_missing and '?' in self.symbols:
            raise ValueError('Missing symbol ? used as state symbol')  # pragma: no cover
        if self.has_gaps and '-' in self.symbols:
            raise ValueError('Gap symbol - used as state symbol')  # pragma: no cover

        res = [f"    {len(self.taxa)}   {len(self.characters)}"]
        for taxon, states in self.items():
            seq = ''
            for state in states.values():
                assert isinstance(state, str) or state is None
                seq += '?' if state is None else ('-' if state == GAP else state)
            res.append(f'{phylip_name(taxon)}{seq}')
        return '\n'.join(res)

    def to_fasta(self) -> str:
        """
        :return: The character matrix serialized in the \
        `FASTA format <https://en.wikipedia.org/wiki/FASTA_format>`_
        """
        # convert states codes as digits to letters
        # convert missing *and* gap to '-'
        if self.has_uncertain or self.has_polymorphic:
            raise ValueError('Cannot convert matrix with uncertain or polymorphic states.')

        digits: dict[str, Optional[str]] = {s: None for s in self.symbols if s in string.digits}
        if digits:
            if len(self.symbols) > len(string.ascii_uppercase):  # pragma: no cover
                raise ValueError('Too many symbols in matrix to replace digits with letters')
            for digit in sorted(digits):
                for c in string.ascii_uppercase:
                    if c not in self.symbols and (c not in digits.values()):
                        digits[digit] = c
                        break

        res = []
        for taxon, states in self.items():
            seq = ''.join(
                '-' if state is None or state == GAP else digits.get(state, state)
                for state in states.values())
            res.append(f'> {taxon}')
            res.extend(textwrap.wrap(seq, 70))
        return '\n'.join(res)

    @classmethod
    def from_fasta(cls, fasta: str) -> 'CharacterMatrix':
        """
        .. code-block:: python

            >>> from commonnexus import Nexus
            >>> from commonnexus.blocks import Data
            >>> from commonnexus.tools.matrix import CharacterMatrix
            >>> print(Nexus.from_blocks(Data.from_data(CharacterMatrix.from_fasta(
            ...     '> t1\\nABA BAA\\n> t2\\nBAB ABA'))))
            #NEXUS
            BEGIN DATA;
                DIMENSIONS NCHAR=6;
                FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="AB";
                MATRIX
                t1 ABABAA
                t2 BABABA;
            END;
        """
        def get_row(
                nchar: int,
                seq: list[str],
                taxon: str,
        ) -> tuple[int, collections.OrderedDict[str, str]]:
            if nchar is not None:
                assert len(seq) == nchar, "Only aligned sequences can be converted."
            assert taxon is not None
            return len(seq), collections.OrderedDict([(str(i + 1), c) for i, c in enumerate(seq)])

        res = cls()
        taxon, seq, nchar = None, [], None
        for line in fasta.split('\n'):
            if line.startswith('>'):
                if seq:
                    nchar, res[taxon] = get_row(nchar, seq, taxon)
                taxon, seq = line[1:].strip(), []
                continue
            for chunk in line.strip().split():
                for c in chunk:
                    if c not in string.digits:
                        seq.append(c)
        if seq:
            _, res[taxon] = get_row(nchar, seq, taxon)
        return res
