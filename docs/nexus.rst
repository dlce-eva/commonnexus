NEXUS Files
===========


Reading NEXUS data
------------------

Since NEXUS is an *Extensible File Format*, it's natural habitat is the file system. Thus, to
instantiate a :class:`Nexus <commonnexus.nexus.Nexus>` object, we typically read a file to access
NEXUS data:

.. code-block:: python

    >>> from commonnexus import Nexus
    >>> nex = Nexus.from_file('tests/fixtures/ape_random.trees')
    >>> for name in nex.blocks:
    ...     print(name)
    ...
    TAXA
    TREES


.. autoclass:: commonnexus.nexus.Config
    :members:

.. autoclass:: commonnexus.nexus.Nexus
    :members:
    :special-members:


Writing NEXUS data
------------------

`commonnexus` provides functionality to write NEXUS by manipulating :class:`commonnexus.nexus.Nexus`
objects, which can then be written to a file.

.. code-block:: python

    >>> nex = Nexus()
    >>> nex.to_file('test.nex')

will write a minimal NEXUS file containing just the text ``#NEXUS``.

Since blocks are the somewhat self-contained units of information in NEXUS, the main ways to
manipulate a ``Nexus`` object are

.. automethod:: commonnexus.nexus.Nexus.append_block

.. automethod:: commonnexus.nexus.Nexus.remove_block

.. automethod:: commonnexus.nexus.Nexus.replace_block


The methods to add blocks accept :class:`Block` instances as argument. Such instances can be
obtained by calling the generic factory method

.. automethod:: commonnexus.blocks.Block.from_commands

or specific implementations of `Block.from_data`, such as
:meth:`commonnexus.blocks.characters.Characters.from_data` or
:meth:`commonnexus.blocks.trees.Trees.from_data`


Comments
~~~~~~~~

The ``from_data`` methods of blocks accept a keyword argument ``comment`` to add a comment to a
block construct.

To add a comment to the top of a NEXUS file, one can proceed as follows:

.. code-block:: python

    >>> nex = Nexus('#NEXUS\n[{}]\n'.format('Comment goes here'))
    >>> nex.append_block(Block.from_commands([], name='theblock'))
    >>> print(nex)
    #NEXUS
    [Comment goes here]

    BEGIN theblock;
    END;
