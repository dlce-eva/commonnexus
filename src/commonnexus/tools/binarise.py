"""
Recode a CHARACTERS (or DATA) matrix such that it only contains binary characters.
"""
import collections

from commonnexus import Nexus
from commonnexus.blocks.characters import GAP, Characters


def binarise(nexus: Nexus, uncertain_state='0') -> Nexus:
    """
    :param nexus: The `Nexus` object to be binarised.
    :param uncertain_state:
    :return: The changed `Nexus` object.

    .. note::

        The `Nexus` object passed into the function is modified in-place and only returned for
        added convenience.

    .. code-block:: python

        >>> from commonnexus.tools import binarise
        >>> print(binarise(Nexus('''#NEXUS
        ... BEGIN DATA;
        ... DIMENSIONS nchar=1;
        ... FORMAT SYMBOLS="abcde";
        ... MATRIX t1 a t2 b t3 c t4 d t5 e;
        ... END;''')))
        #NEXUS
        BEGIN DATA;
        DIMENSIONS NCHAR=5;
        FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
        CHARSTATELABELS
            1 1_1,
            2 1_2,
            3 1_3,
            4 1_4,
            5 1_5;
        MATRIX
            t1 10000
            t2 01000
            t3 00100
            t4 00010
            t5 00001;
        END;
    """
    # 1. Determine the symbol range per character in the data
    # 2. Recode the matrix
    # 3. Adapt DIMENSIONS.NCHAR, MATRIX, FORMAT.[SYMBOLS|MISSING|GAP], CHARSTATELABELS
    # Possibly copy TAXLABELS
    block = nexus.DATA or nexus.CHARACTERS
    if block.FORMAT:
        assert block.FORMAT.datatype == 'STANDARD'
    matrix = block.get_matrix()
    charstates = collections.defaultdict(set)
    for row in matrix.values():
        for char, value in row.items():
            for v in ([value] if not isinstance(value, (tuple, set)) else value):
                if v != GAP and (v is not None):
                    charstates[char].add(v)
    charstates = {k: sorted(v) for k, v in charstates.items()}
    new = collections.OrderedDict()
    for taxon, row in matrix.items():
        new[taxon] = collections.OrderedDict()
        for char, value in row.items():
            for i, state in enumerate(charstates[char], start=1):
                if value is None:
                    v = None
                elif value == GAP:
                    v = GAP
                else:
                    value = [value] if isinstance(value, str) else value
                    # Note: We code uncertainty like polymorphism!
                    v = '1' if state in value else '0'
                new[taxon]['{}_{}'.format(char, i)] = v
    nexus.replace_block(block, Characters.from_data(new))
    return nexus
