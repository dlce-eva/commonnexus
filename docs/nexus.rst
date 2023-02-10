NEXUS Files
===========

Since NEXUS is an *Extensible File Format*, it's natural habitat is the file system. Thus, to
instantiate a :class:`Nexus <commonnexus.nexus.Nexus>` object, we typically read a file:

.. code-block:: python

    >>> from commonnexus import Nexus
    >>> nex = Nexus.from_file('tests/fixtures/ape_random.trees')
    >>> for name in nex.blocks:
    ...     print(name)
    ...
    TAXA
    TREES


.. automodule:: commonnexus.nexus
    :members:
