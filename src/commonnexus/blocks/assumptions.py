from .base import Block


class Assumptions(Block):
    """
    The ASSUMPTIONS block houses assumptions about the data or gives general directions as to how
    to treat them (e.g., which characters are to be excluded from consideration). The commands
    currently placed in this block were primarily designed for parsimony analysis. More commands,
    embodying assumptions useful in distance, maximum likelihood, and other sorts of analyses, will
    be developed in the future.
    For example, matrices specifying relative rates of character state change, useful for both
    distance and likelihood analyses, will eventually be included here.
    The general structure of the assumptions block is

    .. rst-class:: nexus

        | BEGIN ASSUMPTIONS;
        | [OPTIONS [DEFTYPE = type-name]
        | [POLYTCOUNT= {MINSTEPS | MAXSTEPS}]
        | [GAPMODE= {MISSING | NEWSTATE} ] ; ]
        | [USERTYPE type-name [ ( {STEPMATRIX |
        | CSTREE} ) ] =UsERTYPE-description; ]
        | [TYPESET [*] typeset-name
        | [ ({STANDARD | VECTOR} ) ] = TYPESET -
        | definition;]
        | [WTSET [*] wtset-name [( {STANDARD |
        | VECTOR} {TOKENS | NOTOKENS}) ] =
        | WrSET-defini tion; ]
        | [EXSET [*] exset-name [( {STANDARD |
        | VECTOR} ) ] = character-set; ]
        | [ANCSTATES [*] ancstates-name
        | [ ({STANDARD | VECTOR} {TOKENS | NO
        | TOKENS} ) ] = ANCSTATES-defini tion; ]
        | END;

    An example ASSUMPTIONS block follows:

    .. code-block::

        BEGIN ASSUMPTIONS;
            OPTIONS DEFTYPE=ORD;
            USERTYPE m y 0 r d = 4
                0 1 2 3
                . 1 2 3
                1 . 1 2
                2 1 . 1
                3 2 1
            USERTYPE myTree (CSTREE) = ( (0 ,1) a,
( 2 , 3 ) b ) c ;
TYPESET * mixed=lRREv: 1 3 10,
UNORD 5 - 7 ;
WTSET * one = 2 : 1-3 6 1 1 - 1 5 , 3 : 7 8;
WTSET two = 2 :4 9, 3 : 1 - 3 5;
EXSET n o l a r v a l = l - 9 ;
ANCSTATES m i x e d = 0 : 1 3 5-8 1 1 ,
1 : 2 4 9 - 1 5 ;
END;
USERTYPES must be defined before they are
referred to in any TYPESET.
In earlier versions of MacClade and
PAUP, TAXSET and CHARSET also appeared
in the ASSUMPTIONS block. These now ap-
pear in the SETS block. There are a number
of other commands in the ASSUMPTIONS
block that also have SET in their name (e.g.,
WTSET, EXSET), but these commands as-
sign values to objects, they do not define
sets of objects, and therefore they do not
belong in the SETS block. (Commands such
as WTSET and EXSET are so named for his-
torical reasons; although they might ide-
ally be renamed CHARACTERWEIGHTS and
EXCLUDEDCHARACTERS, doing so would
cause existing programs to be incompati-
ble with the file format.) We recommend
that programs also accept TAXSET and
CHARSET commands in the ASSUMPTIONS
block so that older files can be read. In ad-
dition, the GAPMODE subcommand of the
OPTIONS command of this block was orig-
inally housed in an OPTIONS command in
the DATA block. Because this subcommand
dictates how data are to be treated rather
than providing details about the data
themselves, it was moved into the AS-
SUMPTIONS block.
OPTIONS.—This command houses a
number of disparate subcommands. They
are all of the form subcommand=option.
1. DEFTYPE. This subcommand specifies
the default character type for parsimony
analyses. Whenever a character's type is
not explicitly stated, its type is taken to be
the default type. Default DEFTYPE is
UNORD (see the Appendix, character trans-
formation type, for a definition of UNORD).
2. POLYTCOUNT. Setting POLYTCOUNT to
MINSTEPS specifies that trees with polyto-
mies are to be counted (in parsimony anal-
yses) in such a way that the number of
steps for each character is the minimum
number of steps for that character over any
resolution of the polytomy. A tree length
that is the sum of these minimum numbers
of steps may be below the tree length of
the most-parsimonious dichotomous reso-
lution. Setting POLYTCOUNT to MAXSTEPS
specifies that trees with polytomies are to
be counted in such a way that occurrence
of derived states on elements of a polyto-
my are to be counted as independent der-
ivations. Such a tree length may be above
the tree length of any fully dichotomous
resolution. The NEXUS format does not
specify a default value for POLYTCOUNT;
the default value may differ from program
to program.
3. GAPMODE. This subcommand specifies
how gaps are to be treated. GAP-
MODE =MISSING specifies that gaps are to
be treated in the same way as missing
data; GAPMODE=NEWSTATE specifies that
gaps are to be treated as an additional
state (for DNA/RNA/NUCLEOTIDE data, as
a fifth base).
USERTYPE.—This command defines a
character transformation type, as used in
parsimony analysis to designate the cost of
changes between states. There are several
predefined character types (see character
transformation type in the Appendix);
USERTYPE allows additional character
types to be created.
USERTYPE is an object definition com-
mand with the exception that an asterisk
cannot be used to indicate the default type
(default type is stated in the OPTIONS com-
mand of the ASSUMPTIONS block). The stan-
dard defines no limit to the length of the
type name, although individual programs
might impose restrictions.
STEPMATRIX format is
USERTYPE m y M a t r i x (STEPMATRIX) = n
s s s s
. k k k
k . k k
k k . k
k k k
where n is the number of rows and col-
umns in the step matrix, the s's are state
symbols, and the k's are the cost for going
between states. The n can take any value
>2. Diagonal elements may be listed as pe-
riods. If a change is to be prohibited, then
one enters an "i" for infinity. Typically, the
state symbols will be in sequence, but they
need not be. The following matrices assign
values identically:
USERTYPE myMatrix (STEPMATRIX) =4
0 1 2 3
. 1 5 1
1 . 5 1
5 5 . 5
1 1 5 . ;
USERTYPE myMatrix2 (STEPMATRIX) =4
2 0 3 1
. 5 5 5
5 . 1 1
5 1 . 1
5 1 1
The number of steps may be either in-
tegers or real numbers. The range of pos-
sible values will differ from program to
program. Versions 3.0-3.04 of MacClade
use the format name REALMATRIX rather
than STEPMATRIX if the matrix contains
real numbers. Future programs should
treat REALMATRIX as a synonym of
STEPMATRIX.
CSTREE format is very similar to the
TREE format in a TREES block. That is, char-
acter state trees are described in the paren-
thesis notation following the rules given
for TREES of taxa. Instead of taxon labels,
character state symbols are used. Thus,
USERTYPE cstree-name (CSTREE) =
[{list-of-subtrees)]
[state-symbol]];
where each subtree has the same format as
the overall tree and the subtrees are sepa-
rated by commas. Two examples are
shown in Figure 1.
TYPESET.—This command specifies the
type assigned to each character as used in
parsimony analysis. This is a standard ob-
ject definition command. Any characters
not listed in the character-set have the de-
fault character type. See "object definition
command" in the Appendix for informa-
tion about STANDARD versus VECTOR for-
mats. The type names to be used are either
the predefined ones or those defined in a
USERTYPE command. Each value in a defi-
nition in VECTOR format must be separated
by whitespace. The following are equiva-
lent type sets:
TYPESET my t y p e s = O R D : 1 4 6 , UNORD:
2 3 5 ;
TYPESET m y t y p e s (VECTOR) = O R D UNORD
UNORD ORD UNORD ORD;
WTSET.—This command specifies the
weights of each character. This is a stan-
dard object definition command. Any
characters not listed in the character-set
have weight 1. The weights may be either
integers or real numbers. The minimum
and maximum weight value will differ
from program to program. Each value in a
definition in VECTOR format must be sep-
arated by whitespace unless the N O -
TOKENS option is invoked, in which case no
whitespace is needed and all weights must
be integers in the range 0-9. The following
are equivalent weight sets:
WTSET mywts = 3 : 1 4 6, 1: 2 3 5;
WTSET mywts (VECTOR) =3 1 1 3 1 3 ;
In earlier versions of MacClade, the for-
matting subcommand REAL was used to
indicate that real-valued weights were in-
cluded in the WTSET. This subcommand is
no longer in use; programs are expected to
detect the presence of integral or real-value
weights while reading the WTSET com-
mand.
EXSET.—This command specifies which
characters are to be excluded from consid-
eration. This is a standard object definition
command. Any characters not listed in the
character-set are included. The VECTOR for-
mat consists of 0's and l's: a 1 indicates
that the character is to be excluded; white-
space is not necessary between 0's and l's.
The following commands are equivalent
and serve to exclude characters 5, 6, 7, 8,
and 12.
EXSET * toExclude = 5-8 12;
EXSET * toExclude (VECTOR) =
000011110001;
ANCSTATES.—This command allows
specification of ancestral states. This is a
standard object definition command. Any
valid state symbol can be used in the de-
scription for discrete data, and any valid
value can be used for continuous data. TO-
KENS is the default for DATATYPE =
CONTINUOUS; NOTOKENS is the default for
all other DATATYPES. TOKENS is not al-
lowed for DATATYPES DNA, RNA, and Nu-
CLEOTIDE. If TOKENS is invoked, the stan-
dard three-letter amino acid abbreviations
can be used with DATATYPE=PROTEIN and
defined state names can be used for DATA-
TYPE =STANDARD. NOTOKENS is not al-
lowed for DATATYPE=CONTINUOUS.
The following commands are equivalent:
ANCSTATES a n c e s t o r = 0 :1-3 5-7 12,
1:4 8-10, 2 : 1 1 ;
ANCSTATES a n c e s t o r (VECTOR) =
000100011120;
    """
    pass
