from .base import Block, Payload
from commonnexus.tokenizer import iter_words_and_punctuation


class Eliminate(Payload):
    """
    This command allows specification of a list of characters that are to be excluded from
    consideration. Programs are expected to ignore ELIMINATEd characters completely during reading.
    In avoiding allocation of memory to store character information, the programs can save a
    considerable amount of computer memory. (This subcommand is similar to ZAP in version 3.1.1
    of PAUP.) For example,

    .. code-block::

        ELIMINATE 4-100;

    tells the program to skip over characters 4 through 100 in reading the matrix. Character-set
    names are not allowed in the character list. This command does not affect character numbers.
    """
    def __init__(self, tokens):
        super().__init__(tokens)


class Dimensions(Payload):
    """
    The DIMENSIONS command specifies the number of characters. The number following NCHAR
    is the number of characters in the data matrix. The NEXUS standard does not impose limits on the
    number of characters; a limit may be imposed by particular computer programs.

    It is strongly advised that new taxa not be defined in a CHARACTERS block, for the reasons
    discussed in the description of the DATA block. If new taxa are to be defined, this must be
    indicated by the NEWTAXA subcommand, specifying that new taxa are to be defined (this allows
    the computer program to prepare for creation of new taxa). NEWTAXA, if present, must appear
    before the NTAX subcommand. The NTAX subcommand, indicating the number of taxa in the MATRIX
    command in the block, is optional, unless NEWTAXA is specified, in which case it is required.

    :ivar bool newtaxa:
    :ivar typing.Optional[int] ntax:
    :ivar int nchar:
    """
    def __init__(self, tokens):
        super().__init__(tokens)
        self.newtaxa = False
        self.ntax = None
        self.char = None
        words = iter_words_and_punctuation(tokens)
        while 1:
            try:
                word = next(words)
                subcommand = None
                if isinstance(word, str):
                    subcommand = word.upper()
                if subcommand == 'NEWTAXA':
                    self.newtaxa = True
                elif subcommand == 'NTAX':
                    n = next(words)
                    assert n.text == '='
                    self.ntax = int(next(words))
                elif subcommand == 'NCHAR':
                    n = next(words)
                    assert n.text == '='
                    self.nchar = int(next(words))
            except StopIteration:
                break
        assert self.nchar and not ((not self.newtaxa) or self.ntax)


