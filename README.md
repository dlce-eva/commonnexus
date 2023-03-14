# commonnexus

[![Build Status](https://github.com/dlce-eva/commonnexus/workflows/tests/badge.svg)](https://github.com/dlce-eva/commonnexus/actions?query=workflow%3Atests)
[![Documentation Status](https://readthedocs.org/projects/commonnexus/badge/?version=latest)](https://commonnexus.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://badge.fury.io/py/commonnexus.svg)](https://pypi.org/project/commonnexus)

This package provides functionality to read and write the NEXUS file format as specified in

> Maddison, Swofford, and Maddison (1997). "NEXUS: An extensible file format for systematic information". Systematic Biology. 46 (4): 590–621. [doi:10.1093/sysbio/46.4.590](https://doi.org/10.1093/sysbio/46.4.590)

Rather than trying to rip out relevant portions of a NEXUS file as quickly as possible, the implementation
in `commonnexus` tries to do "the right thing" according to the specification, i.e. parse a file token by
token. Thus, we sacrifice speed for correctness and the ability to support weird edge cases like

> Comments do not break tokens. Thus, `AssuMP[comment]TiONS` is processed as `ASSUMPTIONS`.


## Install

Install `commonnexus` from [PyPI](https://pypi.org/project/commonnexus):
```shell
pip install commonnexus
```


## Overview

`commonnexus` provides a [Python API](#python-api) as well as a [shell command](#command-line-usage)
to manipulate (the data in) NEXUS files.

In particular, it allows reading NEXUS

```python
>>> from commonnexus import Nexus
>>> nex = Nexus.from_file('docs/characters.nex')
>>> nex.CHARACTERS.get_matrix()['t1'].values()
odict_values(['1', '0', '0', '1', '0', '1', '0', '0', '0', '0'])
```

and writing NEXUS

```python
>>> from commonnexus import Nexus
>>> from commonnexus.blocks import Data
>>> nex = Nexus.from_file('docs/characters.nex')
>>> print(Nexus.from_blocks(Data.from_data(nex.CHARACTERS.get_matrix())))
#NEXUS
BEGIN DATA;
	DIMENSIONS NCHAR=10;
	FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";
	MATRIX 
    t1 1001010000
    t2 0101000100
    t3 0011101010
    t4 0001100001
    t5 0001100001;
END;
```


## Command line usage

Installing the `commonnexus` package will also install a command line interface `commonnexus`, which provides several
sub-commands to manipulate NEXUS files.

Run `commonnexus -h` to get an overview of available sub-commands or find detailed documentation
with examples [on ReadTheDocs](https://commonnexus.readthedocs.io/en/latest/cli.html).


## Python API

The Python API tries to convert NEXUS constructs to appropriate Python objects, e.g.
- NEXUS content is a `list` of `Command` objects,
- missing states in a CHARACTERS MATRIX are conveyed as `None` values, etc.

This allows for dealing with NEXUS data in a way that is abstracted from the NEXUS formatting
conventions

For a detailed documentation of the Python API, refer to the
[docs on ReadTheDocs](https://commonnexus.readthedocs.io/en/latest/index.html).


## See also

- https://doi.org/10.1093/sysbio/46.4.590
- https://github.com/dlce-eva/python-nexus
- http://wiki.christophchamp.com/index.php?title=NEXUS_file_format
