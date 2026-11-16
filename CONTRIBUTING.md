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

## Working on this community repository

The OpenTLV/.github organization bootstrap uses the branch
`feat/bootstrap-community-standards`. In a PR in OpenTLV/.github, use `Refs #1`
while deployment acceptance checks remain pending; use `Closes #1` only when
the PR completes all acceptance criteria.

Requirements: Git and Python 3.12 with pip and venv. From a fresh checkout:

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
```

For newly created files, stage the intended paths with `git add <path>` before
running `pre-commit run --all-files`: it checks files known to Git. The first run
may normalize files; review changes and rerun until all checks pass. Both tools
run in this repository's CI. Dependencies are pinned directly; their transitive
dependencies are resolved by pip and are not a complete lockfile.
When updating PyYAML or REUSE, keep the versions in requirements-dev.txt and
.pre-commit-config.yaml aligned. CI runs REUSE through the pre-commit hook.

Keep Markdown readable as plain text, use descriptive link text and relative
links within this repository, and use absolute GitHub links in inherited files
when referring to central policies. Verify claims and public project links
against current repositories. Avoid announcing planned capabilities as available.
Record user-visible policy and configuration changes under Unreleased in
CHANGELOG.md. End each entry associated with an issue with its number in
parentheses, for example `(#1)`. Follow the licensing instructions at
<https://github.com/OpenTLV/.github/blob/main/docs/licensing.md>.

## Contributions and ownership

Submit only material you have the right to contribute. Contributions are offered
under the destination repository's applicable license. Preserve existing
copyright and third-party notices; do not assume this repository's MIT license
licenses another project. No CLA or signed-off-by requirement is introduced by
these defaults. Each repository may document additional requirements.
