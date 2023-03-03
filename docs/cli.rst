Command-line interface
======================

`commonnexus` comes with a `shell command <https://swcarpentry.github.io/shell-novice/reference.html#shell>`_
of the same name: `commonnexus`. `commonnexus` is a *multi-command* CLI, or a "git-like multi-tool command",
i.e. actual functionality to manipulate NEXUS files is implemented as sub-commands. To get an overview
and a list of sub-commands, run

.. command-output:: commonnexus -h


Most commands can read input from `stdin` and print results to `stdout`. Thus, these commands can
easily be chained together with other shell commands:

.. command-output:: echo "#nexus begin trees; tree 1 = ((a,b)c); end;" | commonnexus normalise - | grep TREE | grep -v TREES
    :shell:


In the following we describe the available sub-commands.


`commonnexus normalise`
-----------------------

Arguably the most important sub-command is `normalise`, because it removes quite a few complexities
of the NEXUS format (e.g. different `TRIANGLE` options for `DISTANCES`, or `EQUATE` mappings for
`CHARACTERS`), and thus makes downstream NEXUS reading a lot more reliable.

.. command-output:: commonnexus normalise -h

For examples of of running `commonnexus normalise` refer to the documentation of the underlying
function :func:`commonnexus.tools.normalise.normalise`.

**Normalising CHARACTERS:**

.. command-output:: commonnexus normalise '#nexus begin d[c]ata; dimensions nchar=3; format missing=x nolabels; matrix x01 100 010; end;'


**Normalising DISTANCES:**

.. command-output:: commonnexus normalise '#nexus begin distances; dimensions ntax=3; format missing=x nodiagonal; matrix t1 t2 x t3 1.0 2.1; end;'


**Normalising TREES:**

.. command-output:: commonnexus normalise '#nexus begin trees; translate a t1, b t2, c t3; tree 1 = ((a,b)c); end;'


`commonnexus combine`
---------------------


.. command-output:: commonnexus combine -h

**Combining CHARACTERS blocks:**

.. command-output:: cat characters.nex | commonnexus combine - characters.nex
    :shell:


**Combining TREES blocks:**


`commonnexus binarise`
----------------------

.. command-output:: commonnexus binarise -h


**Examples**:

.. command-output:: commonnexus binarise "#NEXUS BEGIN DATA; DIMENSIONS nchar=1; MATRIX t1 a t2 b t3 c t4 d t5 e; END;"


`commonnexus describe`
----------------------

.. command-output:: commonnexus describe -h


**Describing character set sizes:**

The output of the `describe` command is also suitable for piping to other commands. E.g.
`termgraph <https://pypi.org/project/termgraph/>`_ can be used to display character set sizes:

.. command-output:: commonnexus describe characters.nex --binary-character-size | termgraph
    :shell:
