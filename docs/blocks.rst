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


Mutability
----------

``Nexus`` objects are mutable, i.e. blocks can be added and removed during the "lifetime" of a
``Nexus`` instance. To make this possible, the only data kept in an instance is the list of tokens
representing the parsed NEXUS content. Thus, when accessing a block in a ``Nexus`` object, this
``Block`` instance is created from the token list, and, consequently, accessing a block again will
return a new instance:

.. code-block:: python

    >>> from commonnexus import Nexus
    >>> nex = Nexus('#NEXUS\nBEGIN BLOCK;\nEND;')
    >>> nex.BLOCK is nex.BLOCK
    False
    >>> id(nex.BLOCK)
    140138642078064
    >>> id(nex.BLOCK)
    140138642079584

Since blocks are ``tuple`` instances, they will still compare as expected, if they are created from
the same list of tokens, though:

.. code-block:: python

    >>> nex.BLOCK == nex.BLOCK
    True

But to take advantage of caching happening of block level (e.g. of TRANSLATE mappings in TREES a block),
care must be taken to retain a reference to the ``Block`` instance:

.. code-block:: python

    >>> nex = Nexus('#NEXUS\nBEGIN TREES;\nTRANSLATE a b, c d;\nTREE tree = (a,c);\nEND;')
    >>> trees = nex.TREES
    >>> trees.translate(trees.TREE).newick
    '(b,d)'


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
