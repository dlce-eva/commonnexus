import pathlib

import pytest

from commonnexus import Nexus


@pytest.fixture
def fixture_dir():
    return pathlib.Path(__file__).parent / 'fixtures'


@pytest.fixture
def nexus():
    def make_one(**blocks):
        block = lambda name, text: 'BEGIN {};\n{}\nEND;'.format(name, text)
        return Nexus('#nexus\n{}'.format('\n'.join(block(n, t) for n, t in blocks.items())))
    return make_one
