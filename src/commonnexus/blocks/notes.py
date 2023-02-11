from .base import Block


class Notes(Block):
    """
    The NOTES block stores notes about var-
ious objects in a NEXUS file, including
taxa, characters, states, and trees:
BEGIN NOTES;
[TEXT [TAXON = t a x o n - s e t ] [CHARACTER=
character-set] [STATE=state-set]
[TREE = t r e e - s e t ] SOURCE= {INLINE |
FILE | RESOURCE}TEXT= t e x t - o r -
source-descriptor; ]
[PICTURE [TAX0N=taxan-set] [CHARACTER=
character-set] [STATE= state-set]
[ TREE = tree -set] [FORMAT= {PICT |
TIFF | EPS | JPEG | GIF} ] [ENCODE =
{NONE | UUENCODE | BINHEX} ] SOURCE =
{INLINE | FILE | RESOURCE}PICTURE=
picture-or-source-
descriptor; ]
END;
There are no restrictions on the order of
commands.
If the written description of the taxon-
set, character-set, state-set, or tree-set con-
tains more than one token, it must be en-
closed in parentheses, as in the following
example:
TEXT TAXON= (1-3) TEXT= ' t h e s e taxa
from t h e f a r n o r t h ' ;
If both a taxon-set and a character-set
are specified, then the text or picture ap-
plies to those characters for those particu-
lar taxa. If both a character-set and a state-
set are specified, then the text or picture
applies to those states for those particular
characters.
TEXT.—This command allows text to be
attached to various objects.
The SOURCE subcommand indicates the
location of the text. The INLINE option in-
dicates that the text is present at the end
of the TEXT command; the FILE option in-
dicates that it is in a separate file (the name
of which is then specified in the TEXT sub-
command); the RESOURCE option indicates
that it is in the resource fork of the current
file, in a resource of type TEXT (the numer-
ical ID of which is then specified in the
TEXT subcommand).
For example, in the following
TEXT T A X O N = 5 CHARACTER=2 T E X T = ' 4
specimens observed';
TEXT TAxoN=Pan TEXT= 'This genus
l i v e s in A f r i c a ' ;
TEXT CHARACTER=2 TEXT= ' Perhaps t h i s
character should be deleted' ;
TEXT CHARACTER=1 STATE = 0 TEXT= 'This
state is hard to detect' ;
the first command assigns the note "4
specimens observed" to the data entry for
taxon 5, character 2; the second command
assigns the note "Perhaps this character
should be deleted" to character 2; the third
command assigns the note "This genus
lives in Africa" to the taxon Paw, and the
last command assigns the note "This state
is hard to detect" to state 0 of character 1.
The text or source descriptor must be a
single NEXUS word. If the text contains
NEXUS whitespace or punctuation, it
needs to be surrounded by single quotes,
with any contained single quotes convert-
ed to a pair of single quotes.
PICTURE.— This command allows a pic-
ture to be attached to an object.
The FORMAT subcommand allows spec-
ification of the graphics format of the im-
age.
The SOURCE subcommand indicates the
location of the picture. The INLINE option
indicates that the picture is present at the
end of the PICTURE command; the FILE op-
tion indicates that it is in a separate file
(the name of which is then specified in the
PICTURE subcommand); the RESOURCE op-
tion indicates that it is in the resource fork
of the current file, in a resource of type
PICT (the numerical ID of which is then
specified in the PICTURE command). The
RESOURCE option is designed for Apple
Macintosh® text files.
For example, the following command
PICTURE TAXON=5 CHARACTER=2
FORMAT=GIF SouRCE=file
PiCTURE=wide. t h o r a x . g i f ;
assigns the image in the GIF-formatted file
wide.thorax.gif to the data entry for taxon
5, character 2.
The picture or source descriptor must be
a single NEXUS word. If the picture con-
tains NEXUS whitespace or punctuation, it
needs to be surrounded by single quotes,
with any contained single quotes convert-
ed to a pair of single quotes.
Most graphics formats do not describe
pictures using standard text characters. For
this reason many images cannot be includ-
ed INLINE in a NEXUS command unless
they are converted into text characters. The
ENCODE subcommand specifies the conver-
sion mechanism used for inline images; an
example is shown in Figure 2
    """
    pass
