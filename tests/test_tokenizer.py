import pytest

from commonnexus.tokenizer import *


@pytest.mark.parametrize(
    'text,words',
    [
        ("Bembidion\nB._zephyrum\n'John''s sparrow (eastern) '\n",
         ['Bembidion', 'B._zephyrum', "John's sparrow (eastern) "]),
        (r"[\\i]Bembidion_velox[\\p]_Linnaeus", ['Bembidion_velox_Linnaeus']),
        ("'B. zephyrum' ", [Word('B._zephyrum')]),
    ]
)
def test_iter_words(text, words):
    assert [w for w in iter_words_and_punctuation(iter_tokens(iter(text)))] == words


def test_iter_words_2():
    assert [w for w in iter_words_and_punctuation(iter_tokens(iter('abc-def')), allow_punctuation_in_word='-')] == ['abc-def']
