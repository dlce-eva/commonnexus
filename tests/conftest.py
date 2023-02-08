import pathlib

import pytest


@pytest.fixture
def fixture_dir():
    return pathlib.Path(__file__).parent / 'fixtures'
