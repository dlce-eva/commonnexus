import pytest

from commonnexus.tokenizer import *


@pytest.mark.parametrize(
    'text,ttype',
    [
        ("abcd", TokenType.WORD),
        ("'a b'", TokenType.QWORD),
        (" \t\n", TokenType.WHITESPACE),
        ('+', TokenType.PUNCTUATION),
        ("[a 'comment+]", TokenType.COMMENT),
    ]
)
def test_iter_tokens(text, ttype):
    tokens = list(iter_tokens(iter(text)))
    assert len(tokens) == 1 and tokens[0].type == ttype


@pytest.mark.parametrize(
    'text,words',
    [
        ("Bembidion\nB._zephyrum\n'John''s sparrow (eastern) '\n",
         ['Bembidion', 'B._zephyrum', "John's sparrow (eastern) "]),
        (r"[\\i]Bembidion_velox[\\p]_Linnaeus", ['Bembidion_velox_Linnaeus']),
        ("'B. zephyrum' ", [Word('B._zephyrum')]),
        ("aword 'the ''word'", ["aword", "the 'word"]),
    ]
)
def test_iter_words(text, words):
    assert [w for w in iter_words_and_punctuation(iter_tokens(iter(text)))] == words


def test_iter_words_2():
    assert [w for w in iter_words_and_punctuation(iter_tokens(iter('abc-def')), allow_punctuation_in_word='-')] == ['abc-def']


@pytest.mark.parametrize(
    'start,string,length,allow_single_word',
    [
        ('"', 'a b c"', 3, False),
        ('word', 'a b c"', 1, True),
        (None, '"a b c"', 3, False),
    ]
)
def test_iter_delimited(start, string, length, allow_single_word):
    res = list(iter_delimited(
        start,
        iter_words_and_punctuation(iter_tokens(iter(string))),
        allow_single_word=allow_single_word))
    assert len(res) == length
