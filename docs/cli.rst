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

.. warning::

    While :class:`commonnexus.Nexus <commonnexus.nexus.Nexus>` can read multiple blocks with the same
    name just fine, most of the commands listed below assume just one block per block type in their
    input (i.e. only act on the first occurrence of each block type).

In the following we describe the available sub-commands.


`commonnexus normalise`
-----------------------

Arguably the most important sub-command is `normalise`, because it removes quite a few complexities
of the NEXUS format (e.g. different `TRIANGLE` options for `DISTANCES`, or `EQUATE` mappings for
`CHARACTERS`), and thus makes downstream NEXUS reading a lot more reliable.

.. command-output:: commonnexus normalise -h

For examples of of running `commonnexus normalise` refer to the documentation of the underlying
function :func:`commonnexus.tools.normalise.normalise`.

Normalising CHARACTERS
~~~~~~~~~~~~~~~~~~~~~~

.. command-output:: commonnexus normalise '#nexus begin d[c]ata; dimensions nchar=3; format missing=x nolabels; matrix x01 100 010; end;'


Normalising DISTANCES
~~~~~~~~~~~~~~~~~~~~~

.. command-output:: commonnexus normalise '#nexus begin distances; dimensions ntax=3; format missing=x nodiagonal; matrix t1 t2 x t3 1.0 2.1; end;'


Normalising TREES
~~~~~~~~~~~~~~~~~

.. command-output:: commonnexus normalise '#nexus begin trees; translate a t1, b t2, c t3; tree 1 = ((a,b)c); end;'


`commonnexus combine`
---------------------

Combining data from multiple NEXUS files into a single one can be useful to have data and resulting
trees from a phylogenetic analysis in a single file or to aggregate character data for the same
set of taxa.

.. command-output:: commonnexus combine -h

Combining CHARACTERS blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. command-output:: cat characters.nex | commonnexus combine - characters.nex
    :shell:


`commonnexus split`
-------------------

The `Mesquite software <https://www.mesquiteproject.org/>`_ can write multiple TAXA, CHARACTERS and
TREES blocks - linked together via TITLE and LINK commands to a single NEXUS file. Most other tools
can't handle such "multi-taxa" files, though.

Running ``commonnexus split`` will split such files into one NEXUS file per CARACTERS or TREES block,
bundled with the appropriate TAXA block.

.. command-output:: commonnexus split -h


`commonnexus characters`
------------------------

The `characters` sub-command provides functionality to manipulate the characters matrix in a NEXUS file.

.. command-output:: commonnexus characters -h


"Binarise" the matrix
~~~~~~~~~~~~~~~~~~~~~

Some tools (e.g. `BEAST <http://www.beast2.org/features/data-type-binary.html>`_) offer special analysis options
for binary data. To convert multistate character data to you can run ``characters --binarise``:

.. command-output:: commonnexus characters --binarise "#NEXUS BEGIN DATA; DIMENSIONS nchar=1; MATRIX t1 a t2 b t3 c t4 d t5 e; END;"


"Multistatise" the matrix
~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes characters which are "naturally multistate" are coded as binary data (for the above reason).
E.g. `cognate-coded wordlist data <https://calc.hypotheses.org/849>`_ are often binarised for analysis
with BEAST, i.e. each cognate set is considered a separate character as opposed to grouping cognate sets
for the same meaning into a multistate character. Binary data is somewhat harder to inspect "manually",
though. E.g. figuring out whether languages may have words coded as cognate in two different cognate sets
for the same meaning is difficult looking at data such as
`<https://github.com/phlorest/birchall_et_al2016/blob/main/raw/Chapacuran_Swadesh207-2019-labelled.nex>`_.

Running ``characters --multitatise`` on such data can make this easier. The ``--multistatise`` option
expects a Python lambda function as argument, which converts a character label into a group key.
E.g. the character labels

.. code-block::

        1 100_laugh_A,
        2 100_laugh_B,
        3 100_laugh_C,

could be merged into a multistate character passing ``lambda c: '_'.join(c.split('_')[:-1])``.

.. code-block:: bash

    curl https://raw.githubusercontent.com/phlorest/birchall_et_al2016/main/raw/Chapacuran_Swadesh207-2019-labelled.nex |\\
    commonnexus characters --multistatise "lambda c: '_'.join(c.split('_')[:-1])" -

will output a `MATRIX` with rows like

.. code-block:: bash

    Cojubim  AAAAAAA??AB(AB)AECABAAAAACAABBECAAAA?A?(AB)ACAA?AA?AEACAA??CBA??AADACBB?C?(AB)...

where polymorphisms (e.g. ``(AB)``) mean a language has a word coded as cognate with two different
cognate sets for the same meaning.


Describing character set sizes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The output of the most commands is also suitable for piping to other commands. E.g.
`termgraph <https://pypi.org/project/termgraph/>`_ can be used to display character set sizes:

.. command-output:: commonnexus characters characters.nex --describe binary-setsize | termgraph
    :shell:


`commonnexus trees`
-------------------

The `trees` sub-command provides functionality to manipulate the TREES block in a NEXUS file.

.. command-output:: commonnexus trees -h



`commonnexus taxa`
------------------

The `taxa` sub-command provides functionality to manipulate the set of taxa in a NEXUS file.

.. command-output:: commonnexus taxa -h


Removing taxa
~~~~~~~~~~~~~

While removing a taxon from a NEXUS file can be as simple as deleting one line in the CHARACTERS MATRIX
command, it typically isn't because the taxon may also appears in TREES TRANSLATE, etc. ``taxa --drop``
will remove relevant taxon references from `TAXA`, `TREES`, `CHARACTERS`, `DATA`, `DISTANCES` and `NOTES` blocks.

.. command-output:: commonnexus taxa --drop t1 "#NEXUS BEGIN DATA; DIMENSIONS nchar=1; MATRIX t1 a t2 b t3 c t4 d t5 e; END;"

If you want to drop constant/invariant characters which might have arisen due to removing a taxon, you
could pipe the result of ``taxa --drop`` into ``characters --drop constant``.


Describing taxa
~~~~~~~~~~~~~~~

Describing the data for a taxon in a NEXUS file is particularly useful for files with a CHARACTERS
MATRIX of DATATYPE=STANDARD and labeled states - such as the files from `Morphobank <https://morphobank.org/>`_.

Running

.. code-block:: bash

    commonnexus taxa ../tests/fixtures/regression/mbank_X962_11-22-2013_1534.nex --describe 1

will output a markdown formatted table of characters looking like

+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Character                                                                 | State                                         | Notes         |
+===========================================================================+===============================================+===============+
| Vomer, shape of tooth patch                                               | Trapezoidal to ovate                          |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Orbitosphenoid                                                            | Present                                       |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Pterotic, enclosure of lateral line canal                                 | absent or incomplete                          |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Frontals, midline suture                                                  | joined along entire midline                   |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Frontoparietal crests                                                     | absent                                        |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Frontoparietal crests, sensory pore on dorsal margin                      | ?                                             |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Supraoccipital crest, shape                                               | long and low                                  |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Supraoccipital crest, horizontal shelf projecting laterally at mid-height | present                                       |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Supraoccipital crest, shape of dorsal margin                              | blade-like                                    |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Sphenotic, horizontal shelf                                               | absent                                        |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Mesethmoid, anterolaterally facing projection                             | absent                                        |               |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| Lateral ethmoid-lacrimal articulation, orientation                        | entirely or primarily in the horizontal plane | Waldman, 1986 |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+
| ...                                                                                                                                       |
+---------------------------------------------------------------------------+-----------------------------------------------+---------------+

