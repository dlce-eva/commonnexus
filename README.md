# commonnexus

[![Build Status](https://github.com/dlce-eva/commonnexus/workflows/tests/badge.svg)](https://github.com/dlce-eva/commonnexus/actions?query=workflow%3Atests)
[![Documentation Status](https://readthedocs.org/projects/commonnexus/badge/?version=latest)](https://commonnexus.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://badge.fury.io/py/commonnexus.svg)](https://pypi.org/project/commonnexus)

This package provides functionality to read and write the Nexus file format as specified in

> Maddison, Swofford, and Maddison (1997). "NEXUS: An extensible file format for systematic information". Systematic Biology. 46 (4): 590–621. [doi:10.1093/sysbio/46.4.590](https://doi.org/10.1093/sysbio/46.4.590)

Rather than trying to rip out relevant portions of a Nexus file as quickly as possible, the implementation
in `commonnexus` tries to do "the right thing" according to the specification, i.e. parse a file token by
token. Thus, we sacrifice speed for correctness and the ability to support weird edge cases like

> Comments do not break tokens. Thus, `AssuMP[comment]TiONS` is processed as `ASSUMPTIONS`.



## Install

Install `commonnexus` from [PyPI](https://pypi.org/project/commonnexus):
```shell
pip install commonnexus
```


## Command line usage

Installing the `commonnexus` package will also install a command line interface `commonnexus`, which provides several
sub-commands to manipulate NEXUS files.

Run `commonnexus -h` to get an overview of available sub-commands.


## Python API

For a detailed documentation of the Python API, refer to the
[docs on ReadTheDocs](https://commonnexus.readthedocs.io/en/latest/index.html).


## See also

- https://doi.org/10.1093/sysbio/46.4.590
- https://github.com/dlce-eva/python-nexus
- http://wiki.christophchamp.com/index.php?title=NEXUS_file_format
