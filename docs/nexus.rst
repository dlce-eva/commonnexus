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


.. automodule:: commonnexus.nexus


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

