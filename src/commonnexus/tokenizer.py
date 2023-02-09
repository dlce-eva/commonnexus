"""

Punctuation
~~~~~~~~~~~

    Any of the following text characters are considered punctuation at some times:

    ..code-block::

        ( ) [ ] { } / \\ , ; : = * ' " " + - < >

    The following punctuation marks have special properties: [ ] do not break a
    word; + and - are allowed as state symbols, but none of the rest are allowed; - is
    considered punctuation except were it is the minus sign in a negative number.
"""
import enum
import itertools
import dataclasses

__all__ = ['TokenType', 'Token', 'iter_tokens', 'get_name', 'iter_words_and_punctuation', 'Word']

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

    @property
    def is_whitespace(self):
        return self.type == TokenType.WHITESPACE

    @property
    def is_comment(self):
        return self.type == TokenType.COMMENT

    @property
    def is_punctuation(self):
        return self.type == TokenType.PUNCTUATION

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


class Word(str):
    def __eq__(self, other):
        return self.replace(' ', '_') == other.replace(' ', '_')

    def __hash__(self):
        return hash(str(self))


def iter_words_and_punctuation(tokens, allow_punctuation_in_word=None):
    """
    Word

    From the spec:

        Except for special cases involving quotes or comments, a NEXUS word is any string of text
        characters that is bounded by whitespace or punctuation and that does not contain
        whitespace or punctuation. If the first character of a word is a single quote, then
        the word ends with the next single quote (unless that single quote is in a pair of
        consecutive single quotes; if so, then the word ends at the first unpaired single quote).
        Any character, including punctuation and whitespace, may be contained within a quoted word.
        A word cannot consist of only whitespace and punctuation. On each of the following lines
        is a single legal word:

        .. code-block::

            Bembidion
            B._zephyrum
            'John''s sparrow (eastern) '

        Underscores are considered equivalent to blank spaces, except that underscores are dark
        characters and blank spaces are whitespace. Thus, a program encountering "B._zephyrum" and
        "'B. zephyrum'" should judge them to be identical.  Any doubled single quotes within a
        quoted word should be converted to single quotes within the program. Thus, 'John''s' would
        be treated internally within a program as John's. Of course, if the program writes out
        such a word to a NEXUS file, the quote should be redoubled, and quotes should be written
        around the word: 'John' 's.
        A string of dark characters is broken into several words by whitespace and any punctuation
        other than brackets, unless the string is surrounded by quotes.
        Thus, "[\\i]Bembidion_velox[\\p]_Linnaeus" consists of one word, as does
        '- - A single word', whereas "two()words" consists of four tokens: the word "two",
        two punctuation characters, and the word "words".
    """
    allow_punctuation_in_word = allow_punctuation_in_word or ''
    word = ''
    for i, token in enumerate(tokens):
        if token.type == TokenType.QWORD:
            if word:
                yield Word(word)
                word = ''
            yield token.text
        elif token.type == TokenType.WORD:
            word += token.text
        elif token.is_whitespace:
            if word:
                yield Word(word)
                word = ''
        elif token.is_punctuation:
            if token.text in allow_punctuation_in_word:
                word += token.text
            else:
                if word:
                    yield Word(word)
                    word = ''
                yield token
    if word:
        yield Word(word)
