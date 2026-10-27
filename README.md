# OpenTLV Community Repository

This public repository is the home for OpenTLV community health files and shared
GitHub templates. It is included as the `../.github` sibling in the
[OpenTLV workspace](https://github.com/OpenTLV/opentlv-workspace).

Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## Bootstrap scope

This initial setup provides repository and licensing metadata. Shared contribution
guidance, Code of Conduct, security policy and templates are tracked separately in
[Workspace #48](https://github.com/OpenTLV/opentlv-workspace/issues/48), following
[bootstrap #47](https://github.com/OpenTLV/opentlv-workspace/issues/47).
No organization-wide policy is established by this README.

Repository-local community files take precedence over organization defaults.
Each repository retains its LICENSE, SPDX/REUSE metadata, package notices,
build/test instructions, CI and private vulnerability reporting settings.
This repository does not distribute those settings or run component builds.

## Licensing

Original contributions by Marek Cingel are copyright Marek Cingel and licensed
under MIT; see [LICENSE](LICENSE). OpenTLV is the GitHub organization, not a
separate legal copyright holder. Preserve contributor and third-party notices;
MIT contributions do not assign copyright.

This repository follows the workspace's REUSE/SPDX convention. [REUSE.toml](REUSE.toml)
annotates explicit documentation and configuration paths with aggregate metadata.
New source files need their own accurate copyright and SPDX headers. Third-party
files retain their own notices and license texts. [LICENSES/MIT.txt](LICENSES/MIT.txt)
provides the referenced license text without replacing the root LICENSE.

## Local contributor checks

Python 3.10+ and Git are required. From this repository, create a dedicated
contributor environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` in Bash, then run:

```bash
python -m pip install -r requirements-dev.txt
python -m pre_commit install
python -m pre_commit validate-config
python -m pre_commit run --all-files
python -m reuse lint
```

The pinned hooks check whitespace, final newlines, YAML/JSON syntax, file size,
Markdown and repository-wide REUSE metadata. The first run downloads hook
environments, including the Markdownlint Node runtime. Hooks apply only to this
checkout; other OpenTLV repositories keep their own configurations.

Whitespace and Markdown hooks may edit files. Review and stage the changes, then
rerun checks. New files must be staged to be included by `--all-files`. Third-party
and generated directories are excluded from formatting hooks but still need valid
licensing metadata for REUSE. Binary fixtures are excluded from text rewriting.
Copyright metadata is checked without automatic ownership annotation.

To run only the license check:

```bash
python -m reuse lint
```

No additional CI is needed for this bootstrap.
