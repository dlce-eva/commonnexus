import itertools

from ._compat import cached_property
from .tokenizer import TokenType, iter_tokens, Token, get_name


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

    def __eq__(self, other):  # To make command removal in Nexus.replace_block work.
        return id(self) == id(other)

    @classmethod
    def from_name_and_payload(cls, name, payload='', comment=None):
        tokens = []
        if comment:
            tokens.extend([Token('\n', TokenType.WHITESPACE), Token(comment, TokenType.COMMENT)])
        tokens.append(Token('\n', TokenType.WHITESPACE))
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
                itertools.dropwhile(
                    lambda t: t.type in {TokenType.WHITESPACE, TokenType.COMMENT}, self[:-1])):
            if not found and t.type == TokenType.WHITESPACE:
                # Drop the first whitespace token, too.
                continue
            found = True
            if type is None or (type == t.type):
                yield t
