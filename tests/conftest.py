import os
import pathlib

import pytest

from commonnexus import Nexus


@pytest.fixture
def fixture_dir():
    return pathlib.Path(__file__).parent / 'fixtures'


@pytest.fixture
def morphobank(fixture_dir):
    return fixture_dir / 'regression' / 'mbank_X962_11-22-2013_1534.nex'


@pytest.fixture
def nexus():
    def make_one(**blocks):
        cfg = blocks.pop('config', None)
        block = lambda name, text: 'BEGIN {};\n{}\nEND;'.format(name, text)
        return Nexus(
            '#nexus\n{}'.format('\n'.join(block(n, t) for n, t in blocks.items())),
            config=cfg)
    return make_one


def pytest_generate_tests(metafunc):
    dendropy_examples = pathlib.Path(__file__).parent / 'fixtures' / 'dendropy' / 'tests' / 'data'

    xfail = [
        'standard-test-chars-protein.matchchar.nexus',  # Is X an equate symbol for DATATYPE=PROTEIN?
        'standard-test-chars-protein.interleaved.nexus',  # Is X an equate symbol for DATATYPE=PROTEIN?
        'standard-test-chars-protein.simple.nexus',  # same
        'standard-test-chars-protein.basic.nexus',  # same
        'caenophidia_mos.chars.nexus',  # same
    ]

    def iter_paths():
        for dirpath, dirnames, filenames in os.walk(str(dendropy_examples)):
            for fname in filenames:
                p = pathlib.Path(dirpath).joinpath(fname)
                try:
                    text = p.read_text(encoding='utf8')
                    if text[:100].lower().strip().startswith('#nexus'):
                        yield pytest.param(text, marks=pytest.mark.xfail) if p.name in xfail else text
                except:
                    pass

    if "dendropyexample" in metafunc.fixturenames:
        metafunc.parametrize("dendropyexample", list(iter_paths()))
