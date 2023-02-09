import typing
import collections

from newick import Token, NewickString, Node

from .base import Payload, Block
from commonnexus.tokenizer import TokenType, iter_words_and_punctuation


class Translate(Payload):
    """
    The tree description requires references to the taxa defined in a TAXA, DATA,
    CHARACTERS, UNALIGNED, or DISTANCES block. These references can be made using the label assigned
    to them in the TAXA or DATA blocks, their numbers, or a token specified in the TRANSLATE command.
    The TRANSLATE statement maps arbitrary labels in the tree specification to valid taxon names.
    If the arbitrary labels are integers, they are mapped onto the valid taxon names as dictated by
    the TRANSLATE command without any consideration of the order of the taxa in the matrix. Thus,
    if an integer is encountered in the tree description, a program first checks to see if
    it matches one of the arbitrary labels defined in the TRANSLATE command; only if
    no matching label is found will the integer be presumed to refer to the taxon in that
    position in the matrix (e.g., if the label in the description is 15, but this is not a label
    defined in the TRANSLATE command, a program should take this to refer to the 15th taxon).

    In the following example,

    .. code-block::

        BEGIN TAXA;
            TAXLABELS Scarabaeus Drosophila Aranaeus;
        END;
        BEGIN TREES;
            TRANSLATE beetle Scarabaeus, fly Drosophila, spider Aranaeus;
            TREE tree1 = ((1,2),3);
            TREE tree2 = ((beetle,fly),spider);
            TREE tree3= ((Scarabaeus,Drosophila),Aranaeus);
        END;

    the TRANSLATE command specifies that the label "beetle" can be used in the tree description to
    refer to Scarabaeus, "fly" to Drosophila, and "spider" to Aranaeus. This means that Scarabaeus
    can be referred to in a tree description as 1, Scarabaeus, or beetle. Thus, the three trees are
    identical.

    :ivar typing.Dict[str, str] mapping: The mapping of tokens used in the tree description to \
    valid taxon names.
    """
    def __init__(self, tokens):
        super().__init__(tokens)
        # get a word, and another word, then look for comma.
        self.mapping = collections.OrderedDict()
        key, value = None, None
        for t in iter_words_and_punctuation(tokens):
            if not key:
                assert isinstance(t, str)
                key = t
                continue
            if not value:
                assert isinstance(t, str)
                value = t
                continue
            assert t.is_punctuation and t.text == ','
            self.mapping[key] = value
            key, value = None, None
        if key and value:
            self.mapping[key] = value


