Tools
=====

`commonnexus` provides a couple of *tools*, implementing common operations on NEXUS objects.
These tools are often functions operating on (a) :class:`commonnexus.Nexus` instance(s), and
returning a new of modified :class:`commonnexus.Nexus` object.


`combine`
---------

.. automodule:: commonnexus.tools.combine
    :members:


`normalise`
-----------

.. automodule:: commonnexus.tools.normalise
    :members:


`matrix`
--------

CHARACTERS matrices are arguably the most complex objects in NEXUS files. Thus, manipulations of
such matrices is implemented in a separate module.

.. automodule:: commonnexus.tools.matrix
    :members:
