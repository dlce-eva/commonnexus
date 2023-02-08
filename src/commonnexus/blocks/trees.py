import types

from newick import Token, NewickString

from .base import Payload, Block
from commonnexus.tokenizer import TokenType
from commonnexus._compat import cached_property


class Tree(Payload):
    """
    Payload of the TREE command used in TREES blocks.
    """
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

    @cached_property
    def newick(self):
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
        return types.SimpleNamespace(string=''.join(ns), node=NewickString(nt).to_node())


class Trees(Block):
    __commands__ = {'TREE': Tree}
