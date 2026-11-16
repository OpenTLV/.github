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

The shared chooser offers Bug report for reproducible defects, Feature request
for new capabilities, and Chore for maintenance, tooling, or documentation work.
Blank issues are disabled for general contributors. GitHub still offers its
built-in **Blank issue** option, labeled **Maintainers only**, to users with
Write, Maintain, or Admin access. This setting is not an Admin-only permission
boundary. Component-specific forms belong in the consuming repository;
maintainers must include every form they want to retain in that local set.

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

## Dependency security settings

In each repository's **Settings > Advanced Security** page (the navigation may
also group this under **Security and quality**), enable and verify:

1. **Dependency graph** to inventory supported dependency manifests and lockfiles.
2. **Dependabot alerts** to report known vulnerabilities in that inventory.
3. **Dependabot security updates** to propose fixes for vulnerable dependencies.

These are repository settings. They are not enabled by inheriting community
files or by adding `.github/dependabot.yml`. That file configures scheduled
version updates; in this repository it schedules monthly GitHub Actions updates.
Security alerts and security updates require their own settings. See GitHub's
[repository security quickstart](https://docs.github.com/en/code-security/getting-started/quickstart-for-securing-your-repository)
and [Dependabot security update setup](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates).

After enabling the settings, inspect **Insights > Dependency graph** for the
expected dependencies and its **Dependabot** tab for configured version-update
jobs. Check **Security and quality > Dependabot alerts** for scan results; an
empty alert list alone does not prove that scanning is enabled. Record the
repository, date, enabled settings, and verification evidence below. Review any
proposed dependency updates against paired pins in requirements-dev.txt and
.pre-commit-config.yaml before merging them.

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
| Default forms | Open the consuming repository's new-issue chooser as a general contributor | Bug report, Feature request, Chore, and contact links appear; blank issue is hidden |
| Maintainer blank issue | Open the same chooser with Write, Maintain, or Admin access | Built-in Blank issue option appears with the Maintainers only label |
| Form validation | Choose each form and attempt submission without required fields | Required fields prevent submission; no issue needs to be created |
| Valid submissions | In the agreed public test repository, submit one clearly marked test issue per form with all required fields completed | Each issue is created with the supplied fields; record its URL and close it as a test |
| Local form override | On the test repository's default branch add a valid local form with a unique name | Only local forms appear; shared Bug report, Feature request, and Chore forms disappear |
| Configuration override | Replace that local form with a local config.yml containing blank_issues_enabled: true | Shared forms remain absent |
| Restore inheritance | Remove the test repository's local ISSUE_TEMPLATE directory | Shared forms return |
| Local policy override | Add a local CONTRIBUTING.md with a unique marker | GitHub contribution link resolves to the local policy |
| PR template | Open a new PR from a nonempty test branch without a local PR template | Shared template populates the description |
| Security reporting | Inspect Advisories as a non-maintainer after enabling reporting | Report a vulnerability is available |
| Dependency security | Inspect the repository's Advanced Security settings, dependency graph, and Dependabot pages | Dependency graph, Dependabot alerts, and security updates are enabled; dependency inventory and update jobs are visible |

Record date, repository, default-branch commit, observer, screenshots or URLs,
and results in the table below. If GitHub caches an old state, retry after it
refreshes and record the observed behavior. Restore test fixtures afterward.

Adding the Chore form and policy clarifications for issue #2 requires a new
deployment verification run. The historical results below cover the bootstrap
commit only; they do not verify the new form's rendering or submission behavior.

## Verification record

Bootstrap baseline, 2026-11-16: the live GitHub connector confirmed that
OpenTLV/.github and OpenTLV/opentlv are public, non-archived repositories with
default branch main. Local checkouts initially contain only README/LICENSE in
the community repository and LICENSE in opentlv. No available implementation or
release capabilities are asserted by the profile.

| Evidence | Status |
| --- | --- |
| Final merged commit `feea457affa5813e13874e2434538c76c3072aa1` | Verified on 2026-11-16: clean local checkout; `pre-commit run --all-files` and standalone `reuse lint` passed; REUSE covered 20/20 files |
| Community quality CI | [Run 43891801580](https://github.com/OpenTLV/.github/actions/runs/43891801580) passed on the same merged commit; job logs confirm both community-files and reuse hooks passed |
| Profile rendering on GitHub | Verified on 2026-11-16 in a separate signed-out headless Chrome session: headings, paragraphs, and links display correctly on the [organization overview](https://github.com/OpenTLV) |
| Public documentation links | All 17 unique HTTPS links in repository Markdown returned HTTP 200 on 2026-11-16; profile claims were checked against the live public repositories |
| Inherited conduct, contribution, and security policies | Verified on 2026-11-16 in [opentlv Community Standards](https://github.com/OpenTLV/opentlv/community); [security policy](https://github.com/OpenTLV/opentlv/security/policy) displays the shared policy, while the consuming repository's tree contains only LICENSE |
| Inherited support links and PR template | Pending signed-in UI verification |
| Issue forms, required fields, and local template/config overrides | Pending signed-in UI verification; the consuming repository's issue chooser redirects signed-out requests to login |
| Private vulnerability reporting setting and non-maintainer visibility | Pending authenticated setup and verification; public advisory pages alone do not establish whether reporting is enabled |
| Dependency graph | Disabled in the maintainer-provided screenshot on 2026-11-16; enabling and verifying the repository setting remains pending |
| Dependabot alerts and security updates | Pending authenticated setup and verification; the committed version-update configuration does not establish these settings |

The local verification artifacts are saved under the ignored
`.cache/deployment-verification/` directory: `profile.png`, public page HTML,
`results.json`, and `links.json`. They are local evidence, not published assets.
The checks above apply to the merged implementation commit, before this
verification-record update.

Authenticated UI checks could not be completed in this session because both
available Computer Use entry points reported that the native pipe was
unavailable. No test issues, test repositories, or override fixtures were
created, and no reporting settings were changed. Complete the remaining checks
using the procedure above when authenticated browser access is available.

Do not close the parent issue as complete until these checks have recorded
evidence and the repository-local quality checks pass.
