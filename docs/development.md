# Developing the community repository

This guide applies only to OpenTLV/.github. Read the shared
[contribution rules](../CONTRIBUTING.md) for branch names, commits, pull requests,
and changelogs. Other OpenTLV repositories define their own development setup.

## Setup and checks

Requirements: Git and CPython 3.10 or 3.12 with pip and venv; both are checked in
CI. Supported platforms and dependency installation boundaries are documented
in the [dependency integrity policy](dependencies.md). Select the intended interpreter before creating the virtual
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
python -m pip install --require-hashes --only-binary=:all: -r requirements-build.txt
python -m pip install --require-hashes --no-build-isolation --only-binary=:all: --no-binary=reuse -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

Pre-commit runs Markdown lint, the community checker, its regression tests, and
REUSE licensing checks. Separate REUSE and unittest runs are not required for
normal validation. To isolate a failure, run `pre-commit run reuse --all-files`
or `pre-commit run community-check-tests --all-files`.

Stage intended new files with `git add <path>` before the full run so Markdown
lint includes them. The first run may normalize files; review changes and rerun
until all checks pass. Coverage differs by hook:

| Check | File coverage with `pre-commit run --all-files` |
| --- | --- |
| Markdown lint | Markdown files selected by pre-commit from Git-tracked paths, including newly staged files; unstaged untracked files are not selected. |
| Community checker (`scripts/check_community.py`) | Existing tracked files plus non-ignored untracked files, discovered through `git ls-files --cached --others --exclude-standard`; ignores the hook's filename list. |
| REUSE | Repository files, including non-ignored untracked files, subject to REUSE exclusions such as license texts, metadata sidecars, empty files, and symlinks; ignores the hook's filename list. |
| Regression tests | Runs the test suite regardless of the selected filenames. |

The three local hooks use `language: system`, `pass_filenames: false`, and
`always_run: true`. They use the activated, hash-locked Python environment instead
of installing dependencies in separate hook environments.
Consequently, a pre-commit filename selection does not restrict their scope.
Untracked files inside ignored directories such as `.cache/` and `.venv/` are
excluded from repository scans.

Changes to workflows must also pass actionlint and zizmor; see
[GitHub Actions checks](actions-checks.md) for local commands. CI runs the same
pre-commit checks and runs the workflow analyzers once on Python 3.12.

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
adding status sections to the changelog.
Follow the [licensing instructions](licensing.md).

## Tooling and updates

Pre-commit installs markdownlint-cli 0.45.0 from its pinned Git commit and an
isolated Node.js 24.11.1 runtime; a global Node.js installation is not required.
The first run needs network access to GitHub, PyPI, the npm registry, and the
Node.js download service.

- Dependabot proposes monthly updates for SHA-pinned workflow actions.
- Maintain direct Python pins in `requirements-dev.in` and regenerate
  `requirements-dev.txt` using the [dependency integrity policy](dependencies.md).
  Local Python hooks use that environment and have no separate dependency pins.
- Maintain hook revisions and the Node.js runtime manually.
- Review analyzer releases monthly and when relevant security fixes appear.
  Follow the [analyzer integrity and update policy](actions-checks.md#suppressions-and-updates)
  for paired versions, artifact URLs, and hashes.

The full Python development graph is pinned and hash-checked, including
transitive dependencies. The analyzer and lock-generator wheel requirements are
separate hash-checked files. The [dependency integrity policy](dependencies.md)
describes regeneration, supported environments, and the remaining bootstrap and
Node/npm limitations. Run the documented checks after updates.

Scheduled updates do not enable the dependency graph, Dependabot alerts, or
security updates. Maintainers configure these settings separately; follow the
[adoption guide](adoption.md).

## Workspace integration

This directory is a standalone Git repository, even when opened in a multi-root
workspace beside other OpenTLV projects. Run setup and checks from this directory
with its own `.venv`; install hooks here only. From the parent workspace, use
`git -C .github status` to inspect this repository and select its interpreter in
your editor. Editor tasks must set their working directory to this repository.

The shared policies are GitHub defaults; these development dependencies, hooks,
lint rules, and CI are local to OpenTLV/.github. Other repositories maintain
their own tooling and adopt changes explicitly through their own review process.