class Format(Payload):
    """
    The FORMAT command specifies the format of the data MATRIX. This is a crucial command because
    misinterpretation of the format of the data matrix could lead to anything from incorrect results
    to spectacular crashes. The DATATYPE subcommand must appear first in the command.

    The RESPECTCASE subcommand must appear before the MISSING, GAP, SYMBOLS, and MATCHCHAR
    subcommands.

    The following are possible formatting subcommands.

    1. DATATYPE = {STANDARD | DNA | RNA | NUCLEOTIDE | PROTEIN | CONTINUOUS}.
       This subcommand specifies the class of data. If present, it must be the first subcommand
       in the FORMAT command. Standard data consist of any general sort of discrete character data,
       and this class is typically used for morphological data, restriction site data, and so on.
       DNA, RNA, NUCLEOTIDE, and PROTEIN designate molecular sequence data. Meristic morphometric
       data and other information with continuous values can be housed in matrices of
       DATATYPE=CONTINUOUS. These DATATYPES are described in detail, with examples, at the end of
       the description of the CHARACTERS block.
    2. RESPECTCASE. By default, information in a MATRIX may be entered in uppercase,
       lowercase, or a mixture of uppercase and lowercase. If RESPECTCASE is requested,
       case is considered significant in SYMBOLS, MISSING, GAP, and MATCHCHAR subcom-
       mands and in subsequent references to states. For example, if RESPECTCASE is invoked, then
       SYMBOLS="A a B b" designates four states whose symbols are A, a, B, and b, which can then
       each be used in the MATRIX command and elsewhere. If RESPECTCASE is not invoked, then A and a
       are considered homonymous state symbols. This subcommand must appear be-
       fore the SYMBOLS subcommand. This subcommand is not applicable to DATATYPE = DNA, RNA,
       NUCLEOTIDE, PROTEIN, and CONTINUOUS.
    3. MISSING. This subcommand declares the symbol that designates missing data.
       The default is "?". For example, MISSING =X defines an X to represent missing
       data. Whitespace is illegal as a missing data symbol, as are the following symbols:
       ( ) [ ] { } / \\ , ; : = * ' " * ` < > ^
    4. GAP. This subcommand declares the symbol that designates a data gap (e.g.,
       base absent in DNA sequence because of deletion or an inapplicable character in
       morphological data). There is no default gap symbol; a gap symbol must be defined
       by the GAP subcommand before any gaps can be entered into the matrix. For exam-
       ple, GAP = - defines a hyphen to represent a gap. Whitespace is illegal as a gap sym-
       bol, as are the following symbols:  ( ) [ ] { } / \\ , ; : = * ' " * ` < > ^
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
       for PROTEIN but not DNA, RNA, and NUCLEOTIDE matrices.)
    6. EQUATE. This subcommand allows one to define symbols to represent one matrix
       entry. For example, EQUATE="E=(012)" means that each occurrence of E in the MA-
       TRIX command will be interpreted as meaning states 0, 1, and 2. The equate
       symbols cannot be ( ) [ ] { } / \\ , ; : = * ' " * ` < > ^ or any or the currently defined
       MISSING, GAP, MATCHCHAR, or state SYMBOLS. Case is significant in equate symbols.
       That is, MISSING=? EQUATE="E=(012)e=?" means that E will be interpreted as
       0, 1, and 2 and e will be interpreted as missing data.
    7. MATCHCHAR. This subcommand defines a matching character symbol. If this sub-
       command is included, then a matching character symbol in the MATRIX indicates
       that the states are equivalent to the states possessed by the first taxon listed in the
       matrix for that character. In the following matrix, the sequence for taxon 2 is GACTTTC:

       .. code-block::

            BEGIN DATA;
                DIMENSION NCHAR = 7;
                FORMAT DATATYPE=DNA MATCHCHAR = .;
                MATRIX
                    taxon_l GACCTTA
                    taxon_2 ...T..C
                    taxon_3 ..T.C..;
            END;

       Whitespace is illegal as a matching character symbol, as are the following symbols:
        ( ) [ ] { } / \\ , ; : = * ' " * ` < > ^
    8. [No] LABELS. This subcommand declares whether taxon or character labels are
       to appear on the left side of the matrix. By default, they should appear. If NOLABELS
       is used, then no labels appear, but then all currently defined taxa must be included in
       the MATRIX in the order in which they were originally defined.
    9. TRANSPOSE. This subcommand indicates that the MATRIX is in transposed for-
       mat, with each row of the matrix representing the information from one character
       and each column representing the information from one taxon. The following is an
       example of a TRANSPOSEd MATRIX:

       .. code-block::

            MATRIX
                character_1 101101
                character_2 011100
                character_3 011110 ;

    10. INTERLEAVE. This subcommand indicates that the MATRIX is in interleaved
        format, i.e., it is broken up into sections. If the data are not transposed, then each sec-
        tion contains the information for some of the characters for all taxa. For example, the
        first section might contain data for characters 1-50 for all taxa, the second section
        contains data for characters 51-100, etc. Taxa in each section must occur in the
        same order. This format is especially useful for molecular sequence data, where the
        number of characters can be large. A small interleaved matrix follows:

        .. code-block::

            MATRIX
                taxon_1 ACCTCGGC
                taxon_2 ACCTCGGC
                taxon_3 ACGTCGCT
                taxon_4 ACGTCGCT
                taxon_1 TTAACGA
                taxon_2 TTAACCA
                taxon_3 CTCACCA
                taxon_4 TTCACCA

        The interleaved sections need not all be of the same length. In an interleaved matrix,
        newline characters are significant: they indicate that the next character information
        encountered applies to a different taxon (for nontransposed matrices).
    11. ITEMS. Each entry in the matrix gives information about a character's condition
        in a taxon. The.ITEMS subcommand indicates what items of information are listed
        at each entry of the matrix. With discrete character data, the entry typically consists
        of the states observed in the taxon (either the single state observed or several states
        if the taxon is polymorphic or of uncertain state). This can be specified by the state-
        ment ITEMS=STATES, but because it is the default and the only option allowed by
        most current programs for discrete data, an ITEMS statement is usually unnecessary.
        For continuous data, however, the wealth of alternatives (average, median, variance,
        minimum, maximum, sample size)t often requires an explicit ITEMS statement to in-
        dicate what information is represented in each data matrix entry. Some ITEMS (such
        as VARIANCE) would be appropriate to only some DATATYPES; other ITEMS such as
        SAMPLESIZE and STATES would be appropriate to most or all DATATYPES. If more
        than one item is indicated, parentheses must be used to surround the list of items,
        e.g., ITEMS=(AVERAGE VARIANCE); otherwise the parentheses are unnecessary,
        e.g., ITEMS=AVERAGE. More information about ITEMS options can be found in the
        discussion of the different DATATYPES under MATRIX; information specifically about
        the STATES option is given under STATESFORMAT.
    12. STATESFORMAT. The entry in a matrix usually lists (for discrete data) or may list
        (for continuous data) the states observed in the taxon. The STATESFORMAT subcom-
        mand specifies what information is conveyed in that list of STATES. In most current
        programs for discrete data, when a taxon is polymorphic the entry of the matrix lists
        only what distinct states were observed, without any indication of the number or
        frequency of individuals sampled with each of the states. Thus, if all individuals
        sampled within the taxon have state A, the matrix entry would be A, whereas if some
        have state A and others have state B, the entry would be (AB), which corresponds
        to the option STATESFORMAT=STATESPRESENT. Because it is the default for dis-
        crete data, this statement is typically unnecessary with current programs. The
        other STATESFORMAT options can be illustrated with an example, in which two in-
        dividuals of a taxon were observed to have state A and three were observed to have
        state B. When STATESFORMAT=INDIVIDUALS, the state of each of the individuals (or
        other appropriate sampling subunit) is listed exhaustively, (A A B B B); when STATES-
        FORMAT =COUNT, the number of individuals with each observed state is indicated,
        e.g., (A:2 B:3); when STATESFORMAT=FREQUENCY, the frequencies of various ob-
        served states are indicated, e.g., (A:0.40 B:0.60). The STATESFORMAT command may
        also be used for continuous data, for which the default is STATESFORMAT=INDIVIDUALS.
    13. [No] TOKENS. This subcommand specifies whether data matrix entries are
        single symbols or whether they can be tokens. If TOKENS, then the data values must
        be full NEXUS tokens, separated by whitespace or punctuation as appropriate, as in
        the following example:

        .. code-block::

            BEGIN CHARACTERS;
                DIMENSIONS NCHAR= 3 ;
                CHARSTATELABELS 1 hair/absent
                    present, 2 color/red blue,
                    3 size/small big;
                FORMAT TOKENS;
                MATRIX
                    taxon_1 absent red big
                    taxon_2 absent blue small
                    taxon_3 present blue small ;
            END;

        TOKENS is the default (and the only allowed option) for DATATYPE=CONTINUOUS;
        NOTOKENS is the default for all other DATATYPES. TOKENS is not allowed for
        DATATYPES DNA, RNA, and NUCLEOTIDE. If TOKENS is invoked, the standard three-
        letter amino acid abbreviations can be used with DATATYPE = PROTEIN and defined
        state names can be used for DATATYPE=STANDARD.
    """
    def __init__(self, tokens):
        super().__init__(tokens)
        self.datatype = None
        self.respectcase = False
        self.missing = '?'  # FIXME: one-character, most punctuation excluded
        self.gap = None
        self.symbols = []
        self.equate = {}
        self.matchchar = None
        self.labels = None
        self.transpose = False
        self.interleave = False
        self.items = []
        self.statesformat = None
        self.tokens = None
        """
         [ DATATYPE = { STANDARD| DNA | RNA | NUCLEOTIDE I PROTEIN | CONTINUOUS} ]
        [ SYMBOLS = " symbol [symbol...]"]
        [ EQUATE = " symbol = entry [symbol = entry... ] " ]
        [ITEMS=([MIN] [MAX] [MEDIAN] [AVERAGE] [VARIANCE] [STDERROR] [SAMPLESIZE] [STATES])]
        [STATESFORMAT= {STATESPRESENT | INDIVIDUALS | COUNT | FREQUENCY}.]
        """
        words = iter_words_and_punctuation(tokens)

        def word_after_equals():
            n = next(words)
            assert n.text == '='
            return next(words)

        while 1:
            try:
                word = next(words)
                subcommand = None
                if isinstance(word, str):
                    subcommand = word.upper()
                if subcommand in ['DATATYPE', 'MISSING', 'MATCHCHAR', 'GAP', 'STATESFORMAT']:
                    setattr(self, subcommand.lower(), word_after_equals())
                elif subcommand in ['RESPECTCASE', 'TRANSPOSE', 'INTERLEAVE']:
                    setattr(self, subcommand.lower(), True)
                elif subcommand in ['NOLABELS', 'LABELS', 'NOTOKENS', 'TOKENS']:
                    setattr(self, subcommand.replace('NO', '').lower(), 'NO' not in subcommand)
                elif subcommand == 'SYMBOLS':
                    pass  # consume the next word and optionally leading/trailing double quotes
                elif subcommand == 'EQUATE':
                    pass  # "s=(ab)s=a" ...
                elif subcommand == 'ITEMS':
                    pass  # consume the next word, or ( + words + )
            except StopIteration:
                break


