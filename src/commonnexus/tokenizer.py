import enum
import itertools
import dataclasses

__all__ = ['TokenType', 'Token', 'iter_tokens', 'get_name']

QUOTE = "'"
COMMENT = {'[': 1, ']': -1}
PUNCTUATION = r'(){}/\,;:=*"+-<>'
WHITESPACE = '\t\r\n '


class TokenType(enum.Enum):
    WORD = 1
    QWORD = 2
    COMMENT = 3
    PUNCTUATION = 4
    WHITESPACE = 5


@dataclasses.dataclass
class Token:
    """
    We parse Nexus in one pass, storing the data as list of tokens with enough
    information to extract relevant parts from this list later on.
    """
    __slots__ = ['text', 'type']
    text: str
    type: TokenType

    @classmethod
    def from_text(cls, tokens, type=None):
        return cls(
            text=''.join(tokens),
            type=type or (TokenType.WHITESPACE if tokens[-1] in WHITESPACE else TokenType.WORD))

    @property
    def is_semicolon(self):
        return self.type == TokenType.PUNCTUATION and self.text == ';'

    def __str__(self):
        if self.type == TokenType.COMMENT:
            return '[{}]'.format(self.text)
        if self.type == TokenType.QWORD:
            return "'{}'".format(self.text.replace("'", "''"))
        return self.text


def iter_tokens(s):
    token, lookahead = [], None

    while True:
        try:
            c = lookahead or next(s)
            lookahead = None

            if c == QUOTE:  # A quoted string.
                doublequote = False
                if token:
                    if token[-1] in WHITESPACE:
                        yield Token.from_text(token, TokenType.WHITESPACE)
                    else:
                        raise ValueError()  # pragma: no cover
                    token = []

                while 1:
                    c = lookahead or next(s)
                    lookahead = None
                    while c != QUOTE:
                        token.append(c)
                        c = next(s)

                    if doublequote:
                        token.append(c)
                        doublequote = False
                    else:
                        lookahead = next(s)
                        if lookahead == QUOTE:
                            doublequote = True
                        else:  # End of quoted string
                            yield Token.from_text(token, TokenType.QWORD)
                            token = []
                            break
                continue

            if c == '[':  # A comment.
                if token:
                    yield Token.from_text(token)
                    token = []
                commentlevel = 1
                while 1:
                    c = next(s)
                    while c not in COMMENT:
                        token.append(c)
                        c = next(s)
                    commentlevel += COMMENT[c]
                    if commentlevel == 0:
                        yield Token.from_text(token, TokenType.COMMENT)
                        token = []
                        break
                    else:
                        token.append(c)
                continue

            if c in WHITESPACE:
                if token and (token[-1] not in WHITESPACE):
                    yield Token.from_text(token, TokenType.WORD)
                    token = []
                token.append(c)
                continue

            if c in PUNCTUATION:
                if token:
                    yield Token.from_text(token)
                    token = []
                yield Token.from_text(c, TokenType.PUNCTUATION)
                continue

            if token and (token[-1] in WHITESPACE):
                yield Token.from_text(token, TokenType.WHITESPACE)
                token = []
            token.append(c)

        except StopIteration:
            break

    if token:
        yield Token.from_text(token)


def get_name(tokens):
    """
    The Nexus spec allows comments **in** block or command names. This function takes this into
    account when assembling a name from an iterable of tokens.
    """
    res = ''
    for t in itertools.dropwhile(lambda t: t.type != TokenType.WORD, tokens):
        if res:
            # We already encountered one word.
            if t.type == TokenType.WORD:
                res += t.text
            elif t.type != TokenType.COMMENT:
                break
        else:
            res += t.text
    return res.upper()
