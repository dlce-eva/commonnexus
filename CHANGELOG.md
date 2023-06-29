# Changes

## [Unreleased]

- Dropped py3.7 compatibility.


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

