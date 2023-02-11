from .base import Block


class Codons(Block):
    """
    The CODONS block contains information about the genetic code, the regions of DNA and RNA
    sequences that are protein coding, and the location of triplets coding for amino adds in
    nucleotide sequences.

    .. rst-class:: nexus

        | BEGIN CODONS;
        |   [CODONPOSSET [*] name [( {STANDARD | VECTOR}) ] =
        |     N: character-set,
        |     1: character-set,
        |     2: character-set,
        |     3 : character-set; ]
        |   [GENETICCODE code-name
        |     [([CODEORDER=132|other] [NUCORDER = TCAG|other] [[NO]TOKENS] [EXTENSIONS="symbols-list"])]
        |     = genetic code description];]
        |   [CODESET [*] codeset-name { (CHARACTERS | UNALIGNED | TAXA) } =
        |     code-name:character-set or taxon-set
        |     [,code-name:character-set or taxon-set...]; ]
        | END;

    GENETICCODE must precede any CODESET that refers to it. There are several predefined genetic
    codes:

    .. code-block::

        UNIVERSAL      [universal]
        UNIVERSAL.EXT  [universal, extended]
        MTDNA.DROS     [Drosophila mtDNA]
        MTDNA.DROS.EXT [Drosophila | mtDNA , extended]
        MTDNA.MAM      [Mammalian mtDNA]
        MTDNA.MAM.EXT  [Mamma1ian mtDNA, extended]
        MTDNA.YEAST    [Yeast mtDNA]

    For a summary of the genetic codes, see Osawa et al. (1992). Extended codes are those in which
    "extra" amino acids have been added to avoid disjunct amino adds (see the EXTENSIONS subcommand
    under GENETICCODE).

    CODONPOSSET.—This command stores
information about protein-coding regions
and the codon positions of nucleotide ba-
ses in protein-coding regions and follows
the format of a standard object definition
command.
Those characters designated as 1, 2, or 3
are coding bases specified as being of
positions 1, 2, and 3, respectively. Those
characters designated as N are considered
non-protein-coding. Those characters des-
ignated as ? are of unknown nature. Any
unspedfied bases are considered of un-
known nature (equivalent to ?). If no
CODONPOSSET statement is present, all
bases are presumed of unknown nature.
For example, the following command
CODONPOSSET * c o d i n g =
2 : 1 2 - . \ 3 ,
3 : 1 3 - A 3 ;
designates bases 1-10 as noncoding and
positions the remaining bases in the order
123123123

    GENETICCODE.—GENETICCODE stores in-
formation about a user-defined genetic
code. Multiple GENETICCODES may be de-
fined in the block. This is a standard object
definition command except that the default
genetic code is not indicated by an asterisk
after GENETICCODE.
The genetic code description is a listing
of amino acids. By default, the first amino
add listed is that coded for by the triplet
TTT, and the last amino add listed is that
coded for by GGG. In between, the order
of triplets follows a pattern controlled by
the subcommands NUCORDER and
CODEORDER. By default, the amino acids
are listed in the following order: TTT, TCT,
TAT, TGT, TTC, TCC, TAC, TGC, and so
on. The universal genetic code can thus be
written
GENETICCODE UNTITLED=
F S Y C
F S Y C
L S * *
L S * W
L P H R
L P H R
L P Q R
L P Q R
I T N S
I T N S
I T K R
M T K R
V A D G
V A D G
V A E G
V A E G
This assigns TTT to phenylalanine, TCT to
serine, TAT to tyrosine, TGT to cysteine,
and so on.
The following subcommands are includ-
ed.
1. CODEORDER. The default CODEORDER is
231, indicating that the second codon nu-
cleotide changes most quickly (i.e., codons
represented by adjacent amino acids in the
listing always differ at second positions),
the third nucleotide changes next most
quickly, and the first nucleotide changes
most slowly in the list (such that the co-
dons representing the first 16 listed amino
acids all have the same first nucleotide).
2. NUCORDER. The default NUCORDER is
TCAG, indicating that the codons with T at
a given position are listed first, C next, etc.
For example, if CODEORDER is 123 and the
NUCORDER is ACGT, then the amino acids
would be listed in order to correspond to
codons in the order AAA CAA GAA TAA
ACA CCA GCA TCA, etc.
3. [No] TOKENS. If TOKENS, then amino
acids are to be listed by their standard
three-letter abbreviations for amino acids
(e.g., Leu, Glu). A termination codon is
designated by Ter or Stp. If NOTOKENS (the
default), then the IUPAC symbols are used
in the listing. A termination codon is des-
ignated by an asterisk.
4. EXTENSIONS. This command lists the
symbols for "extra" amino acids that are
added to avoid disjunct amino acids. For
example, serines in the universal code are
coded for by two distinct groups of co-
dons; one cannot change between these
groups without going through a different
amino acid. Serine is therefore disjunct. In
the UNIVERSAL code, serine is kept disjunct,
with all serines symbolized by S. In the
UNIVERSAL.EXT code, however, one serine
group is identified by the extra amino acid
symbol 1 and the other group is identified
by 2. To indicate this, the EXTENSIONS sub-
command would read EXTENSIONS="S S",
indicating that "extra" amino acids 1 and
2 are both serines. In the genetic code de-
scription, the symbols 1 and 2 would then
both stand for serine. For example, the uni-
versal extended genetic code could be rep-
resented by
GENETICCODE * u n i v e r s a l
( NUCORDER=TCAG C O D E O R D E R = 2 1 3
EXTENSIONS= " S S " ) =
H R I T N 2
H R I T N 2
V A D G
V A D G
Q R I T K R V A E G
F 1 Y C L P
F 1 Y C L P
L I * * L P
L 1 * W L P Q R M T K R V A E G ;
(Note that the CODEORDER has been
changed in this example.)

CODESET.—This object definition assigns
genetic codes to various characters and
taxa. All nucleotide sites are designated as
coding, and all amino acid sites have a ge-
netic code assigned to them. If the CHAR-
ACTERS format is used, then character-sets
are to be used in the description, and the
genetic code is thus applied to the char-
acters listed. For example,
CODESET oddcodeset = customcode:
4-99;
designates the genetic code "custom code"
as applying to characters 4-99 for all taxa.
If UNALIGNED, then genetic code is pre-
sumed to apply to all sites in an UNA-
LIGNED block. Such a CODESET command
might look like this:
CODESET mycodeset
(UNALIGNED) = u n i v e r s a l : ALL;
For UNALIGNED, the only character-set that
can be used is ALL.
If the TAXA format is used, then taxon-
sets are used in the description. Thus, dif-
ferent genetic codes can be assigned to dif-
ferent taxa for all characters. Current pro-
grams do not accept any character-set
other than ALL nor any taxon-set other
than ALL.
    """
    pass
