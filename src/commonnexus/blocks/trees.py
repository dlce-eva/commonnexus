import typing
import warnings
import collections

import newick

from .base import Payload, Block
from commonnexus.util import log_or_raise
from commonnexus.tokenizer import TokenType, iter_words_and_punctuation, Word


class Translate(Payload):
    """
    The tree description requires references to the taxa defined in a TAXA, DATA,
    CHARACTERS, UNALIGNED, or DISTANCES block. These references can be made using the label assigned
    to them in the TAXA or DATA blocks, their numbers, or a token specified in the TRANSLATE
    command. The TRANSLATE statement maps arbitrary labels in the tree specification to valid taxon
    names. If the arbitrary labels are integers, they are mapped onto the valid taxon names as
    dictated by the TRANSLATE command without any consideration of the order of the taxa in the
    matrix. Thus, if an integer is encountered in the tree description, a program first checks to
    see if it matches one of the arbitrary labels defined in the TRANSLATE command; only if
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

    .. note::

        The ``TRANSLATE`` data is typically not accessed directly, but just used implicitly when
        calling :meth:`Trees.translate`.
    """
    def __init__(self, tokens, nexus=None):
        super().__init__(tokens, nexus=nexus)
        # get a word, and another word, then look for comma.
        self.mapping = collections.OrderedDict()
        key, value = None, None
        for t in iter_words_and_punctuation(self._tokens, nexus=nexus):
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

    The label of the node is a NEXUS token that is a taxon's defined name, a taxon's number, a
    taxon's label from the translation table, or a clade's defined name. The label is optional for
    internal nodes that are not observed taxa; it is not optional for terminal nodes. Internal
    nodes that have no label are represented implicitly by the parentheses containing the list of
    subclades. If the name of a TAXSET is used, it is interpreted as a list of the terminal taxa
    defined to be in the TAXSET (with commas implicitly inserted between the taxa). The length of
    the branch below the node is a number, positive or negative. Rooted and unrooted trees can be
    specified using the [&R] and [&U] comments at the start of the tree description. For example,

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
    :ivar newick.Node newick: The tree description as `newick.Node`.

    .. code-block:: python

        >>> tree = Tree('tree4= (((Bluebird)Archaeopteryx,Crocodile)Archosauria,Rattlesnake)')
        >>> tree.name
        'tree4'
        >>> print(tree.newick.ascii_art())
                                        ┌─Archaeopteryx ──Bluebird
                        ┌─Archosauria───┤
        ────────────────┤               └─Crocodile
                        └─Rattlesnake
    """
    __multivalued__ = True

    def __init__(self, tokens, nexus=None):
        super().__init__(tokens, nexus=nexus)
        # We parse tree name and rooting information right away.
        self.name, ncomplete, e, self._rooted, nwk = None, False, False, None, False

        tokens = iter(self._tokens)
        while not self.name:
            t = next(tokens)
            if t.type in {TokenType.WORD, TokenType.QWORD}:
                self.name = t.text
                if t.type == TokenType.QWORD:
                    ncomplete = True

        while not e:
            t = next(tokens)
            if t.type == TokenType.WORD:
                assert not ncomplete, 'Stuff between tree name and ='
                self.name += t.text
            if t.type == TokenType.PUNCTUATION:
                if t.text == '=':
                    e = True
                else:
                    assert not ncomplete, 'Stuff between tree name and ='
                    self.name += t.text  # FIXME: Should we append punctuation to tree names?

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

    @staticmethod
    def format(name: str,
               newick_node: newick.Node,
               rooted: typing.Optional[bool] = None) -> str:
        """
        Returns a representation of a tree as NEXUS string, suitable as payload of a ``TREE``
        command.
        """
        return '{} = {}{}'.format(
            Word(name).as_nexus_string(),
            '' if rooted is None else '[&{}] '.format('R' if rooted else 'U'),
            newick_node.newick)

    @property
    def rooted(self):
        if self._rooted:
            return self._rooted == '&R'

    @property
    def newick(self):
        if not self._nn:
            self._nn = self._parse_newick()
        return self._nn

    def _parse_newick(self):
        # Read newick string and `newick.Node` object lazily.
        if self.nexus and self.nexus.cfg.validate_newick:
            # More correct, but slower: Let the newick parser validate the data.
            return newick.loads('(' + ''.join(str(t) for t in self._remaining_tokens))[0]
        # Quicker but by-passes some validation: Instantiate NewickString from pre-parsed Nexus
        # tokens!
        nt = [newick.Token('(', newick.TokenType.OBRACE, 0)]
        word, level = [], 1

        for token in self._remaining_tokens:
            # now we assemble newick string and newick tokens in one go.
            if token.type == TokenType.WORD:
                word.append(token.text)
            elif token.type == TokenType.PUNCTUATION:
                if token.text in newick.RESERVED_PUNCTUATION:
                    # delimits words!
                    if word:
                        nt.append(newick.Token(''.join(word), newick.TokenType.WORD, level))
                        word = []
                    if token.text == ')':
                        level -= 1
                    nt.append(
                        newick.Token(token.text, newick.RESERVED_PUNCTUATION[token.text], level))
                    if token.text == '(':
                        level += 1
                else:
                    word.append(token.text)
            elif token.type == TokenType.COMMENT:
                if word:
                    nt.append(newick.Token(''.join(word), newick.TokenType.WORD, level))
                    word = []
                nt.append(newick.Token('[' + token.text + ']', newick.TokenType.COMMENT, level))
            elif token.type == TokenType.QWORD:
                assert not word  # As in NEXUS, a newick QWORD can not follow a WORD.
                nt.append(
                    newick.Token(Word(token.text).as_nexus_string(), newick.TokenType.QWORD, level))
        if word:
            nt.append(newick.Token(''.join(word), newick.TokenType.WORD, level))
        return newick.NewickString(nt).to_node()


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
            if cmd.name not in self.payload_map:  # pragma: no cover
                valid = log_or_raise(
                    'Invalid command for {} block: {}'.format(self.name, cmd.name), log=log)
            if cmd.name == 'TRANSLATE':
                if with_translate:  # pragma: no cover
                    valid = log_or_raise('Duplicate TRANSLATE command', log=log)
                elif tree_seen:  # pragma: no cover
                    valid = log_or_raise(
                        'TRANSLATE command **after** TREE command', log=log, level='warning')
                else:
                    with_translate = True
            else:
                tree_seen = True
        return valid

    def translate(self, tree: typing.Union[Tree, newick.Node]) -> newick.Node:
        """

        :param tree:
        :return: A Newick node where the node labels have been translated to valid taxon labels.

        .. note::

            Translating a tree does **not** change tree's representation in the containing
            ``Nexus`` instance. To replace un-translated trees in a NEXUS file with translated
            ones, the following code would work:

            .. code-block:: python

                >>> untranslated = Nexus.from_file(path)
                >>> trees = []
                >>> for tree in untranslated.TREES.commands['TREE']:
                ...     trees.append(Tree.format(
                ...         tree.name,
                ...         untranslated.TREES.translate(tree).newick,
                ...         rooted=tree.rooted))
                >>> untranslated.replace_block(
                ...     untranslated.TREES, [('TREE', tree) for tree in trees])
                >>> path.write_text(str(untranslated))
        """
        mapping = {}
        if 'TRANSLATE' in self.commands:
            mapping.update(self.TRANSLATE.mapping)
        if 'TAXA' in self.linked_blocks:
            mapping.update({
                str(k): v for k, v in self.linked_blocks['TAXA'].TAXLABELS.labels.items()})
        elif self.nexus.TAXA and self.nexus.TAXA.TAXLABELS:
            mapping.update({str(k): v for k, v in self.nexus.TAXA.TAXLABELS.labels.items()})
        taxa = set(mapping.values())

        def rename(n):
            if n.name:
                if n.name in mapping:
                    n.name = mapping[n.name]
                elif n.name not in taxa:
                    warnings.warn('un-translatable tree node: {}'.format(n.name))

        node = tree.newick if isinstance(tree, Tree) else tree
        node.visit(rename)
        return node

    @classmethod
    def from_data(cls,
                  *tree_specs,
                  **translate_labels) -> 'Trees':
        TITLE = translate_labels.pop('TITLE', None)
        LINK = translate_labels.pop('LINK', None)
        ID = translate_labels.pop('ID', None)
        nexus = translate_labels.pop('nexus', None)
        cmds = []
        detranslate = {v: k for k, v in translate_labels.items()}

        def rename(n):
            if n.name in detranslate:
                n.name = detranslate[n.name]

        if translate_labels:
            cmds.append((
                'TRANSLATE',
                ',\n'.join('{} {}'.format(
                    Word(k).as_nexus_string(),
                    Word(v).as_nexus_string())
                    for k, v in sorted(translate_labels.items()))
            ))
        for name, nwk, rooted in tree_specs:
            if isinstance(nwk, str):
                nwk = newick.loads(nwk)[0]
            if translate_labels:
                nwk.visit(rename)
            cmds.append(('TREE', Tree.format(name, nwk, rooted)))
        return cls.from_commands(cmds, nexus=nexus, TITLE=TITLE, LINK=LINK, ID=ID)
