# Adopting the community defaults

## What GitHub inherits

Keep OpenTLV/.github public and publish these files on its default branch.
GitHub can supply missing contribution, conduct, security, support, issue
template, and pull request template files to organization repositories.
Inherited files are displayed by GitHub; they do not become files in a consuming
repository's clone, package, or history.

A repository's corresponding local community file wins. For supported community
files with multiple locations, GitHub checks `.github/`, root, then `docs/`.
A valid local `.github/ISSUE_TEMPLATE` form/template or configuration replaces
the entire organization's default issue-template directory; GitHub does not
merge individual inherited forms with local forms. Copy every form you want to
keep when defining local templates. Our forms do not assign labels or people,
so consuming repositories need no matching labels or accounts.

The organization profile comes from `profile/README.md`. A project's README,
license, CI workflows, branch protection, permissions, release process, and
security settings remain local. This repository's pre-commit, REUSE, editor,
and CI configurations are not automatically inherited. Adopting a check requires
an explicit change reviewed in the consuming repository.

See GitHub's authoritative
[default community file rules](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
and [issue template guidance](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository).

## Maintainer onboarding

1. Review the defaults against the destination project's requirements. Add local
   policies when ownership, support windows, contacts, or contribution steps differ.
2. Keep the project's own license and notices. Never rely on an inherited license.
3. Enable private vulnerability reporting in the affected repository's
   **Settings > Security > Advanced Security** settings (the layout may vary).
   Follow the current
   [GitHub setup instructions](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
   Check **Security > Advisories** from a non-maintainer account for the reporting
   button. Do not submit a fabricated vulnerability to test delivery.
4. Publish a monitored private reporting contact locally if private reporting is
   unavailable. Document release support locally when releases exist.
5. Review issue and pull request creation screens and links as described below.

## Deployment acceptance procedure

These are manual checks against GitHub's behavior. Local lint cannot prove
inheritance, rendering, permissions, or security settings. Perform them after
the proposed files land on OpenTLV/.github's default branch. Use a maintainer-owned
public test repository in the organization; avoid changing another project's
policies or creating test issues without agreement.

| Check | Procedure | Expected result |
| --- | --- | --- |
| Profile | Visit the organization overview signed out | Profile displays with working public links and accurate status |
| Inherited policies | In a public repository with no corresponding local files, inspect Community Standards and contribution/security/support links | Links lead to these defaults |
| Default forms | Open the consuming repository's new-issue chooser | Bug report, Feature request, and contact links appear |
| Form validation | Choose each form and attempt submission without required fields | Required fields prevent submission; no issue needs to be created |
| Local form override | On the test repository's default branch add a valid local form with a unique name | Only local forms appear; shared bug/feature forms disappear |
| Configuration override | Replace that local form with a local config.yml containing blank_issues_enabled: true | Shared forms remain absent |
| Restore inheritance | Remove the test repository's local ISSUE_TEMPLATE directory | Shared forms return |
| Local policy override | Add a local CONTRIBUTING.md with a unique marker | GitHub contribution link resolves to the local policy |
| PR template | Open a new PR from a nonempty test branch without a local PR template | Shared template populates the description |
| Security reporting | Inspect Advisories as a non-maintainer after enabling reporting | Report a vulnerability is available |

Record date, repository, default-branch commit, observer, screenshots or URLs,
and results in the table below. If GitHub caches an old state, retry after it
refreshes and record the observed behavior. Restore test fixtures afterward.

## Verification record

Bootstrap baseline, 2026-11-16: the live GitHub connector confirmed that
OpenTLV/.github and OpenTLV/opentlv are public, non-archived repositories with
default branch main. Local checkouts initially contain only README/LICENSE in
the community repository and LICENSE in opentlv. No available implementation or
release capabilities are asserted by the profile.

| Evidence | Status |
| --- | --- |
| Profile rendering on GitHub | Pending deployment |
| Inherited policies and PR template in a consuming public repository | Pending deployment |
| Required fields and local template/config overrides | Pending deployment |
| Private vulnerability reporting setting and non-maintainer visibility | Pending maintainer setup and verification |

Do not close the parent issue as complete until these checks have recorded
evidence and the repository-local quality checks pass.