class Taxlabels(Payload):
    """
    This command allows specification of the names of the taxa. It
    serves to define taxa and is only allowed in a CHARACTERS block if the NEWTAXA to-
    ken is included in the DIMENSIONS statement.
    """


class Charstatelabels(Payload):
    """
    This command allows specification of both the names of the
    characters and the names of the states. This command was developed as an alter-
    native to the older commands CHARLABELS and STATELABELS. For example,

    .. code-block::

        CHARSTATELABELS
            1 eye_color / red blue green,
            3 head_shape/round square,
            5 pronotum_size/small medium large

    A forward slash (/) separates the character name and the state names, with a
    comma separating the information for different characters. If no state names are to
    be specified, the slash may be omitted; if no character names are to be specified, the
    slash must be included, but no token needs to be included between the character num-
    ber and the slash. If state x is the last state to be named, then subsequent states need
    not be named, but states 1 through x must be. If no name is to be applied to a state,
    enter a single underscore for its name. Character and state names are single NEX-
    US words. Character names must not correspond to another character name or
    number; thus, 1 is not a valid name for the second character listed. There is no restric-
    tion on the length of a character or state name imposed by the NEXUS standard;
    however, particular programs may limit the length. State names cannot be applied
    if DATATYPE=CONTINUOUS.
    """


