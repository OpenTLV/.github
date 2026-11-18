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
keep when defining local templates.

Bug report, Feature request, and Chore default to `bug`, `enhancement`, and
`chore`, respectively. Create those labels in each consuming repository that
uses the shared forms. GitHub applies a default label only when that label
already exists in the repository where the issue is filed.

The shared chooser offers Bug report for reproducible defects, Feature request
for new capabilities, Task for defined implementation work, Chore for maintenance,
tooling, or documentation work, and Epic for larger coordinated work using native
GitHub sub-issues. Chore's Validation field is optional; existing required fields
are unchanged.
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

Branch protections, merge policy, Actions governance, and their inspection limits
are documented in the [governance baseline](governance.md). That document is a
proposal requiring separate approval; community defaults do not enforce it.

1. Review the defaults against the destination project's requirements. Add local
   policies when ownership, support windows, contacts, or contribution steps differ.
2. Keep the project's own license and notices. Never rely on an inherited license.
3. Enable private vulnerability reporting in the affected repository's
   **Settings > Security > Advanced Security** settings (the layout may vary).
   Follow the current
   [GitHub setup instructions](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
   Check **Security > Advisories** from a non-maintainer account for the reporting
   button. Do not submit a fabricated vulnerability to test delivery.
4. Verify the private fallback and conduct-reporting routes described below.
   Document release support locally when releases exist.
5. Review issue and pull request creation screens and links as described below.

## Private reporting routes and verification

The responsible organization contact is
[@marekcingel](https://github.com/marekcingel), with the maintainer-designated
private contact [cingelmarekmt@gmail.com](mailto:cingelmarekmt@gmail.com).
The affected repository's private vulnerability form is primary, and the
[community repository's private form](https://github.com/OpenTLV/.github/security/advisories/new)
routes unavailable repository reporting or cross-repository findings centrally.
The email contact is an independent-of-GitHub fallback for security reports and
the direct private project contact for conduct concerns. A profile link identifies
the owner; it is not a private message channel.

On 2026-11-17, read-only checks of public repository metadata and
`GET /repos/{owner}/{repo}/private-vulnerability-reporting` returned:

| Repository | Visibility/state | Private vulnerability reporting |
| --- | --- | --- |
| OpenTLV/.github | Public, not archived; default branch `main` | `enabled: true` |
| OpenTLV/opentlv | Public, not archived; default branch `main` | `enabled: true` |

This confirms configured enablement on that date for these two repositories,
not every OpenTLV repository. It does not prove reporter-side form access,
notification delivery, monitoring, or response time. No report was submitted,
no settings were changed, and no vulnerability details or credentials were used.
The older baseline below is historical evidence; this check updates only private
reporting configuration status for the two named repositories.

Maintainers should keep these routes usable:

1. An owner/admin verifies private reporting in each eligible public repository
   and in the central fallback repository. Where a feature is unavailable for a
   visibility type or plan, record that limitation and verify the central route;
   inherited policies and organization configuration assignment are not proof.
2. Using a signed-in non-maintainer account, open **Security > Advisories** and
   inspect **Report a vulnerability** without submitting a fabricated finding.
   Record the date, repository, account role, result, and sanitized evidence URL
   or screenshot reference. This reporter-side check remains pending here.
3. The responsible contact confirms access to central private reports and the
   mailbox, and reviews notification preferences and monitoring arrangements.
   Recheck after access or maintainer changes. Email publication was explicitly
   authorized by the maintainer on 2026-11-17; mailbox delivery and GitHub
   notification delivery have not been tested. Do not send test messages or
   fabricated reports without a separately agreed verification procedure.
4. For conduct, inspect whether **Report to repository admins** is available to
   ordinary users and who receives it. Its availability and delivery in these
   repositories remain pending verification. Document GitHub Support's private
   abuse-reporting route as the platform fallback, not as an OpenTLV inbox.

Private vulnerability reporting is a feature of eligible public repositories;
do not assume equivalent availability in private/internal repositories. See
[GitHub setup guidance](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
No paid feature or repository setting is enabled by this documentation.

The published mailbox supplies the private fallback outside GitHub and a direct
project conduct route. Its designation does not establish tested delivery or a
response deadline. An independent project contact for conduct reports involving
the designated maintainer has not been appointed; the conduct policy explains
available escalation routes and that limitation. Do not redirect sensitive
reports to public issues or misuse security advisories for conduct complaints.
Track remaining verification in [issue #28](https://github.com/OpenTLV/.github/issues/28).

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
proposed dependency updates using the local
[tooling and update policy](development.md#tooling-and-updates) before merging them.

## Secret scanning and push protection

Secret scanning detects supported credential patterns after exposure; repository
push protection blocks supported matches before acceptance. Inspect both in
**Settings > Advanced Security**, under **Secret scanning** or **Secret Protection**
depending on the interface. Enabled alerts, no open alerts, or personal-account
push protection do not establish repository-wide push protection.

Prefer native secret-scanning alerts and repository push protection for eligible
public repositories. Public scanning is free; private/internal organization
repositories have different product and plan requirements. Verify entitlement
for additional detection or bypass controls. Do not purchase products or modify
settings without explicit maintainer approval. Sources:
[scanning availability](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning)
and [push protection behavior](https://docs.github.com/en/code-security/concepts/secret-security/push-protection).

Organization owners can use security configurations for eligible repositories
and defaults for new repositories. Inspect individual feature values and target
repositories; assignment alone does not prove enablement. Preserve the agreed
scope of new public repositories and verify existing repositories separately
from future defaults. See [security configurations](https://docs.github.com/en/code-security/how-tos/secure-at-scale/configure-organization-security/establish-complete-coverage/create-custom-configuration).

### Safe verification and evidence

Record the repository, effective scanning and push-protection settings,
organization configuration, and available bypass/alert-dismissal controls in the
tracking issue. Classify values as confirmed, not confirmed, or unavailable to
inspect. Keep snapshots outside Git in ignored `.cache/`. Never save raw alert
payloads, matched strings, or credentials in those snapshots.

After an approved change, refresh settings to verify persistence. Inspect scan
status privately in **Security and quality > Secret scanning**, recording only
sanitized status and coverage. Missing API fields do not mean disabled. An empty
alert list does not prove scanning completed or every possible secret is covered.

Never generate real credentials, publish leaks, bypass protection, or modify
main for testing. Settings evidence does not prove a blocked-push test. If a
test is needed, agree on an isolated scope and a provider-documented nonfunctional
test value first; otherwise record it as unperformed. Genuine historical block
events can provide sanitized evidence without manufacturing an exposure.

### Coverage limits and additional detectors

Native detection is pattern-dependent. Some token types and large or complex
pushes fall outside prevention coverage; later alerts are not prevention.
Review the current [detection limits](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-scope).
Record unavailable controls and their actual plan/visibility limitation before
choosing a mitigation. Do not infer entitlement from a configuration name.

For OpenTLV/.github, defer an additional local/CI detector until a concrete gap
is demonstrated. Verify native coverage first. Existing whitespace, Markdown,
YAML/JSON, and REUSE checks are not secret detectors.

A local detector could add pre-commit feedback, offline checking, or project
patterns. Those benefits must justify another pinned tool, pattern maintenance,
false positives, and exception review. CI-only detection happens after upload
and cannot undo a leak. If warranted, review coverage, license, updates,
sanitized output, and narrowly scoped exceptions before adding a detector.
Retain native protections and repository-local workflows; no additional
orchestrator is needed for this evaluation.

Alert handling follows the [security policy](../SECURITY.md#leaked-credentials-and-secret-scanning-alerts).
Approval boundaries follow the [governance baseline](governance.md). Live settings
and evidence are tracked in [issue #13](https://github.com/OpenTLV/.github/issues/13),
coordinated with #10.

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
| Default forms | Open the consuming repository's new-issue chooser as a general contributor | Bug report, Feature request, Task, Chore, Epic, and contact links appear; blank issue is hidden |
| Maintainer blank issue | Open the same chooser with Write, Maintain, or Admin access | Built-in Blank issue option appears with the Maintainers only label |
| Form validation | Choose each form and attempt submission without required fields | Required fields prevent submission; no issue needs to be created |
| Valid submissions | In the agreed public test repository, submit one clearly marked test issue per form with all required fields completed | Each issue is created with the supplied fields; record its URL and close it as a test |
| Default labels | Inspect the submitted Bug report, Feature request, and Chore issues in the consuming repository | The issues have `bug`, `enhancement`, and `chore`, respectively |
| Local form override | On the test repository's default branch add a valid local form with a unique name | Only local forms appear; all shared forms disappear |
| Configuration override | Replace that local form with a local config.yml containing blank_issues_enabled: true | Shared forms remain absent |
| Restore inheritance | Remove the test repository's local ISSUE_TEMPLATE directory | Shared forms return |
| Local policy override | Add a local CONTRIBUTING.md with a unique marker | GitHub contribution link resolves to the local policy |
| PR template | Open a new PR from a nonempty test branch without a local PR template | Shared template populates the description |
| Security reporting | Inspect Advisories as a non-maintainer after enabling reporting | Report a vulnerability is available |
| Dependency security | Inspect the repository's Advanced Security settings, dependency graph, and Dependabot pages | Dependency graph, Dependabot alerts, and security updates are enabled; dependency inventory and update jobs are visible |

Record date, repository, default-branch commit, observer, screenshots or URLs,
and results in the table below. If GitHub caches an old state, retry after it
refreshes and record the observed behavior. Restore test fixtures afterward.

Changes to forms and policies require deployment verification against the
changed default-branch commit. The baseline results below do not establish
rendering or submission behavior for the Chore form added in issue #2.

For issue #11, verify Task and Epic rendering and required-field validation in
an eligible consuming repository after deployment. Check that Chore can be
submitted with Validation empty, while its original required fields remain
required. Confirm security/support routing is still present. Record the tested
commit and observed behavior; previous form checks do not establish the behavior
of these new or changed forms.

## Verification record

The baseline below records observations from 2026-11-16 for merged commit
`feea457affa5813e13874e2434538c76c3072aa1`. It is dated evidence, not a statement
of current settings or verification of later changes. OpenTLV/.github and
OpenTLV/opentlv were confirmed public and non-archived, with `main` as their
default branch. The profile did not claim implementation or release capabilities.

### Recorded results

| Evidence | Recorded result |
| --- | --- |
| Local quality checks | A clean checkout of the baseline commit passed `pre-commit run --all-files` and a standalone `reuse lint`; REUSE covered 20/20 files |
| Community quality CI | [Run 43891801580](https://github.com/OpenTLV/.github/actions/runs/43891801580) passed on the baseline commit; job logs confirm both community-files and reuse hooks passed |
| Profile rendering on GitHub | Signed-out inspection of the [organization overview](https://github.com/OpenTLV) confirmed that headings, paragraphs, and links displayed correctly |
| Public documentation links | All 17 unique HTTPS links in repository Markdown returned HTTP 200; profile claims were checked against the public repositories |
| Inherited conduct, contribution, and security policies | [opentlv Community Standards](https://github.com/OpenTLV/opentlv/community) showed the inherited policies; the [security policy](https://github.com/OpenTLV/opentlv/security/policy) displayed the shared policy while the consuming repository's tree contained only LICENSE |

### Checks requiring authenticated verification

The following checks had no completed verification recorded in the baseline.
They remain pending in this record until new dated evidence is added. A public
page or an unavailable inspection does not establish an authenticated setting.

| Check | Recorded status and remaining work |
| --- | --- |
| Inherited support links and PR template | Pending signed-in UI verification using the deployment acceptance procedure |
| Issue forms, required fields, and local template/config overrides | Pending signed-in UI verification; signed-out access to the consuming repository's issue chooser redirected to login |
| Private vulnerability reporting setting and non-maintainer visibility | Pending authenticated setup and verification; public advisory pages alone do not establish whether reporting is enabled |
| Dependency graph | A maintainer-provided screenshot showed it disabled on 2026-11-16; enabling and verifying the repository setting remains pending in this record |
| Dependabot alerts and security updates | Pending authenticated setup and verification; the committed version-update configuration does not establish these settings |

The baseline verification did not create test issues, test repositories, or
override fixtures, and did not change reporting settings. Complete the pending
checks with the appropriate authorized accounts using the procedure above, then
record the date, tested commit, repository, and observed result. Do not mark
deployment acceptance complete until evidence for the required checks is
recorded and repository-local quality checks pass.

Keep sanitized verification artifacts outside Git in the ignored
`.cache/deployment-verification/` directory. Record public evidence URLs and
results here so the status can be understood without access to local files.
