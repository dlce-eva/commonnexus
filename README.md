# commonnexus

This package provides functionality to read and write the Nexus file format as specified in

> Maddison, Swofford, and Maddison (1997). "NEXUS: An extensible file format for systematic information". Systematic Biology. 46 (4): 590–621. [doi:10.1093/sysbio/46.4.590](https://doi.org/10.1093/sysbio/46.4.590)

Rather than trying to rip out relevant portions of a Nexus file as quickly as possible, the implementation
in `commonnexus` tries to do "the right thing" according to the specification, i.e. parse a file token by
token. Thus, we sacrifice speed for correctness and the ability to support weird edge cases like

> Comments do not break tokens. Thus, `AssuMP[comment]TiONS` is processed as `ASSUMPTIONS`.