class Charlabels(Payload):
    """
    This command allows specification of names of characters:

    .. code-block::

        CHARLABELS
            flange microsculpture
            body_length
            hind_angles #_spines
            spine_size head_size
            pubescent—intervals head_color
            clypeal—margin;

    Character labels are listed consecutively. If character x is the last character to be
    named, then subsequent characters need not be named, but characters 1 through x
    need to be. If no name is to be applied to a character, a single underscore can be
    used for its name. Character names are single NEXUS words. They must not cor-
    respond to another character name or number; thus, 1 is not a valid name for the
    second character listed. There is no restriction on the length of a
    character name imposed by the NEXUS standard; however, particular programs
    may limit the length. The command should be used only for nontransposed
    matrices (in transposed matrices, the character labels are defined in the MATRIX com-
    mand). We recommend that programs abandon this command in place of the more flexible
    CHARSTATELABELS command when writing NEXUS files, although programs
    should continue to read CHARLABELS because many existing NEXUS files use CHARLABELS.
    """


class Statelabels(Payload):
    """
    This command allows specification of the names of states:

    .. code-block::

        STATELABELS
            1 absent present,
            2 isodiametric transverse,
            3 '4.5-6.2mm' '6.3-7.0mm' '7.7-11.0mm' '>12.0mm',
            4 rounded subangulate angulate,
            10 0 '1-4' '6-9' '7-9' '8-9' 7 8 9,
            11 black rufous metallic flavous,
            12 straight concave,

    (The single quotes that surround some of the state labels in this example are needed
    to properly define the boundaries of the words; see the definition of word in the Appendix.)
    State labels need not be specified for all characters. A comma must separate state labels for
    each character. State labels are listed consecutively within a character. If state x is the
    last state to be named, then subsequent states need not be named, but states 1 through x must
    be. If no name is to be applied to a state, enter a single underscore for its name. State
    names are single NEXUS words. The standard defines no limit to their length, although individ-
    ual programs might impose restrictions. This command is not valid for DATATYPE =CONTINUOUS.
    We recommend that programs abandon this command in place of the more flexible
    CHARSTATELABELS command when writing NEXUS files, although programs should continue to read
    STATELABuse many existing NEXUS files use STATELABELS.
    """


