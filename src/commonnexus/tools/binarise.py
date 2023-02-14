"""
Recode a CHARACTERS (or DATA) matrix such that it only contains binary characters.
"""
import collections

from commonnexus.blocks.characters import GAP, Characters


def binarise(nexus, uncertain_state='0'):
    """
    1. Determine the symbol range per character in the data
    2. Recode the matrix
    3. Adapt DIMENSIONS.NCHAR, MATRIX, FORMAT.[SYMBOLS|MISSING|GAP], CHARSTATELABELS
       Possibly copy TAXLABELS

    :param nexus:
    :param uncertain_state:
    :return:
    """
    block = nexus.DATA or nexus.CHARACTERS
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
