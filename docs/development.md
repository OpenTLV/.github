# Developing the community repository

This guide applies only to OpenTLV/.github. Read the shared
[contribution rules](../CONTRIBUTING.md) for branch names, commits, pull requests,
and changelogs. Other OpenTLV repositories define their own development setup.

## Setup and checks

Use Git and the CPython version in [`.python-version`](../.python-version) with
pip and venv on Ubuntu 24.04 x86-64. CI uses the same version and platform. On
Windows, use Ubuntu 24.04 in WSL 2 and run the commands in its Linux shell.
See the [dependency integrity policy](dependencies.md).
From a fresh checkout:

```sh
git clone https://github.com/OpenTLV/.github.git
cd .github
"python$(cat .python-version)" -m venv .venv
```

Activate the environment and install the locked development dependencies:

```sh
. .venv/bin/activate
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
pre-commit checks in `quality` and the analyzers in `workflow-analyzers`.

The community checker validates UTF-8, LF endings, trailing whitespace, final
newlines, conflict markers, local Markdown link targets, YAML/JSON syntax, and
basic issue form structure. Repository files are limited to 1 MiB each; large
verification artifacts belong in the ignored `.cache/` directory. The Markdown
linter uses `.markdownlint.json`: line-length limits are disabled for readable
tables and URLs, and a top-level heading is not required because the PR template
starts at heading level two. Regression tests exercise valid and invalid files.
Local validation does not establish GitHub form rendering or submission behavior.

### Issue-form option checks

Dropdown and checkbox fields must define a non-empty `attributes.options` list.
Dropdown entries must be nonblank strings. Checkbox entries must be mappings
with a nonblank string `label`; an optional `required` value must be a YAML
boolean. Option labels must be unique within each field. Quote numeric-looking
or boolean-looking dropdown choices to keep them strings when YAML is parsed.
Checkbox labels may contain Markdown.

Issue forms can use `type: upload` with a field ID and a label for attachments.

These checks cover option structure, not the complete GitHub form schema or
rendering behavior. Follow GitHub's [form schema](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema)
for other attributes and verify form behavior after deployment when needed.

### Text files and binary assets

There are currently **no approved binary asset paths or types** in this
repository. All checked files must remain UTF-8 text without NUL bytes and meet
the existing whitespace, newline, and 1 MiB limits. The checker rejects common
binary extensions (the case-insensitive `BINARY_SUFFIXES` set in
`scripts/check_community.py`), invalid UTF-8, and NUL-containing content, including
when a file has been renamed to a text extension. This is a text policy, not a
complete file-format detector; other text-encoded payloads still require review.

The checker rejects symbolic links, including dangling links and tracked files
whose parent directory has been replaced by a symbolic link.

An image suffix or a location under `profile/` does not grant an exception.
Verification screenshots and temporary artifacts stay outside Git in ignored
`.cache/`. Do not add an ignored directory merely to hide an intended repository
asset from validation.

If a genuine need arises, such as an organization profile image, propose the
asset and its checker exception together in a reviewed PR. Identify each exact
repository-relative path and allowed format; prefer a small PNG or JPEG under
`profile/assets/` for that use case. These are candidate formats and locations,
not approved exceptions. Document purpose, source, redistribution rights, and
[licensing/attribution](licensing.md). The implementation must verify format
content rather than trusting an extension, reject malformed files and path
escapes/symlinks, retain the 1 MiB cap, and add positive and negative regression
tests. Keep text checks on every other file; no directory-wide or suffix-only
bypass is permitted. No binary exception is implemented until an asset actually
requires one.

### Local link and conflict-marker checks

The community checker validates ordinary inline Markdown links and images,
angle-bracket autolinks, HTML `href` attributes, and bare file URLs of the form
`https://github.com/OpenTLV/.github/blob/main/<path>`. It checks reference-style
destinations at their definitions, including unused definitions. Repository URLs
map to files in the current checkout, including uncommitted changes. The GitHub
host, owner, and repository name are case-insensitive. The `blob/main/` prefix
and target path retain their case, and `blob` targets must be files. CI checks
these destinations without making network requests.

The same local target and heading checks apply to `contact_links[].url` in
`.github/ISSUE_TEMPLATE/config.yml` and to the Markdown in issue forms'
`body[].attributes.value` for entries of type `markdown`. Use absolute GitHub
file URLs for shared policies so the links also work in consuming repositories.

Relative paths resolve from the containing document; paths beginning with `/`
resolve from the repository root. Percent-encoded paths and fragments are
decoded. Paths escaping the checkout, including resolved symlinks, Windows
drive/stream syntax, backslashes, and NUL bytes, are rejected.

For Markdown targets, fragments must match a heading anchor or an explicit HTML
`id`, including for same-document links. HTML IDs are case-sensitive. Heading
anchors cover ordinary ATX headings and single-line setext headings.
Normalization lowercases text, removes punctuation and formatting,
preserves Unicode letters/numbers and underscores, replaces spaces with hyphens,
and adds numeric suffixes for duplicate headings, including suffix collisions.
Inline code text, simple link labels, and HTML entities in headings are supported.
See GitHub's [section-link rules](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links).

The checker covers the syntax above. Multiline or complex nested headings,
line-range fragments, and fragments on non-Markdown targets are outside that
scope. Use percent encoding or angle-wrapped Markdown destinations for paths
containing spaces or parentheses.
Links and headings inside backtick or tilde fences (up to three leading spaces)
are ignored. Matching inline code spans are excluded from link and HTML ID
extraction. Unmatched backticks leave subsequent links visible.
Nested list/blockquote fences and indented code blocks are outside this subset.

Markdown and YAML suffixes are matched case-insensitively. Git paths with invalid
UTF-8 bytes are reported using byte escapes, and validation continues.

Conflict scanning still examines all file text, including code examples. Opening,
closing, and diff3-base markers are rejected. A standalone separator is rejected
in non-Markdown files and when it has no preceding nonblank line in Markdown.
An equals underline following Markdown text is accepted as a setext heading;
an isolated conflict separator in that position is inherently ambiguous. Full
conflicts remain detectable through their opening/closing markers.

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
isolated Node.js 24.22.3 runtime; a global Node.js installation is not required.
The first run needs network access to GitHub, PyPI, the npm registry, and the
Node.js download service.

- Dependabot checks SHA-pinned workflow actions monthly for releases at least
  seven days old. GitHub generates Dependabot alerts only for actions referenced
  by semantic version, so these SHA pins receive no alert-driven security PRs.
  See [Dependabot cooldown](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#cooldown)
  and [GitHub's alert coverage](https://docs.github.com/en/code-security/reference/supply-chain-security/dependency-graph-supported-package-ecosystems).
- Review online zizmor findings from pushes to `main` and weekly runs. When a
  published advisory affects a pin, verify the fixed upstream release and update
  the full SHA and its version comment promptly.
  See [zizmor's advisory check](https://docs.zizmor.sh/audits/#known-vulnerable-actions).
- Maintain direct Python pins in `requirements-dev.in` and regenerate
  `requirements-dev.txt` using the [dependency integrity policy](dependencies.md).
  Local Python hooks use that environment and have no separate dependency pins.
- Maintain hook revisions and the Node.js runtime manually.
- Review analyzer releases monthly and when relevant security fixes appear.
  Follow the [analyzer integrity and update policy](actions-checks.md#suppressions-and-updates)
  for paired versions, artifact URLs, and hashes.
- During monthly tooling review, check the scheduled `Community quality` runs
  for lockfile drift warnings before deciding whether to regenerate the lock.

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