class Matrix(Payload):
    """
    In its standard format, the MATRIX command contains a sequence of taxon names and state
    information for that taxon. The MATRIX itself is of the form

    .. code-block::

        MATRIX
            taxon-name entry entry... entry
            taxon-name entry entry... entry
            taxon-name entry entry... entry;

    Each entry in the matrix is the information about a particular character for a particular
    taxon. For example, it might be the assignment of state 0 to taxon 1 for character 1.
    Thus, the entry would consist of one state symbol, 0. If the taxon were poly-
    morphic, the entry would consiste of multiple state symbols, e.gv (0 1), indicating
    the taxon has both states 0 and 1. More details about the nature of each entry of
    the matrix are given under ITEMS and under each DATATYPE.
    Each entry needs to be enclosed in parentheses or braces whenever more than
    one state symbol is given, e.g. (01) with standard data and the default NOTOKENS
    option, or if the information is conveyed by more than one NEXUS token, e.g., (0:100)
    or (2.3 4.5 6.7). Otherwise, the parentheses or braces are optional. No whitespace is
    needed between entries in the matrix unless the TOKENS subcommand of the FORMAT command is
    invoked or implied and parentheses or braces do not surround an entry.
    Taxa need not be in the same order as in the TAXA block, and the matrix need not
    contain all taxa. For interleaved matrices, all sections must have the same taxa in the
    same order.
    Examples of matrices of different DATATYPES are described below.

    1. STANDARD data. For DATATYPE=STANDARD, each entry of the matrix con-
       sists of a single state-set. Under the defaults (ITEMS=STATES and STATESFORMAT=
       STATESPRESENT), each entry of the matrix consists of a single state-set; if there are
       multiple states, then the entry must be enclosed in parentheses (indicating polymor-
       phism) or braces (indicating uncertainty in state). For example, in the following matrix,

       .. code-block::

            BEGIN CHARACTERS;
                DIMENSIONS NCHAR=9;
                FORMAT SYMBOLS="-+x";
                MATRIX
                    taxon_1 (-+){-+}+---+--
                    taxon_2 +x-++--+x
                    taxon_3 -++++--+x;
            END;

       taxon_1 is polymorphic for the first character and has either state - or state + for
       the second character. If STATESFORMAT=COUNT or FREQUENCY, then each entry
       must be enclosed in parentheses because more than one token is required to convey
       information for even one state:

       .. code-block::

            BEGIN CHARACTERS;
                DIMENSIONS NCHAR=3;
                FORMAT STATESFORMAT=FREQUENCY
                SYMBOLS = "012";
                MATRIX
                    taxon_1 (0:0.251:0.75) (0:0.31:0.7) (0:0.51:0.32:0.2)
                    taxon_2 (0:0.41:0.6) (0:0.81:0.2) (1:0.152:0.85)
                    taxon_3 (0:0.01:1.0) (0:0.551:0.45) (0:0.11:0.9);
            END;

    2. DNA, RNA, NUCLEOTIDE, and PROTEIN data. For D A T A T Y P E = D N A , RNA,
       NUCLEOTIDE, or PROTEIN, each entry of the matrix consists of one or more state sym-
       bols describing the state(s) at one site in a molecular sequence. If STATESFOR-
       MAT=STATESPRESENT and if an entry represents a single state, then it is represented
       as a single state symbol (or if DATATYPE =PROTEIN and TOKENS, as a three-let-
       ter amino acid name). If an entry represents multiple states, then it must be
       enclosed in parentheses (indicating polymorphism) or braces (indicating uncertain-
       ty in state). Following is a matrix of DATATYPE=DNA:

       .. code-block::

            BEGIN CHARACTERS;
                DIMENSIONS NCHAR=12;
                FORMAT DATATYPE = DNA;
                MATRIX
                    taxon_1 ACCATGGTACGT
                    taxon_2 TCCATGCTACCC
                    taxon_3 TCCATGGAACCC;
            END;

    3. CONTINUOUS data. For DATATYPE=CONTINUOUS, each entry in the matrix must
       be enclosed by parentheses if more than one item is specified in the ITEMS subcommand.
       Parentheses must also be used whenever multiple tokens are needed for an entry in
       the matrix. If an entry consists of a single token (eg., 0.231), it may be written without
       parentheses but must then be separated from other entries by whitespace.

       .. code-block::

            MATRIX
                A 0.453 1.43 78.6
                B 0.34 1.02 55.7
                C 0.22 1.79 69.1;

       A matrix entry can include average, minimum, maximum, variance, standard error,
       sample size, and a listing of states observed in the taxon, as specified in the
       ITEMS subcommand. The sample size, if included, must be in the form of an integer;
       the other numbers can be either in English decimal (e.g., 0.00452) or in exponential
       form (e.g., 4.52E-3).
       The information listed for each taxon for a continuous character is specified in the
       ITEMS subcommand of the FORMAT command. For example, if the matrix contains
       only information about the minimum and maximum value for each taxon, the ITEMS
       subcommand would be ITEMS = (MIN MAX) and a small matrix might look something like this:

       .. code-block::

            MATRIX
                taxon_1 (0.21 0.45) (0.34 0.36)
                taxon_2 (0.13 0.22) (0.45 0.55);

       If the ITEMS include the raw measurements (states), e.g., to list a sample of mea-
       surements from individuals, then the other items must precede the listing of states.
       There is no restriction on the number of elements in the listing of states. This ex-
       ample has only one continuous character:

       .. code-block::

            FORMAT DATATYPE=CONTINUOUS ITEMS=(AVERAGE STATES) STATESFORMAT=INDIVIDUALS;
            MATRIX
                taxon_1 (1.2 2.1 1.6 0.8 1.8 0.3 0.6)
                taxon_2 (1.6 2.2 1.7 1.0 2.0 1.6 1.9 0.8);

       in which the first value is the sample average and the subsequent values comprise
       the sample of observed states. Possible ITEMS to be included are MIN
       (minimum), MAX (maximum), AVERAGE (sample average), VARIANCE (sample vari-
       ance), STDERROR (standard error), MEDIAN (sample median), SAMPLESIZE, and STATES.
       The manner of presentations of states can be indicated using the STATESFORMAT com-
       mand. The default ITEMS for continuous data is AVERAGE.
    """


