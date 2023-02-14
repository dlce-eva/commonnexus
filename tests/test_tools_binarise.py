from commonnexus import Nexus
from commonnexus.tools import binarise


def test_binarise():
    res = binarise(Nexus("""#NEXUS
        BEGIN TAXA;
        DIMENSIONS NTAX=3;
        TAXLABELS Maori Dutch Latin;
        END;
        Begin characters;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="1234567" gap=- transpose nolabels equate="x=(12)";
        Charstatelabels
            1 char1, 2 char2, 3 char3;
        Matrix x23 4-5 67? 
        ;
end;"""))
    assert res.CHARACTERS.DIMENSIONS.nchar == 7
    matrix = res.CHARACTERS.get_matrix()
    assert matrix['Maori']['char1_1'] == '1'
    assert matrix['Maori']['char1_2'] == '1'
    assert matrix['Maori']['char1_3'] == '0'
