# Adopting shared community defaults

## Scope and precedence

GitHub reads supported defaults from the public `OpenTLV/.github` repository's
default branch. Local unpublished changes do not activate them. Policies live at
the repository root; issue forms and their configuration live in
`.github/ISSUE_TEMPLATE/`, and the PR template lives at
`.github/PULL_REQUEST_TEMPLATE.md`.

For each supported policy, GitHub checks the target repository's `.github/`, root
and `docs/` locations, in that order. A local file wins for that policy; if absent,
GitHub looks for the corresponding default in this repository. Local policies
are not combined with defaults. Use explicit links when both shared guidance and
component-specific instructions are needed.

Issue templates are a set: **any file** in a repository's own
`.github/ISSUE_TEMPLATE/`, including `config.yml` alone, suppresses the entire
default set and its configuration. Removing one local form does not inherit just
the missing form. A local PR template also takes precedence over the default.
Check alternative PR template locations and named templates before removing files.

Defaults do not appear in component Git trees, clones, archives or packages.
Retain LICENSE, SPDX/REUSE metadata, packaged notices, build/test instructions and
CI in each repository. This repository's pre-commit and REUSE configurations
validate its own files only. Private vulnerability reporting and notification
subscriptions are separate repository/account settings.

Reference: [GitHub default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).

## Local inventory checked on 2026-10-27

The following table records tracked files in the local checkouts at the listed
commits. `default` means no corresponding local file was found and the proposed
shared file is expected to apply **after publication**. This is a source inventory
and review against GitHub's documented precedence, not proof of rendered GitHub
UI behavior or current remote branch contents. Recheck when adopting a component.

| Repository | Local commit | Contributing | Conduct | Security | Support | Issues | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `opentlv` | `4cd674fe` | local | local | local | default | local set | local |
| `opentlv-cli` | `724aac98` | local | default | default | default | local set | local |
| `opentlv-lua` | `e2b65d51` | default | default | default | default | default set | default |
| `opentlv-python` | `74d7ed75` | local | default | default | default | default set | default |
| `opentlv-rust` | `ee2d1f4e` | default | default | default | default | default set | default |
| `opentlv-go` | `bc73a510` | default | default | default | default | default set | default |
| `opentlv-js` | `42687fb3` | default | default | default | default | default set | default |
| `opentlv-docs` | `a6402b9e` | default | default | default | default | default set | default |
| `opentlv-workspace` | `e74ea38c` | local | local | local | default | local set | local |

Core and Workspace keep their local contribution, conduct and security policies;
Core, CLI and Workspace keep their local issue forms and PR templates. The new
defaults must not silently replace their build instructions or support windows.
No component policy or template is removed by this change.

## Adoption and validation checklist

1. Merge and publish the shared files on the public `.github` default branch.
   Check that shared links resolve there. The issue forms intentionally use
   absolute policy/support links and do not depend on repository labels or assignees.
2. Inspect the target repository's `.github/`, root and `docs/` community files,
   its issue-template directory (including config-only overrides), and all PR
   template locations. Record the commit being checked.
3. Before removing a local policy, retain technical instructions and release/support
   details in owner-maintained documents and link them from a small local entry
   point where necessary. A retained local CONTRIBUTING file should explicitly
   link the shared guidelines if the repository wants to use both.
4. For a repository with no local policies/templates, inspect the community
   standards page, issue chooser and new-PR preview after publication. Expect the
   shared policy links, Bug/Chore plus Blank, security/support contact links and
   the generic PR body. Do not submit test issues or PRs merely to inspect forms.
5. For Core or Workspace, inspect the same surfaces and verify their local
   contribution/security content, issue chooser and PR template remain in use.
   For CLI or Python, verify each retained policy separately: one local file does
   not suppress unrelated shared policy types. Check SUPPORT fallback as well.
6. If replacing an issue-template set in a follow-up change, verify both the
   complete local set and the no-local-files case. Keeping `config.yml` alone
   still blocks all shared forms. Do not delete local files just to demonstrate this.
7. Verify clone/package contents still include required licenses and notices.
   Run that repository's existing validation; do not add a new CI system for defaults.
8. Record hosted UI results separately from local lint/source checks. Update the
   Workspace community pin only after the reviewed `.github` commit is published;
   workspace pins do not control which defaults GitHub displays.

Repository adoption and licensing normalization are tracked separately in
[Core #715](https://github.com/OpenTLV/opentlv/issues/715),
[CLI #23](https://github.com/OpenTLV/opentlv-cli/issues/23),
[Python #33](https://github.com/OpenTLV/opentlv-python/issues/33),
[Rust #31](https://github.com/OpenTLV/opentlv-rust/issues/31),
[Go #29](https://github.com/OpenTLV/opentlv-go/issues/29),
[Lua #38](https://github.com/OpenTLV/opentlv-lua/issues/38),
[JS #30](https://github.com/OpenTLV/opentlv-js/issues/30) and
[Docs #125](https://github.com/OpenTLV/opentlv-docs/issues/125), under
[Core epic #703](https://github.com/OpenTLV/opentlv/issues/703).

## Private vulnerability reporting

On 2026-10-27, private vulnerability reporting was enabled separately through the
GitHub API for all ten repositories listed below. Each update returned HTTP 204
and a subsequent GET returned `enabled: true`. This records repository settings,
not publication of these policies, a test report, a published advisory or verified
maintainer notification delivery. Recheck the live setting before relying on it.

An administrator enables private vulnerability reporting for each public
repository in **Settings > Advanced Security > Private vulnerability reporting**.
The API equivalent is `PUT /repos/OpenTLV/{repository}/private-vulnerability-reporting`;
verify with `GET` on the same endpoint and require `enabled: true`.
The scope is Core, CLI, Lua, Python, Rust, Go, JS, Docs, Workspace and `.github`.
Enabling the feature does not publish an advisory, grant additional collaborators
access or subscribe a maintainer to notifications.

Maintainers must separately check their security-alert watch subscriptions and
notification preferences, and verify advisory access for the owners who will triage
reports. Inspect the **Report a vulnerability** form while signed in without
submitting a test report. Recheck these settings when adding a repository or
changing its maintainers/visibility.

Reference: [GitHub private vulnerability reporting settings](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).

## Attribution and local checks

Shared guidance and templates are adapted from the existing Core/Workspace
policies. The Code of Conduct retains Contributor Covenant 2.1 attribution,
Mozilla's enforcement-ladder credit and CC BY 4.0 metadata. It is excluded from
the MIT annotation block; original OpenTLV files keep their accurate MIT notices.

Use the contributor environment described in [README](../README.md) and run
`python -m pre_commit validate-config`, `python -m pre_commit run --all-files`
and `python -m reuse lint`. Stage new files before `--all-files`, or validate a
disposable Git copy containing the complete proposed tree. Review local links,
unique issue-form field IDs, required input fields and the absence of label or
assignee dependencies. These checks do not establish hosted fallback behavior.