class Characters(Block):
    """
    A CHARACTERS block defines characters and includes character data.

    Taxa are usually not defined in a CHARACTERS block; if they are not, the CHARACTERS block must
    be preceded by a block that defines taxon labels and ordering (e.g., TAXA).

    Syntax of the CHARACTERS block is as follows:

    .. code-block::

        BEGIN CHARACTERS;
            DIMENSIONS [NEWTAXA NTAX=number-of-taxa] NCHAR=number-of-characters;
            [FORMAT
                [DATATYPE = { STANDARD| DNA | RNA | NUCLEOTIDE I PROTEIN | CONTINUOUS} ]
                [RESPECTCASE]
                [MISSING=symbol]
                [ GAP=symbol]
                [ SYMBOLS = " symbol [symbol...]"]
                [ EQUATE = " symbol = entry [symbol = entry... ] " ]
                [MATCHCHAR= symbol ]
                [ [No] LABELS]
                [TRANSPOSE]
                [INTERLEAVE]
                [ITEMS=([MIN] [MAX] [MEDIAN] [AVERAGE] [VARIANCE] [STDERROR] [SAMPLESIZE] [STATES])]
                [STATESFORMAT= {STATESPRESENT | INDIVIDUALS | COUNT | FREQUENCY}.]
                [ [No] TOKENS]
            ;]
            [ELIMINATE character-set;]
            [TAXLABELS taxon-name [taxon-name ...];]
            [CHARSTATELABELS
                character-number [character-name] [/state-name [state-name...]]
                [, character-number [character-name] [/state-name [state-name...]]...]
            ;]
            [CHARLABELS character-name [character-name...];]
            [STATELABELS
                character-number [state-name [state-name ...]]
                    [, character-number [state-name [state-name...]]
                ...]
            ;]
            MATRIX data-matrix;
        END;

    DIMENSIONS, FORMAT, and ELIMINATE must all precede CHARLABELS, CHARSTATELABELS, STATELABELS,
    and MATRIX. DIMENSIONS must precede ELIMINATE. Only one of each command is allowed per block.
    """
    pass


class Data(Characters):
    """
    This block is equivalent to a CHARACTERS block in which the NEWTAXA subcommand is included in
    the DIMENSIONS command. That is, the DATA block is a CHARACTERS block that includes not only
    the definition of characters but also the definition of taxa.
    """
    pass
