# Licensing and attribution

This repository uses the [MIT license](../LICENSE), with the copyright notice
`Copyright (c) 2026 Marek Cingel`. [REUSE.toml](../REUSE.toml) assigns SPDX licensing
metadata to repository files; [LICENSES/MIT.txt](../LICENSES/MIT.txt) carries the
license text.
These declarations cover this repository only. Every other OpenTLV repository
must carry and maintain its own license and copyright notices.

New original material here uses MIT unless explicitly agreed otherwise. Add
accurate author or rights-holder notices where appropriate. The repository-wide
REUSE annotation is aggregated with file-specific notices; it must not be used
to erase or relicense third-party material. Before adding material under a
different license, narrow the annotation's paths to exclude it and add explicit
file-level or path-level metadata and the relevant license in LICENSES/.

Preserve upstream notices for copied or adapted material and document its source,
revision, license, and modifications. Check compatibility before inclusion. A
URL alone does not replace required attribution or license text. Do not add
assets whose redistribution rights are unknown.

## Third-party material and tools

No third-party source code, images, or policy text is intentionally vendored in
this bootstrap. The conduct policy is original. The MIT license text is the
repository's license, duplicated under LICENSES/ for REUSE.

Development tools are installed separately, not redistributed here:

| Tool | Upstream | License |
| --- | --- | --- |
| pre-commit | <https://github.com/pre-commit/pre-commit> | MIT |
| REUSE tool | <https://github.com/fsfe/reuse-tool> | Apache-2.0 AND CC0-1.0 AND CC-BY-SA-4.0 AND GPL-3.0-or-later (distribution metadata) |
| PyYAML | <https://github.com/yaml/pyyaml> | MIT |
| markdownlint-cli | <https://github.com/igorshubovych/markdownlint-cli> | MIT |
| Node.js | <https://github.com/nodejs/node> | MIT with bundled third-party notices |

Tool licenses do not change the license of the material they check. Review
upstream license and dependency metadata when updating pinned versions.

Specification: <https://reuse.software/spec-3.3/>.
