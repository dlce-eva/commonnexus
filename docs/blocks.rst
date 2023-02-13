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

    The eight primary public blocks are TAXA, CHARACTERS, UNALIGNED, DISTANCES, SETS, ASSUMPTIONS,
    CODONS, TREES, and NOTES.


Characters
----------

.. autoclass:: commonnexus.blocks.characters.Characters
    :members:

.. automodule:: commonnexus.blocks.characters
    :members:
    :exclude-members: Characters, Data


Taxa
----

.. autoclass:: commonnexus.blocks.taxa.Taxa
    :members:

.. automodule:: commonnexus.blocks.taxa
    :members:
    :exclude-members: Taxa


Trees
-----

.. autoclass:: commonnexus.blocks.trees.Trees
    :members:

.. automodule:: commonnexus.blocks.trees
    :members:
    :exclude-members: Trees


Distances
---------

.. autoclass:: commonnexus.blocks.distances.Distances
    :members:

.. automodule:: commonnexus.blocks.distances
    :members:
    :exclude-members: Distances


Notes
-----

.. autoclass:: commonnexus.blocks.notes.Notes
    :members:

.. automodule:: commonnexus.blocks.notes
    :members:
    :exclude-members: Notes
