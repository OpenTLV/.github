# Contributing to OpenTLV

Thank you for helping improve OpenTLV. First read the destination repository's
README, license, security policy, and local contribution instructions. Local
instructions take precedence over these defaults.

## Before making a change

Search existing issues and pull requests. Report a reproducible bug or explain
the problem and intended outcome of a proposal in the relevant repository.
Discuss substantial changes before implementation. Never include secrets,
personal information, or sensitive vulnerability details in public issues.

Follow the branch naming rules below, make a small reviewable change, and run
the project's documented checks. Include meaningful regression coverage for behavior changes.
Explain the motivation, resulting behavior, validation, and limitations in the
pull request. Maintainers review changes before merging; no response time or
release schedule is guaranteed.

## Choosing an issue form

| Form | Use it for |
| --- | --- |
| Bug report | Reproducible defects and unexpected behavior |
| Feature request | Proposals for new capabilities or improvements |
| Task | Defined implementation work that is neither a bug report nor a feature proposal |
| Chore | Repository maintenance, tooling, dependencies, or documentation upkeep |
| Epic | Larger coordinated work split into child issues |

For a Task, describe the objective, scope, applicable technical requirements,
acceptance criteria, dependencies or risks, and validation plan. Chore keeps its
required motivation, scope, and acceptance fields; its Validation field is optional.

For an Epic, describe the objective, scope and exclusions, expected outcomes,
planned work breakdown, dependencies or risks, and epic-level acceptance criteria.
After creating it, use GitHub's **Create sub-issue** or **Add existing issue**
controls to track the actual children. The form does not create those relationships
automatically. Keep the child-issue plan descriptive; use native sub-issue progress
instead of maintaining a duplicate checklist in the description. See
[GitHub's sub-issue guide](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues).

Security vulnerabilities belong in private reporting, not these public forms.
Follow the affected repository's security policy or the shared guidance at
<https://github.com/OpenTLV/.github/blob/main/SECURITY.md>.

## Branch names

Create a branch from the destination repository's current default branch. Use
`<type>/<short-description>`, with lowercase English words separated by hyphens.
Use `feat/` consistently rather than `feature/`.

| Prefix | Purpose |
| --- | --- |
| `feat/` | New features or capabilities |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code restructuring without changing behavior |
| `test/` | Tests and test infrastructure |
| `ci/` | CI workflows and automation |
| `chore/` | Other repository maintenance |

Choose the prefix that describes the main purpose of the change, for example
`fix/broken-contribution-links`.

## Pull requests

### Title

Write a concise English title in the imperative that describes the resulting
change. Start with a capital letter and omit the final period. Do not include
issue IDs or type prefixes such as `feat:`, `fix:`, or `docs:` in the title.
Put issue references in the PR description under **Related issues**. Branch
prefixes apply only to branch names.

Examples:

- `Bootstrap organization profile and community standards`
- `Fix broken contribution links`
- `Document repository adoption rules`

### Description and related issues

Use the repository's PR template. Describe the problem and resulting behavior,
checks actually run and their outcomes, and risks or compatibility concerns.
Complete the checklist accurately and replace or remove template placeholders.

In **Related issues**, put each issue on a separate line:

- For issues in the same repository as the PR, use only `#<number>`:
  `Closes #<number>` when the PR fully resolves the issue, or `Refs #<number>`
  when the PR relates to an issue but leaves work remaining.
- Only for issues in another repository, use `Closes owner/repo#<number>` or
  `Refs owner/repo#<number>`.
- Write `None` if no issue applies; remove unused lines.

Replace `<number>` with the actual issue number in the relevant repository.

These naming and description rules are reviewed by maintainers; the current
quality workflow does not enforce branch names, PR titles, or issue references.

### Issue and PR labels

Maintainers apply labels that describe the work. Use labels available in the
destination repository; local label conventions take precedence.

| Label | Purpose |
| --- | --- |
| `bug` | Incorrect behavior or a regression |
| `enhancement` | New features or improvements to project capabilities |
| `documentation` | Changes to documentation or contributor guidance |
| `chore` | Repository maintenance, tooling, dependencies, and CI changes |

Labels can be combined when they describe different aspects of a change. For
example, tooling changes that also update contributor guidance use `chore` and
`documentation`. Use `chore` for maintenance rather than adding `enhancement`
solely because a development tool or check is new.

Branch prefixes and labels serve separate purposes: a `chore/` branch does not
automatically apply a label. Contributors without label permissions can leave
label selection to maintainers.

## Working on this community repository

The OpenTLV/.github organization bootstrap uses the branch
`feat/bootstrap-community-standards`. In a PR in OpenTLV/.github, use `Refs #1`
while deployment acceptance checks remain pending; use `Closes #1` only when
the PR completes all acceptance criteria.

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
may normalize files; review changes and rerun until all checks pass. Both tools
run in this repository's CI. Dependencies are pinned directly; their transitive
dependencies are resolved by pip and are not a complete lockfile.
When updating PyYAML or REUSE, keep the versions in requirements-dev.txt and
.pre-commit-config.yaml aligned. CI runs REUSE through the pre-commit hook.
Dependabot proposes monthly updates for the SHA-pinned workflow actions. Python
tools, hook revisions, and the Node.js runtime are updated manually so the paired
pins stay aligned.

Scheduled version updates do not enable the dependency graph, Dependabot alerts,
or security updates. Maintainers configure these repository settings separately;
follow the [adoption guide](https://github.com/OpenTLV/.github/blob/main/docs/adoption.md).

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
parentheses, for example `(#1)`. Follow Keep a Changelog: group unreleased changes
under Added, Changed, Deprecated, Removed, Fixed, or Security as applicable.
Record deployment evidence and pending checks in docs/adoption.md rather than
adding status sections to the changelog. At release time, move entries under
the actual version and release date; do not invent releases for policy updates.
Follow the licensing instructions at
<https://github.com/OpenTLV/.github/blob/main/docs/licensing.md>.

### Workspace integration

This directory is a standalone Git repository, even when opened in a multi-root
workspace beside other OpenTLV projects. Run setup and checks from this directory
with its own `.venv`; install hooks here only. From the parent workspace, use
`git -C .github status` to inspect this repository and select its interpreter in
your editor. Editor tasks must set their working directory to this repository.

The shared policies are GitHub defaults; these development dependencies, hooks,
lint rules, and CI are local to OpenTLV/.github. Other repositories maintain
their own tooling and adopt changes explicitly through their own review process.

## Contributions and ownership

Submit only material you have the right to contribute. Contributions are offered
under the destination repository's applicable license. Preserve existing
copyright and third-party notices; do not assume this repository's MIT license
licenses another project. No CLA or signed-off-by requirement is introduced by
these defaults. Each repository may document additional requirements.
