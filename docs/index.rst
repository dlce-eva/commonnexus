.. commonnexus documentation master file, created by
   sphinx-quickstart on Wed Feb  8 13:32:30 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to commonnexus's documentation!
=======================================

``commonnexus`` presents an attempt to read and write files in the NEXUS file format specified in

   *Nexus: An Extensible File Format for Systematic Information*, Maddison et al. 1997, `DOI:10.1093/sysbio/46.4.590 <https://doi.org/10.1093/sysbio/46.4.590>`_

favouring correctness over speed. Thus, ``commonnexus`` supports somewhat esoteric features of
NEXUS such as comments **in** words (e.g. ``Assum[comment]pTIOns``), and most of the
:class:`FORMAT <commonnexus.blocks.characters.Format>` options for a
:class:`CHARACTERS <commonnexus.blocks.characters.Characters>`
:class:`MATRIX <commonnexus.blocks.characters.Matrix>`. This is possible, because parsing is based on
a proper tokenizer, rather than using regular expressions which typically require assumptions about
the format that are not warranted for generic NEXUS.

``commonnexus`` also supports "editing" of NEXUS files by adding, removing or replacing command-level
chunks. To do so in a minimally intrusive way - i.e. keeping the formatting of the rest of the file -
the tokenized full content of a NEXUS file is kept in memory, which again presents a trade-off that
should be kept in mind when deciding on suitability of ``commonnexus`` for a task.

Since all of the functionality in this package is informed by the specification, we often quote
the spec in documentation in the codebase, where it would be cumbersome to attribute the source
each time. Thus, if you use this package (or just its documentation), make sure to cite
`Maddison et al. 1997 <https://doi.org/10.1093/sysbio/46.4.590>`_


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   nexus
   blocks


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
