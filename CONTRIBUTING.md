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
Include links to existing child issues when available. After submission, someone
with Triage access or higher can use **Create sub-issue** or **Add existing issue**
to connect the child issues. Track progress through those links. See
[GitHub's sub-issue guide](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues).

Security vulnerabilities belong in private reporting, not these public forms.
Follow the affected repository's security policy or the shared guidance at
<https://github.com/OpenTLV/.github/blob/main/SECURITY.md>.

## Branch names

Create a branch from the destination repository's current default branch. Use
`<type>/<issue-number>-<short-description>` when the work relates to an issue,
for example `docs/26-simplify-validation-guidance`. Put the issue number directly
after the slash, without `#`. If several issues apply, use the primary issue's
number and list all relevant issues in the PR description. For an issue in
another repository, include its full `owner/repo#number` reference in the PR
description so the branch number has context.

For work without an issue, use `<type>/<short-description>`. Write the description
in lowercase English words separated by hyphens. Use `feat/` consistently rather
than `feature/`.

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
`fix/20-broken-contribution-links` for work linked to issue #20, or
`fix/broken-contribution-links` when no issue applies. Existing branches do not
need to be renamed; use this convention for new branches.

## Commit messages

Write a concise English commit message describing the change. When the commit
relates to an issue, include its number in parentheses at the end of the subject,
for example `Document organization-wide changelog conventions (#17)`.
For an issue in another repository, use `(owner/repo#17)` instead.

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

Maintainers review these naming and description rules. Follow the destination
repository's documented automated checks as well.

### Issue and PR labels

The shared Bug report, Feature request, and Chore forms apply `bug`,
`enhancement`, and `chore`, respectively, where those labels exist.
Maintainers apply any additional labels that describe the work. Use labels
available in the destination repository and follow its local conventions.

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

## Changelogs

For future changelog updates across OpenTLV repositories, use a root
`CHANGELOG.md` following [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

- When there are pending changes, use `## [Unreleased]` as the first version
  section. Add notable changes there as work lands, grouped under
  `Added`, `Changed`, `Deprecated`, `Removed`,
  `Fixed`, or `Security` where applicable; omit empty categories.
- Keep released versions in reverse chronological order
  (newest release first).
- **Prepend a newly introduced category at the top of its version section**,
  before any existing categories. Categories have no fixed order.
- **Prepend every new entry at the top of its category**, above all existing
  entries in that category. Never append it below older entries. This is an
  explicit OpenTLV convention in addition to Keep a Changelog.
- Preserve existing entries when adding new ones. Avoid unnecessary reordering
  or rewriting of historical release notes.
- Write clear, user-facing descriptions of notable changes. Curate the notes;
  do not generate a changelog by dumping Git commit logs.
- At release time, move the relevant Unreleased entries into a section named
  `## [<version>] - YYYY-MM-DD`, using the actual version and ISO 8601 release
  date. If all entries have moved, the empty Unreleased section and its link
  definition may be omitted until the next pending change. Do not invent
  releases for policy updates.
- Use the `v` prefix in Git release tags, for example `v1.0.0`, but omit it
  from changelog version headings: `## [1.0.0] - YYYY-MM-DD`.
- Link version headings to tags or comparisons where applicable. When the
  Unreleased section is present, its comparison starts at the latest release
  tag, if one exists.

Every OpenTLV `CHANGELOG.md` must start with the introduction shown below.
The `OpenTLV/.github` changelog keeps all references unlinked and uses plain
text for the names of both standards. Other repositories include both links as
shown. The versions, dates, and changes after the introduction are examples.

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Newest added feature.
- Previously documented feature.

### Fixed

- Newest bug fix.
- Previously documented bug fix.

## [0.9.0] - 2026-11-16

### Changed

- Improve configuration diagnostics.

## [0.8.0] - 2026-10-01

### Added

- Initial configuration support.
```

For example, in a repository with tags `v0.8.0` and `v0.9.0`, define
`[Unreleased]` as `https://github.com/OWNER/REPO/compare/v0.9.0...HEAD` and
`[0.9.0]` as `https://github.com/OWNER/REPO/compare/v0.8.0...v0.9.0`, replacing
`OWNER/REPO` and tag names with the destination repository's actual values.

For release candidates, stable promotion, and publication, follow the
[OpenTLV release policy](https://github.com/OpenTLV/.github/blob/main/docs/releases.md).

## Repository development guidance

Follow the destination repository's development instructions for setup, tooling,
and checks. For changes to OpenTLV/.github itself, see its
[development guide](https://github.com/OpenTLV/.github/blob/main/docs/development.md).

## Contributions and ownership

Submit only material you have the right to contribute. Contributions are offered
under the destination repository's applicable license. Preserve existing
copyright and third-party notices; do not assume this repository's MIT license
licenses another project. No CLA or signed-off-by requirement is introduced by
these defaults. Each repository may document additional requirements.