class Tree(Payload):
    """
    This command describes a tree. Tree descriptions are standard object definition commands.
    They use the familiar parenthesis notation, with node names, branch lengths, and comments
    following the established Newick tree standard (see Felsenstein, 1993).

    The label of the node is a NEXUS token that is a taxon's defined name, a taxon's
    number, a taxon's label from the translation table, or a clade's defined name. The
    label is optional for internal nodes that are not observed taxa; it is not optional for
    terminal nodes. Internal nodes that have no label are represented implicitly by the parentheses
    containing the list of subclades. If the name of a TAXSET is used, it is interpreted as a list
    of the terminal taxa defined to be in the TAXSET (with commas
    implicitly inserted between the taxa). The length of the branch below the node
    is a number, positive or negative. Rooted and unrooted trees can be spec-
    ified using the [&R] and [&U] comments at the start of the tree description. For example,

    .. code-block::

        TREE mytree = [&R] ((1,2),(3,4));

    is a rooted tree, whereas

    .. code-block::

        TREE mytree = [&U] ((1,2),(3,4));

    is an unrooted tree. The NEXUS standard does not specify whether rooted or unrooted is default.

    An example tree with branch lengths is

    .. code-block::

        TREE tree4 = ((beetle:4.3,fly:1.1):1.8,spider:2.5);

    If a file (and its data matrix) has four defined taxa, Crocodile, Bluebird, Archaeopteryx, and
    Rattlesnake, the following tree,

    .. code-block::

        TREE tree4= (((Bluebird)Archaeopteryx,Crocodile)Archosauria,Rattlesnake);

    would indicate that the taxon Archaeopteryx is ancestral to Bluebird and that Crocodile
    is their sister. Archosauria, because it does not refer to a taxon that has been defined
    in a TAXA or DATA block, is interpreted as the name of the clade including Archaeopteryx,
    Bluebird, and Crocodile. Any additional information about a clade, its ancestral node, or the
    branch below it is to be placed in NEXUS comment commands associated with the node. Al-
    though different programs may choose their own conventions for how to embed
    information in comments, the comments that begin with &N are reserved for future
    NEXUS comment commands. The NEXUS standard places no restrictions on the number of taxa
    contained in each tree.

    :ivar str name: The name of the tree.
    :ivar typing.Union[bool, None] rooted: Flag indicating whether the tree is rooted (or `None` \
    if no information is given)
    :ivar str newick_string: The tree description formatted as Newick string.
    :ivar newick.Node newick_node: The tree description as `newick.Node`.
    """
    __multivalued__ = True

    def __init__(self, tokens):
        super().__init__(tokens)
        # We parse tree name and rooting information right away.
        self.name, e, self._rooted, nwk = None, False, None, False

        tokens = iter(tokens)
        while not self.name:
            t = next(tokens)
            if t.type == TokenType.WORD:
                self.name = t.text

        while not e:
            t = next(tokens)
            if t.type == TokenType.WORD:
                self.name += t.text
            if t.type == TokenType.PUNCTUATION:
                if t.text == '=':
                    e = True
                else:
                    self.name += t.text

        while not nwk:
            t = next(tokens)
            if t.type == TokenType.COMMENT and t.text.startswith('&'):
                self._rooted = t.text
            if t.type == TokenType.PUNCTUATION and t.text == '(':
                nwk = True
        assert nwk
        self._remaining_tokens = tokens
        self._ns = None
        self._nn = None

    @property
    def rooted(self):
        if self._rooted:
            return self._rooted == '&R'

    @property
    def newick_string(self):
        if not self._ns:
            self._parse_newick()
        return self._ns

    @property
    def newick_node(self):
        if not self._nn:
            self._parse_newick()
        return self._nn

    def _parse_newick(self):
        # Read newick string and `newick.Node` object lazily.
        ns, l = ['('], 1
        nt = [Token('(', False, 0, 0, True, False, False, False)]

        for token in self._remaining_tokens:
            # now we assemble newick string and newick tokens in one go.
            if token.type == TokenType.WORD:
                ns.append(token.text)
                nt.extend([Token(c, False, 0, l, True, False, False, False) for c in token.text])
            elif token.type == TokenType.PUNCTUATION:
                ns.append(token.text)
                if token.text == ')':
                    l -= 1
                nt.append(Token(token.text, False, 0, l, True,
                                token.text == ',', token.text == ':', False))
                if token.text == '(':
                    l += 1
            elif token.type == TokenType.COMMENT:
                nt.append(Token('[', False, 1, l, False, False, False, False))
                for c in token.text:
                    nt.append(Token(c, False, 1, l, False, False, False, False))
                nt.append(Token(']', False, 1, l, False, False, False, False))
            elif token.type == TokenType.QWORD:
                nt.append(Token("'", True, 0, l, False, False, False, False))
                for c in token.text:
                    if c == "'":
                        nt.append(Token("'", True, 0, l, False, False, False, False))
                    nt.append(Token(c, True, 0, l, False, False, False, False))
                nt.append(Token(']', True, 0, l, False, False, False, False))
        self._ns = ''.join(ns)
        self._nn = NewickString(nt).to_node()


class Trees(Block):
    """
    This block stores information about trees. The syntax for the TREES block is

    .. code-block::

        BEGIN TREES;
            [TRANSLATE arbitrary-token-used-in-tree-description valid-taxon-name
                [, arbitrary-token-used-in-tree-description valid-taxon-name...];]
            [TREE [*] tree-name= tree-specification;]
        END;

    A :class:`TRANSLATE <Translate>` command, if present, must precede any
    :class:`TREE <Tree>` command.
    """
    __commands__ = [Translate, Tree]

    def validate(self, log=None):
        super().validate(log=log)
        valid, with_translate, tree_seen = True, False, False
        for i, cmd in enumerate(self[1:-1]):
            if cmd.name not in self.payload_map:
                if log:
                    log.error('Invalid command for {} block: {}'.format(self.name, cmd.name))
                valid = False
            if cmd.name == 'TRANSLATE':
                if with_translate:
                    log.error('Duplicate TRANSLATE command')
                    valid = False
                elif tree_seen:
                    log.warning('TRANSLATE command **after** TREE command')
                    valid = False
                else:
                    with_translate = True
            else:
                tree_seen = True
        return valid

    def translated(self, tree: typing.Union[Tree, Node]) -> Node:
        mapping = {}
        if 'TRANSLATE' in self.commands:
            mapping.update(self.TRANSLATE.mapping)
        if 'TAXA' in self.nexus.blocks and 'TAXLABELS' in self.nexus.TAXA.commands:
            mapping.update({str(k): v for k, v in self.nexus.TAXA.TAXLABELS.labels.items()})

        def rename(n):
            if n.name in mapping:
                n.name = mapping[n.name]

        node = tree.newick_node if isinstance(tree, Tree) else tree
        node.visit(rename)
        return node
