from commonnexus import Nexus
from commonnexus.tools import binarise


def test_binarise():
    res = binarise(Nexus("""#NEXUS
        BEGIN TAXA;
        DIMENSIONS NTAX=3;
        TAXLABELS Maori Dutch Latin;
        END;
        Begin characters;
        Dimensions ntax=3 nchar=2;
        Format datatype=standard symbols="123456" gap=- transpose nolabels equate="x=(12)";
        Charstatelabels
            1 char1, 2 char2;
        Matrix x23 456
        ;
end;"""))
    assert res.CHARACTERS.DIMENSIONS.nchar == 6
    matrix = res.CHARACTERS.get_matrix()
    assert matrix['Maori']['char1_1'] == '1'
    assert matrix['Maori']['char1_2'] == '1'
    assert matrix['Maori']['char1_3'] == '0'
