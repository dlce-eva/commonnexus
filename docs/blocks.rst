Blocks
======

From the specification:

    Modularity is the primary design feature of a NEXUS file. A NEXUS file is composed of a number
    of blocks, such as TAXA, CHARACTERS, and TREES blocks.

    Other blocks can be added to the file to house various kinds of data, including discrete and
    continuous morphological characters, distance data, frequency data, and information about
    protein-coding regions, genetic codes, assumptions about weights, trees, etc. Images can be
    included. This modular format allows a computer program reading the file to ignore safely the
    unfamiliar parts of the file, permits sharing of the file by various programs, and permits
    future expansion to encompass new information.

    The eight [sic] primary public blocks are TAXA, CHARACTERS, UNALIGNED, DISTANCES, SETS,
    ASSUMPTIONS, CODONS, TREES, and NOTES.


TAXA
----

.. autoclass:: commonnexus.blocks.taxa.Taxa
    :members:


TAXA Commands
~~~~~~~~~~~~~

.. automodule:: commonnexus.blocks.taxa
    :members:
    :exclude-members: Taxa


CHARACTERS (and DATA)
---------------------

.. autoclass:: commonnexus.blocks.characters.Characters
    :members:

.. autoclass:: commonnexus.blocks.characters.Data
    :members:


CHARACTERS Commands
~~~~~~~~~~~~~~~~~~~

.. automodule:: commonnexus.blocks.characters
    :members:
    :exclude-members: Characters, Data


UNALIGNED [not supported]
-------------------------

.. autoclass:: commonnexus.blocks.unaligned.Unaligned


DISTANCES
---------

.. autoclass:: commonnexus.blocks.distances.Distances
    :members:


DISTANCES Commands
~~~~~~~~~~~~~~~~~~

.. automodule:: commonnexus.blocks.distances
    :members:
    :exclude-members: Distances


SETS
----

.. autoclass:: commonnexus.blocks.sets.Sets
    :members:


SETS Commands
~~~~~~~~~~~~~

.. automodule:: commonnexus.blocks.sets
    :members:
    :exclude-members: Sets


ASSUMPTIONS [not supported]
---------------------------

.. autoclass:: commonnexus.blocks.assumptions.Assumptions
    :members:


CODONS [not supported]
----------------------

.. autoclass:: commonnexus.blocks.codons.Codons


TREES
-----

.. autoclass:: commonnexus.blocks.trees.Trees
    :members:


TREES Commands
~~~~~~~~~~~~~~

.. automodule:: commonnexus.blocks.trees
    :members:
    :exclude-members: Trees


NOTES
-----

.. autoclass:: commonnexus.blocks.notes.Notes
    :members:


NOTES Commands
~~~~~~~~~~~~~~

.. automodule:: commonnexus.blocks.notes
    :members:
    :exclude-members: Notes
