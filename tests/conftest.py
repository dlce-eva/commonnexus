import os
import pathlib

import pytest

from commonnexus import Nexus


@pytest.fixture
def fixture_dir():
    return pathlib.Path(__file__).parent / 'fixtures'


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

    def iter_paths():
        for dirpath, dirnames, filenames in os.walk(str(dendropy_examples)):
            for fname in filenames:
                p = pathlib.Path(dirpath).joinpath(fname)
                try:
                    text = p.read_text(encoding='utf8')
                    if text[:100].lower().strip().startswith('#nexus'):
                        yield text
                except:
                    pass

    if "dendropyexample" in metafunc.fixturenames:
        metafunc.parametrize("dendropyexample", list(iter_paths()))
