from .base import Block


class Sets(Block):
    """
    This block stores sets of objects (char-
acters, states, taxa, etc.). The general struc-
ture of the SETS block is as follows.
BEGIN SETS;
[CHARSET charset-name [ ({STANDARD |
VECTOR} ) ] = character-set; ]
[STATESET stateset-name
[ ({STANDARD | V E C T O R } ) ] =
state-set;]
[CHANGESET changeset-name=
state-set<-> state-set
[state-set<-> state-set...]
;]
[TAXSET taxset-name [ ({ STANDARD |
VECTOR} ) ] = taxon-set; ]
[TREESET treeset-name
[ ({STANDARD | V E C T O R } ) ] =
tree-set;]
[CHARPARTITION partition-name
[([{ [No] TOKENS}]
[ {STANDARD | VECTOR}] ) ]
=subset-name:character-set
[, subset-name:character-set
[TAXPARTITION parti tion-name
[([{ [ N o ] T O K E N S } ]
[ {STANDARD | V E C T O R } ] ) ]
=subset-name:taxon-set
[, subset-name:taxon-set.
[TREEPARTITION partition-name
[([{ [No] TOKENS}]
[ {STANDARD I VECTOR}] )
= s u b s e t - n a m e : t r e e - s e t
[, subset-name:tree-set...]
;]
END;
(See object definition command in the Ap-
pendix for information about STANDARD
versus VECTOR formats.)
An example SETS block is
BEGIN SETS;
CHARSET l a r v a l = 1-3 5-8;
STATESET eyeless = 0;
STATESET eyed=l 2 3;
CHANGESET eyeloss = eyed - >
e y e l e s s ;
TAXSET outgroup=l-4;
TREESET AfrNZVicariance = 3 5 9-12;
CHARPARTITION bodyparts=head: 1-4
7, body:5 6, l e g s : 8 - 1 0 ;
END;
CHARSET.—This command specifies and
names a set of characters; this name can
then be used in subsequent CHARSET def-
initions or wherever a character-set is re-
quired. The VECTOR format consists of 0's
and l's: a 1 indicates that the character is
to be included in the CHARSET; whitespace
is not necessary between 0's and l's. The
name of a CHARSET cannot be equivalent
to a character name or character number.
The character-set CONSTANT is prede-
fined for all DATATYPES; it specifies all in-
variant characters. The character-set RE-
MAINDER is predefined for all DATATYPES;
it specifies all characters not previously
referenced in the command. The character-
set GAPPED is predefined for all DATA-
TYPES; it specifies all characters with a gap
for at least one taxon.
There are four additional predefined
character-sets for characters of DATA-
TYPE =DNA, RNA, and NUCLEOTIDE:
1. Posl. All characters defined by cur-
rent CODONPOSSET as first positions.
2. Pos2. All characters defined by cur-
rent CODONPOSSET as second positions.
3. Pos3. All characters defined by cur-
rent CODONPOSSET as third positions.
4. NONCODING. All characters defined
by current CODONPOSSET as non-protein-
coding sites.
STATESET.—This command allows one to
name a set of states; it is not currently sup-
ported by any program. It is not available
for DATATYPE=CONTINUOUS.
For STANDARD format, the state-set is de-
scribed by a list of state symbols, except
that it should not be enclosed in parenthe-
ses or braces. Any current state-set sym-
bols are valid in the state-set description.
The following STATESET
STATESET t h e S e t = 2 3 4 5;
defines the set composed of states 2, 3, 4,
and 5.
The VECTOR format consists of 0's and
l's: a 1 indicates that the state is to be in-
cluded in the STATESET; whitespace is not
necessary between 0's and l's. For example,
the state-set
STATESET t h e S e t (VECTOR) =1001000;
designates theSet to be the set containing
first and fourth states.
CHANGESET.—This command allows
naming of a set of state changes; it is not
currently supported by any program. It is
not available for DATATYPE=CONTINUOUS.
The description of the CHANGESET con-
sists of pairs of state-sets joined by an op-
erator. State-sets that consist of more than
one token must be contained in parenthe-
ses. There are two allowed operators: ->
and <-> (<- is not allowed). These oper-
ators can best be explained by example.
CHANGESET changesl= (1 2 3) - > (4 6) ;
CHANGESET changes2 = l < - > 4 ;
CHANGESET t r a n s v e r s i o n s = (A G) < - >
(C T) ;
The first CHANGESET represents any
change from 1 to 4, 1 to 6, 2 to 4, 2 to 6, 3
to 4, or 3 to 6, and the second set repre-
sents changes from 1 to 4 and 4 to 1. The
CHANGESET "transversions" defines the set
of all changes between purines and pyrim-
idines as transversions.
TAXSET.—This command defines a set of
taxa. A TAXSET name can be used in sub-
sequent TAXSET definitions or wherever a
taxon-set is required. The name of a
TAXSET cannot be equivalent to a taxon
name or taxon number. The taxa to be in
cluded are described in a taxon-set. For ex-
ample, the following command
TAXSET beetles=0irma- . ;
defines the TAXSET "beetles" to include all
taxa from the taxon Omma to the last de-
fined taxon.
The VECTOR format consists of 0's and
l's: a 1 indicates that the taxon is to be in-
cluded in the TAXSET; whitespace is not
necessary between 0's and l's.
TREESET.—This command defines a set
of trees. A TREESET name can be used in
subsequent TREESET definitions or wher-
ever a tree-set is required. It is not cur-
rently supported by any program. It fol-
lows the same general format as a TAXSET
command.
CHARPARTITION, TAXPARTITION, TREEPAR-
TITION.—These commands define parti-
tions of characters, taxa, and trees, respec-
tively. The partition divides the objects
into several (mutually exclusive) subsets.
They all follow the same format.
There are several formatting options.
The VECTOR format consists of a list of par-
tition names. By default, the name of each
subset is a NEXUS word (this is the TO-
KENS option). The NOTOKENS option is
only available in the VECTOR format; this
allows use of single symbols for the subset
names. Each value in a definition in VEC-
TOR format must be separated by white-
space if the names are tokens but not if
they are NOTOKENS. The following two ex-
amples are equivalent:
TAXPARTITION p o p u l a t i o n s = 1:1-3 ,
2 : 4 - 6 , 3:7 8;
TAXPARTITION p o p u l a t i o n s (VECTOR
NOTOKENS) =11122233;
The following two examples are equiva-
lent:
TAXPARTITION mypartition=
Chiricahua: 1-3,
Huachuca: 4-6, Galiuro: 7 8;
TAXPARTITION mypartition (VECTOR) =
Chiricahua Chiricahua
Chiricahua Huachuca Huachuca
Huachuca Galiuro Galiuro;

    """
    pass
