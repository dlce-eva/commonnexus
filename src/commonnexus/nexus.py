import typing
import pathlib
import itertools
import collections

from .tokenizer import TokenType, iter_tokens, get_name, Word
from commonnexus.command import Command
from commonnexus.blocks import Block

__all__ = ['Config', 'Nexus']

NEXUS = '#NEXUS'


class Config:
    def __init__(self,
                 quote="'",
                 hyphenminus_is_text=False,
                 validate_newick=False,
                 encoding='utf8'):
        self.quote = quote
        self.hyphenminus_is_text = hyphenminus_is_text
        self.validate_newick=validate_newick
        self.encoding = encoding


class Nexus(list):
    """
    A list of tokens with methods to access newick constituents. From the spec:

        The tokens in a NEXUS file are organized into commands, which are in turn organized into
        blocks.

    This is reflected in the ``Nexus`` object. The ``Nexus`` object is just a ``list`` of
    :class:`Commands <Command>`, and has a property :meth:`Nexus.blocks` giving access to
    commands grouped by block:

    .. code-block::

        >>> nex = Nexus('#NEXUS BEGIN myblock; mycmd a b c; END;')
        >>> nex[0].__class__
        <class 'commonnexus.nexus.Command'>
        >>> len(nex.blocks['MYBLOCK'])
        1

    .. note::

        NEXUS is for the most part case-insensitive. ``commonnexus`` reflects this by giving all
        blocks and commands uppercase names. Thus, even if a command or block has a lowercase or
        mixed-case name in the file, the corresponding ``Command`` or ``Block`` object must be
        addressed using the uppercase name.
    """
    def __init__(self,
                 s: typing.Optional[typing.Union[typing.Iterable, typing.List[Command]]] = None,
                 block_implementations=None,
                 config=None):
        self.cfg = config or Config()
        self.trailing_whitespace = []
        #
        # FIXME: We must recurse into subclasses of subclasses to get aliases such as Data for
        # Characters!
        #
        self.block_implementations = {}
        for cls in Block.__subclasses__():
            self.block_implementations[cls.__name__.upper()] = cls
            for scls in cls.__subclasses__():
                self.block_implementations.setdefault(scls.__name__.upper(), scls)

        self.block_implementations.update(block_implementations or {})
        s = s or NEXUS

        if isinstance(s, str):
            s = iter(s)

        if not isinstance(s, list):
            nexus, commands, tokens = False, [], []
            for token in itertools.dropwhile(
                    lambda t: t.type == TokenType.WHITESPACE, iter_tokens(s, quote=self.cfg.quote)):
                if not nexus:
                    assert token.type == TokenType.WORD and token.text.upper() == NEXUS
                    nexus = True
                else:
                    tokens.append(token)
                    if token.is_semicolon:
                        commands.append(Command(tuple(tokens)))
                        tokens = []
            self.trailing_whitespace = tokens
            s = commands
        list.__init__(self, s)

    def word_as_nexus_string(self, word):
        return Word(word).as_nexus_string(self.cfg.quote)

    @classmethod
    def from_file(cls, p, config=None, **kw):
        config = config or Config(**kw)
        p = pathlib.Path(p)
        not_utf8 = False
        with p.open(encoding=config.encoding) as f:
            try:
                return cls(itertools.chain.from_iterable(f), config=config)
            except UnicodeDecodeError:
                not_utf8 = config.encoding == 'utf8'
        if not_utf8:
            # We don't want to do a lot of guessing, but if the default encoding was tried and
            # didn't work, we try with the old-time favourite "latin1":
            config.encoding = 'latin1'
            with p.open(encoding=config.encoding) as f:
                return cls(itertools.chain.from_iterable(f), config=config)

    def to_file(self, p):
        p = pathlib.Path(p)
        p.write_text(str(self), encoding=self.cfg.encoding)

    def __str__(self):
        return NEXUS \
            + ''.join(''.join(str(t) for t in cmd) for cmd in self) \
            + ''.join(str(t) for t in self.trailing_whitespace)

    def iter_comments(self):
        for cmd in self:
            yield from (t for t in cmd if t.type == TokenType.COMMENT)

    @property
    def comments(self):
        return list(self.iter_comments())

    def iter_blocks(self):
        block = None
        for command in itertools.dropwhile(lambda c: not c.is_beginblock, self):
            if command.is_endblock:
                block.append(command)
                # Look up a suitable Block implementation.
                name = get_name(block[0].iter_payload_tokens())
                yield self.block_implementations.get(name, Block)(self, block)
                block = None
            elif command.is_beginblock:
                block = [command]
            elif block is not None:
                block.append(command)

    def validate(self, log=None):
        valid = True
        for block in self.iter_blocks():
            #
            # FIXME: we can do a lot of validation here! If block.__commands__ is a list, there is
            # some fixed order between commands.
            # If Payload.__multivalued__ == False, only one command instance is allowed, ...
            #
            valid = valid and block.validate(log=log)
        return valid

    @property
    def blocks(self):
        res = collections.defaultdict(list)
        for block in self.iter_blocks():
            res[block.name].append(block)
        return res

    def remove_block(self, block):
        for cmd in block:
            self.remove(cmd)

    def append_block(self, block):
        block.nexus = self
        self.extend(block)

    def replace_block(self, block, cmds):
        for i, cmd in enumerate(self):
            if cmd is block[0]:
                break
        else:
            raise ValueError('Block not found')  # pragma: no cover
        for cmd in block[1:-1]:
            self.remove(cmd)
        for n, payload in reversed(cmds):
            self.insert(i + 1, Command.from_name_and_payload(n, payload, quote=self.cfg.quote))

    def append_command(self, block, name, payload=None):
        self.insert(
            self.index(block[-1]),
            Command.from_name_and_payload(name, payload, quote=self.cfg.quote))

    def __getattribute__(self, name):
        """
        NEXUS does not make any prescriptions regarding how many blocks with the same name may
        exist in a file. Thus, the primary way to access blocks is by looking up the list of blocks
        for a given name in :meth:`Nexus.blocks <Nexus.blocks>`. If it can be assumed that just one
        block for a name exists, or only the first block with that name is of interest, this block
        can also be accessed as `Nexus.<BLOCK_NAME>`, i.e. using the uppercase block name as
        attribute of the `Nexus` instance.

        :param name:
        :return:
        """
        if name.isupper():
            try:
                return self.blocks[name][0]
            except IndexError:
                return None
        return list.__getattribute__(self, name)
