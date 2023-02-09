import typing
import itertools
import collections

from ._compat import cached_property
from .tokenizer import TokenType, iter_tokens, Token, get_name
from commonnexus.blocks import Block

NEXUS = '#NEXUS'


class Command(tuple):
    """
    From the specification:

        A command is a collection of tokens terminated by a semicolon. Commands cannot contain
        semicolons, except as terminators, unless the semicolons are contained within a comment
        or within a quoted token consisting of more than one text character.
    """
    @cached_property
    def name(self):
        return get_name(self)

    @classmethod
    def from_name_and_payload(cls, name, payload=''):
        tokens = [Token('\n', TokenType.WHITESPACE)]
        name = list(iter_tokens(iter(name)))
        assert len(name) == 1 and name[0].type == TokenType.WORD
        tokens.extend(name)
        semicolons = 0
        if payload:
            tokens.append(Token(' ', TokenType.WHITESPACE))
            payload = list(iter_tokens(iter(payload)))
            semicolons = len([t for t in payload if t.is_semicolon])
            assert semicolons == 0 or (semicolons == 1 and payload[-1].is_semicolon)
            tokens.extend(payload)
        if semicolons == 0:
            tokens.append(Token(';', TokenType.PUNCTUATION))
        return cls(tokens)

    @property
    def is_beginblock(self):
        return self.name == 'BEGIN'

    @property
    def is_endblock(self):
        # In MacClade, PAUP, and COMPONENT, the ENDBLOCK command has been used as
        # a synonym of the END command.
        return self.name in ['END', 'ENDBLOCK']

    def iter_payload_tokens(self, type=None):
        found = False
        for t in itertools.dropwhile(
                lambda t: t.type != TokenType.WHITESPACE,
                itertools.dropwhile(lambda t: t.type == TokenType.WHITESPACE, self[:-1])):
            if not found and t.type == TokenType.WHITESPACE:
                # Drop the first whitespace token, too.
                continue
            found = True
            if type is None or (type == t.type):
                yield t

    #def payload(self, cls=Payload):
        #return cls(tuple(self.iter_payload_tokens()))


class Nexus(list):
    """
    A list of tokens with methods to access newick constituents.
    """
    def __init__(self,
                 s: typing.Optional[typing.Union[typing.Iterable, typing.List[Command]]] = None,
                 block_implementations=None):
        self.trailing_whitespace = []
        #
        # FIXME: We must recurse into subclasses of subclasses to get aliases such as Data for
        # Characters!
        #
        self.block_implementations = {cls.__name__.upper(): cls for cls in Block.__subclasses__()}
        self.block_implementations.update(block_implementations or {})
        s = s or NEXUS

        if isinstance(s, str):
            s = iter(s)

        if not isinstance(s, list):
            nexus, commands, tokens = False, [], []
            for token in itertools.dropwhile(
                    lambda t: t.type == TokenType.WHITESPACE, iter_tokens(s)):
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

    @classmethod
    def from_file(cls, p):
        with p.open(encoding='utf8') as f:
            return cls(itertools.chain.from_iterable(f))

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

    def append_block(self, name, cmds):
        all_commands = [Command.from_name_and_payload('BEGIN', name)]
        for n, payload in cmds:
            all_commands.append(Command.from_name_and_payload(n, payload))
        all_commands.append(Command.from_name_and_payload('END'))
        self.extend(all_commands)

    def replace_block(self, block, cmds):
        for i, cmd in enumerate(self):
            if cmd is block[0]:
                break
        else:
            raise ValueError('Block not found')
        for cmd in block[1:-1]:
            self.remove(cmd)
        for n, payload in reversed(cmds):
            self.insert(i + 1, Command.from_name_and_payload(n, payload))

    def append_command(self, block, name, payload=None):
        self.insert(self.index(block[-1]), Command.from_name_and_payload(name, payload))

    def __getattribute__(self, name):
        if name.isupper():
            try:
                return self.blocks[name][0]
            except IndexError:
                raise AttributeError('Nexus has no block {}'.format(name))
        return list.__getattribute__(self, name)
