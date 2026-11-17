# Developing the community repository

This guide applies only to OpenTLV/.github. Read the shared
[contribution rules](../CONTRIBUTING.md) for branch names, commits, pull requests,
and changelogs. Other OpenTLV repositories define their own development setup.

## Setup and checks

Requirements: Git and Python 3.10 or newer with pip and venv. The CI checks
Python 3.10 and 3.12. Select the intended interpreter before creating the virtual
environment (for example, `py -3.10` on Windows or `python3.10` on POSIX).
From a fresh checkout:

```sh
git clone https://github.com/OpenTLV/.github.git
cd .github
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in PowerShell, or
`. .venv/bin/activate` in a POSIX shell, then run:

```sh
python -m pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
reuse lint
python -m unittest discover -s tests
```

For newly created files, stage the intended paths with `git add <path>` before
running `pre-commit run --all-files`: it checks files known to Git. The first run
may normalize files; review changes and rerun until all checks pass. Pre-commit
and the workflow analyzers run in this repository's CI. Dependencies are pinned
directly; their transitive dependencies are resolved by pip and are not a complete
lockfile.
When updating PyYAML or REUSE, keep the versions in requirements-dev.txt and
.pre-commit-config.yaml aligned. CI runs REUSE through the pre-commit hook.
Dependabot proposes monthly updates for the SHA-pinned workflow actions. Python
tools, hook revisions, and the Node.js runtime are updated manually so the paired
pins stay aligned. Workflow analyzer pins and integrity checks are maintained
manually as described in [GitHub Actions checks](actions-checks.md).

Changes to workflows must also pass actionlint and zizmor. Follow the same
guide for local commands; these checks run once in the existing quality workflow.

Scheduled version updates do not enable the dependency graph, Dependabot alerts,
or security updates. Maintainers configure these repository settings separately;
follow the [adoption guide](adoption.md).

Pre-commit installs markdownlint-cli 0.45.0 from its pinned Git commit and an
isolated Node.js 24.11.1 runtime; a global Node.js installation is not required.
The first run needs network access to GitHub, PyPI, the npm registry, and the
Node.js download service. Direct Python tool versions and hook/runtime versions
are pinned; transitive Python and npm packages are not a complete lockfile.

The community checker validates UTF-8, LF endings, trailing whitespace, final
newlines, conflict markers, local Markdown link targets, YAML/JSON syntax, and
basic issue form structure. Repository files are limited to 1 MiB each; large
verification artifacts belong in the ignored `.cache/` directory. The Markdown
linter uses `.markdownlint.json`: line-length limits are disabled for readable
tables and URLs, and a top-level heading is not required because the PR template
starts at heading level two. Regression tests exercise valid and invalid files.
Local validation does not establish GitHub form rendering or submission behavior.

Keep Markdown readable as plain text, use descriptive link text and relative
links within this repository, and use absolute GitHub links in inherited files
when referring to central policies. Verify claims and public project links
against current repositories. Avoid announcing planned capabilities as available.
Record user-visible policy and configuration changes under Unreleased in
CHANGELOG.md. End each entry associated with an issue with its number in
parentheses, for example `(#1)`. Follow the shared
[changelog rules](../CONTRIBUTING.md#changelogs), including prepending new entries
within each category.
Record deployment evidence and pending checks in docs/adoption.md rather than
adding status sections to the changelog. At release time, move entries under
the actual version and release date; do not invent releases for policy updates.
Follow the [licensing instructions](licensing.md).

## Workspace integration

This directory is a standalone Git repository, even when opened in a multi-root
workspace beside other OpenTLV projects. Run setup and checks from this directory
with its own `.venv`; install hooks here only. From the parent workspace, use
`git -C .github status` to inspect this repository and select its interpreter in
your editor. Editor tasks must set their working directory to this repository.

The shared policies are GitHub defaults; these development dependencies, hooks,
lint rules, and CI are local to OpenTLV/.github. Other repositories maintain
their own tooling and adopt changes explicitly through their own review process.
