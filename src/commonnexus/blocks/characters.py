"""
A CHARACTERS block defines characters and includes character data. Taxa are usually not defined in
a CHARACTERS block; if they are not, the CHARACTERS block must be preceded by a block that defines
taxon labels and ordering (e.g., TAXA). Details about different types of character data are given
at the end of this section.

Syntax of the CHARACTERS block is as follows:

BEGIN CHARACTERS;
DIMENSIONS [NEWTAXA NTAX=number-of-taxa] NCHAR=number-of-characters;
[FORMAT
[ DATATYPE = { STANDARD! DNA | RNA | NUCLEOTIDE I PROTEIN | CONTINUOUS} ]
[RESPECTCASE]
[MISSING=symbol]
[ GAP=symbol]
[ SYMBOLS = " symbol [symbol...]"]
[ EQUATE = " symbol = entry [symbol = entry... ] " ]
[MATCHCHAR= symbol ]
[ [No] LABELS]
[TRANSPOSE]
[INTERLEAVE]
[ITEMS = ( [MIN] [MAX] [MEDIAN] [AVERAGE] [VARIANCE] [STDERROR] [SAMPLESIZE] [STATES]) ]
[STATESFORMAT= {STATESPRESENT | INDIVIDUALS | COUNT | FREQUENCY}.]
[ [No] TOKENS]
; ]
[ELIMINATE character-set; ]
[TAXLABELS taxon-name [taxon-name ...];]
[CHARSTATELABELS
character-number
[character-name]
[/state-name [state-name.
[, character-number
[character-name]
[/state-name [state-name. .]
[CHARLABELS character-name
[character-name...];]
[ STATELABELS
character-number
[state-name [state-name..
[, character-number
[state-name [state-name..
.]]
.]]
MATRIX data-matrix;
END;

DIMENSIONS, FORMAT, and ELIMINATE must all precede CHARLABELS, CHARSTATELABELS, STATELABELS, and
MATRIX. DIMENSIONS must precede ELIMINATE. Only one of each command is allowed per block.

DIMENSIONS.—The DIMENSIONS command specifies the number of characters. The number following NCHAR
is the number of characters in the data matrix. The NEXUS standard does not impose limits on the
number of characters; a limit may be imposed by particular computer programs.

It is strongly advised that new taxa not be defined in a CHARACTERS block, for the
reasons discussed in the description of the DATA block. If new taxa are to be defined,
this must be indicated by the NEWTAXA subcommand, specifying that new taxa are
to be defined (this allows the computer program to prepare for creation of new
taxa). NEWTAXA, if present, must appear before the NTAX subcommand.
The NTAX subcommand, indicating the number of taxa in the MATRIX command
in the block, is optional, unless NEWTAXA is specified, in which case it is required.

The FORMAT command specifies the format of the data MATRIX. This is a crucial command because
misinterpretation of the format of the data matrix could lead to anything from incorrect results
to spectacular crashes. The DATATYPE subcommand must appear first in the command.

The RESPECTCASE subcommand must appear before the MISSING, GAP, SYMBOLS, and MATCHCHAR subcommands.
The following are possible formatting subcommands.

1. DATATYPE = { STANDARD | DNA | RNA | NUCLEOTIDE | PROTEIN | CONTINUOUS}.
   This subcommand specifies the class of data. If present, it must be the first subcommand
   in the FORMAT command. Standard data consist of any general sort of discrete char-
   acter data, and this class is typically used for morphological data, restriction site
   data, and so on. DNA, RNA, NUCLEOTIDE, and PROTEIN designate molecular sequence
   data. Meristic morphometric data and other information with continuous values can
   be housed in matrices of DATATYPE=CONTINUOUS. These DATATYPES are described
   in detail, with examples, at the end of the description of the CHARACTERS block.
2. RESPECTCASE. By default, information in a MATRIX may be entered in uppercase,
   lowercase, or a mixture of uppercase and lowercase. If RESPECTCASE is requested,
   case is considered significant in SYMBOLS, MISSING, GAP, and MATCHCHAR subcom-
   mands and in subsequent references to states. For example, if RESPECTCASE is invoked, then
   SYMBOLS="A a B b" designates four states whose symbols are A, a, B, and b, which can then each
   be used in the MATRIX command and elsewhere. If RESPECTCASE is not invoked, then A and a
   are considered homonymous state symbols. This subcommand must appear be-
   fore the SYMBOLS subcommand. This subcommand is not applicable to DATA-
   TYPE = DNA, RNA, NUCLEOTIDE, PROTEIN, and CONTINUOUS.
3. MISSING. This subcommand declares the symbol that designates missing data.
   The default is "?". For example, MISSING =X defines an X to represent missing
   data. Whitespace is illegal as a missing data symbol, as are the following symbols:
   ( ) [ ] { } / \ , ; : = * ' " * < > A
4. GAP. This subcommand declares the symbol that designates a data gap (e.g.,
   base absent in DNA sequence because of deletion or an inapplicable character in
   morphological data). There is no default gap symbol; a gap symbol must be defined
   by the GAP subcommand before any gaps can be entered into the matrix. For exam-
   ple, G A P = - defines a hyphen to represent a gap. Whitespace is illegal as a gap sym-
   bol, as are the following symbols: ( ) [ ] { } / \ , ; : = * ' " v < > A
5. SYMBOLS. This subcommand specifies the symbols and their order for character
   states used in the file (including in the MATRIX command). For example, SYMBOLS="0
   1 2 3 4 5 6 7 " designates numbers 0 through 7 as acceptable symbols in a ma-
   trix. The SYMBOLS subcommand is not allowed for DATATYPE=CONTINUOUS. The
   default symbols list differs from one DATATYPE to another, as described under
   state symbol in the Appendix. Whitespace is not needed between elements: SYM-
   BOLS="012" is equivalent to SYMBOLS="0 1 2". For STANDARD DATATYPES, a SYMBOLS
   subcommand will replace the default symbols list of "0 1". For DNA, RNA, NUCLE-
   OTIDE, and PROTEIN DATATYPES, a SYMBOLS subcommand will not replace the default
   symbols list but will add character-state symbols to the SYMBOLS list. The NEXUS
   standard does not define the position of these additional symbols within the SYM-
   BOLS list. (These additional symbols will be inserted at the beginning of the SYMBOLS
   list in PAUP and at the end in MacClade. MacClade will accept additional symbols
   for PROTEIN but not DNA, RNA, and NuCLEOTIDE matrices.)
6. EQUATE. This subcommand allows one
to define symbols to represent one matrix
entry. For example, EQUATE="E=(012)"
means that each occurrence of E in the MA-
TRIX command will be interpreted as
meaning states 0, 1, and 2. The equate
symbols cannot be ( ) [ ] { } / \ , ; : = *
1 " v < > A or any or the currently defined
MISSING, GAP, MATCHCHAR, or state SYM-
BOLS. Case is significant in equate symbols.
That is, MISSING=? EQUATE="E=(012)
e=?" means that E will be interpreted as
0, 1, and 2 and e will be interpreted as
missing data.
7. MATCHCHAR. This subcommand defines
a matching character symbol. If this sub-
command is included, then a matching
character symbol in the MATRIX indicates
that the states are equivalent to the states
possessed by the first taxon listed in the
matrix for that character. In the following
matrix, the sequence for taxon 2 is
GACTTTC:
BEGIN DATA;
DIMENSION N C H A R = 7 ;
FORMAT DATATYPE=DNA MATCHCHAR = . ;
MATRIX
t a x o n _ l GACCTTA
taxon_2 . . . T . . C
taxon_3 . . T . C . . ;
END;
Whitespace is illegal as a matching char-
acter symbol, as are the following symbols:
( ) [ ] { } / \ , ; : = * " ' * < > A
8. [No] LABELS. This subcommand de-
clares whether taxon or character labels are
to appear on the left side of the matrix. By
default, they should appear. If NOLABELS
is used, then no labels appear, but then all
currently defined taxa must be included in
the MATRIX in the order in which they
were originally defined.
9. TRANSPOSE. This subcommand indi-
cates that the MATRIX is in transposed for-
mat, with each row of the matrix repre-
senting the information from one character
and each column representing the infor-
mation from one taxon. The following is an
example of a TRANSPOSEd MATRIX:
MATRIX
c h a r a c t e r _ l 1 0 1 1 0 1
c h a r a c t e r _ 2 0 1 1 1 0 0
c h a r a c t e r _ 3 0 1 1 1 1 0 ;
10. INTERLEAVE. This subcommand in-
dicates that the MATRIX is in interleaved
format, i.e., it is broken up into sections. If
the data are not transposed, then each sec-
tion contains the information for some of
the characters for all taxa. For example, the
first section might contain data for char-
acters 1-50 for all taxa, the second section
contains data for characters 51-100, etc.
Taxa in each section must occur in the
same order. This format is especially useful
for molecular sequence data, where the
number of characters can be large. A small
interleaved matrix follows:
MATRIX
t a x o n _ l A C C T C G G C
t a x o n _ 2 A C C T C G G C
t a x o n _ 3 A C G T C G C T
t a x o n _ 4 A C G T C G C T
taxon_l T T A A C G A
taxon_2 T T A A C C A
taxon_3 C T C A C C A
taxon_4 T T C A C C A
The interleaved sections need not all be of
the same length. In an interleaved matrix,
newline characters are significant: they in-
dicate that the next character information
encountered applies to a different taxon
(for nontransposed matrices).
11. ITEMS. Each entry in the matrix gives
information about a character's condition
in a taxon. The.ITEMS subcommand indi-
cates what items of information are listed
at each entry of the matrix. With discrete
character data, the entry typically consists
of the states observed in the taxon (either
the single state observed or several states
if the taxon is polymorphic or of uncertain
state). This can be specified by the state-
ment ITEMS=STATES, but because it is the
default and the only option allowed by
most current programs for discrete data,
an ITEMS statement is usually unnecessary.
For continuous data, however, the wealth
of alternatives (average, median, variance,
minimum, maximum, sample size)t often
requires an explicit ITEMS statement to in-
dicate what information is represented in
each data matrix entry. Some ITEMS (such
as VARIANCE) would be appropriate to
only some DATATYPES; other ITEMS such as
SAMPLESIZE and STATES would be appro-
priate to most or all DATATYPES. If more
than one item is indicated, parentheses
must be used to surround the list of items,
e.g., ITEMS=(AVERAGE VARIANCE); oth-
erwise the parentheses are unnecessary,
e.g., ITEMS=AVERAGE. More information
about ITEMS options can be found in the
discussion of the different DATATYPES un-
der MATRIX; information specifically about
the STATES option is given under STATES-
FORMAT.
12. STATESFORMAT. The entry in a matrix
usually lists (for discrete data) or may list
(for continuous data) the states observed in
the taxon. The STATESFORMAT subcom-
mand specifies what information is con-
veyed in that list of STATES. In most current
programs for discrete data, when a taxon
is polymorphic the entry of the matrix lists
only what distinct states were observed,
without any indication of the number or
frequency of individuals sampled with
each of the states. Thus, if all individuals
sampled within the taxon have state A, the
matrix entry would be A, whereas if some
have state A and others have state B, the
entry would be (AB), which corresponds
to the option STATESFORMAT=STATES-
PRESENT. Because it is the default for dis-
crete data, this statement is typically un-
necessary with current programs. The
other STATESFORMAT options can be illus-
trated with an example, in which two in-
dividuals of a taxon were observed to have
state A and three were observed to have
state B. When STATESFORMAT=INDIVIDU-
ALS, the state of each of the individuals (or
other appropriate sampling subunit) is list-
ed exhaustively, (A A B B B); when STATES-
FORMAT =COUNT, the number of individu-
als with each observed state is indicated,
e.g., (A:2 B:3); when STATESFORMAT=FRE-
QUENCY, the frequencies of various ob-
served states are indicated, e.g., (A:0.40 B:
0.60). The STATESFORMAT command may
also be used for continuous data, for which
the default is STATESFORMAT=INDIVIDUALS.
13. [No] TOKENS. This subcommand
specifies whether data matrix entries are
single symbols or whether they can be to-
kens. If TOKENS, then the data values must
be full NEXUS tokens, separated by white-
space or punctuation as appropriate, as in
the following example:
BEGIN CHARACTERS;
DIMENSIONS NCHAR= 3 ;
CHARSTATELABELS 1 h a i r / a b s e n t
present, 2 color/red blue,
3 size/small big;
FORMAT TOKENS;
MATRIX
t a x o n _ l absent red b i g
taxon_2 absent b l u e small
taxon_3 p r e s e n t b l u e s m a l l ;
END;
TOKENS is the default (and the only al-
lowed option) for DATATYPE=CONTINUOUS;
NOTOKENS is the default for all other
DATATYPES. TOKENS is not allowed for
DATATYPES DNA, RNA, and NUCLEOTIDE.
If TOKENS is invoked, the standard three-
letter amino acid abbreviations can be used
with DATATYPE = PROTEIN and defined
state names can be used for DATATYPE=
STANDARD.
ELIMINATE.—This command allows spec-
ification of a list of characters that are to
be excluded from consideration. Programs
are expected to ignore ELiMiNATEd char-
acters completely during reading. In
avoiding allocation of memory to store
character information, the programs can
save a considerable amount of computer
memory. (This subcommand is similar to
ZAP in version 3.1.1 of PAUP.) For example,
ELIMINATE 4-100;
tells the program to skip over characters 4
through 100 in reading the matrix. Char-
acter-set names are not allowed in the
character list. This command does not af-
fect character numbers.
TAXLABELS.—This command allows
specification of the names of the taxa. It
serves to define taxa and is only allowed
in a CHARACTERS block if the NEWTAXA to-
ken is included in the DIMENSIONS state-
ment.
CHARSTATELABELS.—This command al-
lows specification of both the names of the
characters and the names of the states.
This command was developed as an alter-
native to the older commands CHARLABELS
and STATELABELS. For example,
CHARSTATELABELS
1 e y e _ c o l o r / r e d blue green,
3 head_shape/round square,
5 pronotum_size/small medium
l a r g e
A forward slash (/) separates the char-
acter name and the state names, with a
comma separating the information for dif-
ferent characters. If no state names are to
be specified, the slash may be omitted; if
no character names are to be specified, the
slash must be included, but no token needs
to be included between the character num-
ber and the slash. If state x is the last state
to be named, then subsequent states need
not be named, but states 1 through x must
be. If no name is to be applied to a state,
enter a single underscore for its name.
Character and state names are single NEX-
US words. Character names must not cor-
respond to another character name or
number; thus, 1 is not a valid name for the
second character listed. There is no restric-
tion on the length of a character or state
name imposed by the NEXUS standard;
however, particular programs may limit
the length. State names cannot be applied
if DATATYPE=CONTINUOUS.
CHARLABELS.—This command allows
specification of names of characters:
CHARLABELS
flange microsculpture
body_length
hind_angles #_spines
s p i n e _ s i z e head_size
pubescent— i n t e r v a l s head_color
clypeal—margin;
Character labels are listed consecutively. If
character x is the last character to be
named, then subsequent characters need
not be named, but characters 1 through x
need to be. If no name is to be applied to
a character, a single underscore can be
used for its name. Character names are
single NEXUS words. They must not cor-
respond to another character name or
number; thus, 1 is not a valid name for the
second character listed.
There is no restriction on the length of a
character name imposed by the NEXUS
standard; however, particular programs
may limit the length. The command
should be used only for nontransposed
matrices (in transposed matrices, the char-
acter labels are defined in the MATRIX com-
mand).
We recommend that programs abandon
this command in place of the more flexible
CHARSTATELABELS command when writ-
ing NEXUS files, although programs
should continue to read CHARLABELS be-
cause many existing NEXUS files use
CHARLABELS.
STATELABELS.—This command allows
specification of the names of states:
STATELABELS
1 a b s e n t p r e s e n t ,
2 i s o d i a m e t r i c t r a n s v e r s e ,
3 '4.5-6.2mm 1 '6.3-7.0mm 1 ' 7 . 7 -
11.0mm' ' >12.0mm',
4 rounded subangulate angulate,
10 0 '1-4' '6-9' '7-9' '8-9' 7 8 9,
11 black rufous metallic flavous,
12 straight concave,
(The single quotes that surround some of
the state labels in this example are needed
to properly define the boundaries of the
words; see the definition of word in the Ap-
pendix.) State labels need not be specified
for all characters. A comma must separate
state labels for each character. State labels
are listed consecutively within a character.
If state x is the last state to be named, then
subsequent states need not be named, but
states 1 through x must be. If no name is
to be applied to a state, enter a single un-
derscore for its name. State names are sin-
gle NEXUS words. The standard defines
no limit to their length, although individ-
ual programs might impose restrictions.
This command is not valid for DATA-
TYPE =CONTINUOUS.
We recommend that programs abandon
this command in place of the more flexible
CHARSTATELABELS command when writ-
ing NEXUS files, although programs
should continue to read STATELABELS be-
cause many existing NEXUS files use
STATELABELS.
MATRIX.—In its standard format, the
MATRIX command contains a sequence of
taxon names and state information for that
taxon. The MATRIX itself is of the form
MATRIX
taxon-name entry entry. . . entry
taxon-name entry entry. . . entry
taxon-name entry entry. . . entry;
Each entry in the matrix is the information
about a particular character for a particu-
lar taxon. For example, it might be the as-
signment of state 0 to taxon 1 for character
1. Thus, the entry would consist of one
state symbol, 0. If the taxon were poly-
morphic, the entry would consiste of mul-
tiple state symbols, e.gv (0 1), indicating
the taxon has both states 0 and 1. More
details about the nature of each entry of
the matrix are given under ITEMS and un-
der each DATATYPE.
Each entry needs to be enclosed in pa-
rentheses or braces whenever more than
one state symbol is given, e.g. (01) with
standard data and the default NOTOKENS
option, or if the information is conveyed by
more than one NEXUS token, e.g., (0:100)
or (2.3 4.5 6.7). Otherwise, the parentheses
or braces are optional. No whitespace is
needed between entries in the matrix un-
less the TOKENS subcommand of the FOR-
MAT command is invoked or implied and
parentheses or braces do not surround an
entry.
Taxa need not be in the same order as
in the TAXA block, and the matrix need not
contain all taxa. For interleaved matrices,
all sections must have the same taxa in the
same order.
Examples of matrices of different
DATATYPES are described below.
1. STANDARD data. For DATATYPE =
STANDARD, each entry of the matrix con-
sists of a single state-set. Under the de-
faults (ITEMS=STATES and STATESFORMAT=
STATESPRESENT), each entry of the matrix
consists of a single state-set; if there are
multiple states, then the entry must be en-
closed in parentheses (indicating polymor-
phism) or braces (indicating uncertainty in
state). For example, in the following ma-
trix,
BEGIN CHARACTERS;
DIMENSIONS N C H A R = 9 ;
FORMAT SYMBOLS= " - + x " ;
MATRIX
t a x o n _ l (- + ) { - + }+ + - -
taxon_2 +X- + H hx
taxon_3 - + + + + - - +x;
END;
taxon_l is polymorphic for the first char-
acter and has either state - or state + for
the second character. If STATESFORMAT=
COUNT or FREQUENCY, then each entry
must be enclosed in parentheses because
more than one token is required to convey
information for even one state:
BEGIN CHARACTERS;
DIMENSIONS N C H A R = 3 ;
FORMAT STATESFORMAT=FREQUENCY
SYMBOLS = " 0 1 2 " ;
MATRIX
t a x o n _ l ( 0 : 0 . 2 5 1 : 0 . 7 5 )
( 0 : 0 . 3 1 : 0 . 7 )
( 0 : 0 . 5 1 : 0 . 3 2 : 0 . 2 )
t a x o n _ 2 ( 0 : 0 . 4 1 : 0 . 6 )
( 0 : 0 . 8 1 : 0 . 2 ) ( 1 : 0 . 1 5 2 : 0 . 8 5 )
t a x o n _ 3 ( 0 : 0 . 0 1 : 1 . 0 )
( 0 : 0 . 5 5 1 : 0 . 4 5 ) ( 0 : 0 . 1 1 : 0 . 9 ) ;
END;
2. DNA, RNA, NUCLEOTIDE, and P R O -
TEIN data. For D A T A T Y P E = D N A , RNA,
NUCLEOTIDE, or PROTEIN, each entry of the
matrix consists of one or more state sym-
bols describing the state(s) at one site in a
molecular sequence. If STATESFOR-
MAT=STATESPRESENT and if an entry rep-
resents a single state, then it is represented
as a single state symbol (or if DATA-
TYPE =PROTEIN and TOKENS, as a three-let-
ter amino acid name). If an entry repre-
sents multiple states, then it must be
enclosed in parentheses (indicating poly-
morphism) or braces (indicating uncertain-
ty in state). Following is a matrix of
DATATYPE=DNA:
BEGIN CHARACTERS;
DIMENSIONS N C H A R = 1 2 ;
FORMAT DATATYPE = DNA;
MATRIX
t a x o n _ l ACCATGGTACGT
t a x o n _ 2 TCCATGCTACCC
t a x o n _ 3 TCCATGGAACCC;
E N D ;
3. CONTINUOUS data. For DATATYPE=
CONTINUOUS, each entry in the matrix must
be enclosed by parentheses if more than one
item is specified in the ITEMS subcommand.
Parentheses must also be used whenever
multiple tokens are needed for an entry in
the matrix. If an entry consists of a single
token (eg., 0.231), it may be written without
parentheses but must then be separated
from other entries by whitespace.
MATRIX
A 0 . 4 5 3 1 . 4 3 7 8 . 6
B 0 . 3 4 1 . 0 2 5 5 . 7
C 0 . 2 2 1 . 7 9 6 9 . 1 ;
A matrix entry can include average, min-
imum, maximum, variance, standard error,
sample size, and a listing of states ob-
served in the taxon, as specified in the
ITEMS subcommand. The sample size, if in-
cluded, must be in the form of an integer;
the other numbers can be either in English
decimal (e.g., 0.00452) or in exponential
form (e.g., 4.52E-3).
The information listed for each taxon for
a continuous character is specified in the
ITEMS subcommand of the FORMAT com-
mand. For example, if the matrix contains
only information about the minimum and
maximum value for each taxon, the ITEMS
subcommand would be
ITEMS = (MIN MAX)
and a small matrix might look something
like this:
MATRIX
t a x o n _ l ( 0 . 2 1 0 . 4 5 ) ( 0 . 3 4 0 . 3 6 )
t a x o n _ 2 ( 0 . 1 3 0 . 2 2 ) ( 0 . 4 5 0 . 5 5 ) ;
If the ITEMS include the raw measure-
ments (states), e.g., to list a sample of mea-
surements from individuals, then the other
items must precede the listing of states.
There is no restriction on the number of
elements in the listing of states. This ex-
ample has only one continuous character:
FORMAT DATATYPE=CONTINUOUS
I T E M S = (AVERAGE STATES)
STATESFORMAT= INDIVIDUALS ;
MATRIX
t a x o n _ l ( 1 . 2 2 . 1 1.6 0 . 8 1.8 0 . 3
0 . 6 )
t a x o n _ 2 ( 1 . 6 2 . 2 1.7 1.0 2 . 0 1.6
1.9 0 . 8 ) ;
in which the first value is the sample av-
erage and the subsequent values comprise
the sample of observed states.
Possible ITEMS to be included are M I N
(minimum), MAX (maximum), AVERAGE
(sample average), VARIANCE (sample vari-
ance), STDERROR (standard error), MEDIAN
(sample median), SAMPLESIZE, and STATES.
The manner of presentations of states can
be indicated using the STATESFORMAT com-
mand. The default ITEMS for continuous
data is AVERAGE.
"""
from .base import Block


class Characters(Block):
    pass
