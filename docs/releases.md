# Release tags and GitHub Releases

This policy applies to every OpenTLV repository, including OpenTLV/.github.
Each repository owns its Full CI and release workflow. Only its release
workflow creates release tags. The tag, GitHub Release, and changelog entry
all identify the same version and the same commit from `main`.
Implementation of the shared CLI and the first release workflow is tracked in
[OpenTLV/.github#69](https://github.com/OpenTLV/.github/issues/69).

## What each repository configures

| Setting | What maintainers record in the repository |
| --- | --- |
| Display name | The project name used in release titles, including its capitalization. |
| Full CI | The repository's trusted workflow and the jobs that must succeed for a release. In OpenTLV/.github these are the `quality` and `workflow-analyzers` jobs of `Community quality`. |
| Publication identity | A dedicated actor, such as a GitHub App installed on the repository. Limit access to its write credential and the signing key to the release workflow's publication job on protected `main`. Validation and Full CI run with read-only access. |
| Signing identity | The approved public key fingerprint, its maintainer or team owner, and the verification material used to check signatures. The owner controls key access, rotation, and revocation. |
| Changelog tool | One parameterized Python CLI maintained in OpenTLV/.github. In each consuming workflow, check out OpenTLV/.github at a reviewed full commit SHA in a separate directory. OpenTLV/.github uses the script in its own pinned candidate checkout. |

## Publish a version

1. **Pin the candidate.** Dispatch the repository's release workflow from
   `refs/heads/main` with a full [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)
   version, such as `0.1.0-rc.1` or `0.1.0`. Reject other refs. Capture the
   dispatch commit SHA once and use it for checkout, validation, Full CI, and
   tagging, even if `main` advances during the run.
2. **Prepare the release notes.** Invoke the shared CLI directly with Python.
   Pass `--changelog` pointing to the candidate's root `CHANGELOG.md`,
   `--version` with the full input (without a leading `v`), and
   `--output release-notes.md`. Require the first release heading below
   `## [Unreleased]` to be `## [<version>] - YYYY-MM-DD` with a valid date
   and an exact version match, including any prerelease and build identifiers.
   Stop on a missing or mismatched section. Extract only that section's body,
   ending before the next version heading or at EOF. Preserve Markdown headings, lists, links,
   and code blocks. Include the definitions for references used in that body,
   even when they appear elsewhere in the changelog. Resolve relative link
   destinations against the pinned revision so they work on the Release page.
3. **Require Full CI for this commit.** Before creating any new tag, run the
   repository's Full CI for the pinned SHA and require every designated job
   to finish successfully. If CI runs separately, verify the repository,
   workflow identity, `head_sha`, and job conclusions for the candidate run.
   A skipped job, a passing PR check on a different SHA, or missing evidence
   blocks publication.
4. **Sign, verify, and push.** Serialize publication using a single
   repository-wide concurrency group across versions, with in-progress
   publication allowed to finish. Inside that group, check the remote tag
   first and apply the retry rules below if it exists. Otherwise create a
   signed annotated tag named `v<version>` directly on the pinned commit.
   Verify its signature against the repository's approved fingerprint, then
   inspect the signed tag object's embedded name, target type (`commit`), and
   target SHA. Push just that verified tag, without force.
5. **Publish the GitHub Release.** After confirming the verified tag exists
   on the remote, create the Release against it. Set the title to
   `<display name> <version>` and use the prepared Markdown file as its body.
   With GitHub CLI, use `gh release create` with `--verify-tag`, `--title`,
   and `--notes-file release-notes.md`. Add `--prerelease` exactly when the
   version has a SemVer prerelease component. [GitHub CLI release reference](https://cli.github.com/manual/gh_release_create).

## Retry an interrupted publication

Retry with the original version and pinned SHA. Under the same concurrency
group, read the remote state again, including after an ambiguous push or API
response. An access or network error leaves that state unknown and stops the run.

| Remote state | Workflow action |
| --- | --- |
| Tag and Release are absent | Follow the full publication sequence, including the exact-SHA Full CI gate. |
| Tag exists, Release is absent | Fetch the tag object. Verify its signature and approved signer, embedded name, and direct commit target exactly as for a new tag. Reuse the verified tag and publish the missing Release from the original candidate's notes. |
| Tag and published Release exist | Verify the tag, then compare the Release's tag, title, Markdown body, and prerelease flag to the expected values. A match completes the retry. |
| Tag is lightweight, unsigned, signed by an unapproved key, or names a different version or commit | Stop and report the conflict. The existing tag is immutable. |
| Release or remote state conflicts with the expected publication | Stop for maintainer review. Preserve the existing publication. |

## Signing key rotation

Store the private key in the repository's protected release environment or a
signing service restricted to its publisher. Keep trusted public verification
material independently of the tag being checked. For example, with OpenPGP,
use `git verify-tag --raw`, require successful verification, and match the
verified fingerprint to the approved key. [Git signature verification](https://git-scm.com/docs/git-verify-tag).

For a planned rotation, the owner reviews and records the replacement
fingerprint and its effective date, verifies a test signature, switches the
publisher to the new key, and retires the old private credential. Retain old
public keys and their approval periods for verifying historical releases. For a
suspected compromise, suspend publication, revoke the affected credential, and
review affected tags before resuming with an approved replacement. Existing
tags keep their original signatures.

## Enforce and verify immutable tags

Configure two **Active** tag rulesets. GitHub applies the bypass list to all
rules within one ruleset, so keep creation and immutability in separate rulesets.
[GitHub ruleset controls](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

| Target | Rules | Bypass actors |
| --- | --- | --- |
| All tags, with no exclusions | Restrict updates and restrict deletions | Empty, including for administrators and the release identity |
| Release tag names matching `v*` | Restrict creations | Only the dedicated release workflow identity |

In **Settings → Rules → Rulesets**, inspect repository and inherited rulesets.
Confirm active enforcement, tag targets, exclusions, restrictions, and bypass
actors with an account that can see those lists. An omitted bypass list is
unverified. [GitHub rulesets API](https://docs.github.com/en/rest/repos/rules#get-a-repository-ruleset).

Before the first production release, exercise equivalent rules in a disposable
repository. Confirm an ordinary writer cannot create a release tag and the
workflow can. As each actor, attempt a forced update to a different object and
a deletion for both a release tag and an unrelated tag in that disposable
repository. Confirm server-side ruleset rejections in rule insights and verify
that the remote tag object IDs still match their original values. Record the
actors, ruleset IDs, and outcomes alongside the production settings review. Follow the
[repository governance baseline](governance.md) when applying settings.

## Example promotion from prerelease to stable

For a project with display name `OpenTLV`, the first dated heading
`## [0.1.0-rc.1] - 2026-11-10` yields tag `v0.1.0-rc.1` and a GitHub
prerelease titled `OpenTLV 0.1.0-rc.1`.

To promote it without code changes, keep that published section intact. Add a
new dated stable section immediately below Unreleased that links to the
prerelease. In this example the shared CLI carries the `rc-notes` definition
into the stable Release body.

```markdown
## [0.1.0] - 2026-11-12

### Changed

- Promote [0.1.0-rc.1][rc-notes] to stable without code changes.

[rc-notes]: https://github.com/OpenTLV/opentlv/releases/tag/v0.1.0-rc.1
```

Run Full CI on the new `main` commit containing this stable section. After it
passes, the workflow signs `v0.1.0` on that commit and publishes `OpenTLV 0.1.0`
as a stable Release. Its body includes the link to the prerelease.
