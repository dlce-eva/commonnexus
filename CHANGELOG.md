# Changes

## [Unreleased]

- Support renaming taxa when normalising NEXUS.


## [v1.8.0] - 2023-11-16

- Support writing NEXUS which is "more compatible" with some R packages.
- Add Python 3.12 to supported versions.


## [v1.7.0] - 2023-10-13

Allow adding a comment to blocks created from data.


## [v1.6.1] - 2023-10-05

- Fixed bug whereby the correct precedence of taxa labels was not obeyed when
  translating trees.


## [v1.6.0] - 2023-08-09

- `tools.normalise.normalise` now accepts a `remove_taxa` argument, making
  it easy to remove taxa from a NEXUS file in a consistent way.


## [v1.5.0] - 2023-07-20

- Make NEXUS content created by `commonnexus` simpler to parse and thus
  `commonnexus normalise` more useful as a tool to prepare NEXUS input for
  other tools.


## [v1.4.0] - 2023-07-18

- Dropped py3.7 compatibility.
- Allow unquoted content for SYMBOLS sub-command of FORMAT.
- Warn (or raise Error) when duplicate character names are specified for a MATRIX.


## [v1.3.0] - 2023-05-17

- Cache translate mappings in TREES block to speedup translation of multiple trees.


## [v1.2.0] - 2023-03-15

- API: Added `Tree.newick_string` property.


## [v1.1.0] - 2023-03-13

- Fixed bug where the Nexus.cfg was not consulted when reading CHARACTERS MATRIX.
- Keep state labels when normalising a NEXUS CHARACTERS block.
- Better support for Morphbank-style references in NOTES.
- CLI: Support dropping characters by number.
- CLI: Support batch-renaming taxa via lambda function.
- CLI: Added `split` command to split Mesquite's multi-block NEXUS.
- CLI: Added `taxa --describe` option, which is particularly useful with Morphobank NEXUS.
- CLI: Added `trees --rename` option.
- CLI Backwards incompatibility: `characters --multistatise` now requires an argument for
  the `--multistatise` option.


## [v1.0.0] - 2023-03-08

First, feature-complete release.

