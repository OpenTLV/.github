# Repository governance baseline

This is the source of truth for the proposed OpenTLV governance baseline under
[issue #10](https://github.com/OpenTLV/.github/issues/10). It applies to new,
eligible repositories, starting with OpenTLV/.github. It is a proposal for review,
not evidence of enabled GitHub settings. Applying or changing settings requires
separate maintainer approval. Never rewrite main, force-push, or bypass protection
to implement or test this baseline.

Keep audit reports and evidence snapshots outside version control, for example
under the ignored `.cache/governance-audits/` directory. Record review outcomes
in the tracking issue. Audit snapshots do not redefine this baseline.

## GitHub Free scope and ownership

GitHub Free is the declared plan for this work; billing was not inspected.
Recheck eligibility when a repository's plan or visibility changes.

| Control | Preferred scope on GitHub Free | Boundary |
| --- | --- | --- |
| Branch rulesets or classic protection | Each public repository | Public Free repositories support these controls; do not assume the same for private Free repositories |
| Organization-wide branch rulesets | Not available under the declared Free plan | Organization rulesets require Team or Enterprise; apply the baseline per eligible repository |
| Actions allow policy and restricted token defaults | Organization Actions settings | Inspect owner-visible controls, then inventory repository exceptions; do not infer policy from workflow files |
| Dependency and security features | Organization security configuration or bulk/default settings where offered, otherwise each repository | Check feature eligibility and resulting repository state; defaults for new repositories do not prove coverage of existing or transferred repositories |
| Merge methods and required check names | Each repository | Preserve project-specific checks and merge history |
| Community guidance | Public OpenTLV/.github defaults | Community inheritance does not install rulesets, workflows, or security settings |

Sources: [repository ruleset availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets),
[organization ruleset plans](https://docs.github.com/en/organizations/managing-organization-settings/creating-rulesets-for-repositories-in-your-organization),
[organization Actions settings](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization),
and [organization security management](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/managing-security-and-analysis-settings-for-your-organization).

## Proposed main branch controls

Use a repository branch ruleset targeting `refs/heads/main`, or equivalent classic
protection if required. Avoid overlapping configurations with conflicting rules.

| Setting | Proposed value |
| --- | --- |
| Enforcement | Active only after separate approval and safe validation |
| Require signed commits | Enabled; verify every newly introduced commit, including bot commits |
| Require a pull request | Enabled |
| Required approving reviews | 0 for the current solo-maintainer workflow |
| Required Code Owner or last-push approval | Disabled while there is no independent reviewer; revisit when the team grows |
| Require conversation resolution | Enabled |
| Required checks | Project-specific successful checks from the expected GitHub App |
| Branch up to date before merge | Enabled; update through a signed merge commit when necessary |
| Force pushes and branch deletion | Blocked |
| Linear history | Disabled |
| Routine bypass actors | None; any exceptional bypass requires separate documented approval |
| Allowed PR merge method | Regular merge commit; preserve all branch commits and their parent relationships |

For OpenTLV/.github require `quality (3.10)` and `quality (3.12)`, produced by
GitHub Actions, app ID `15368`. Confirm these
names and source again on a fresh PR before making them required. Another
repository must select its own checks; do not copy these names blindly.

Keep **Allow merge commits** enabled. Propose disabling squash and rebase merge
methods for this history-preserving policy. Do not apply that change without
approval. Keep PR, Main, and Full
orchestrators repository-local if a project uses them. This repository currently
needs only its Community quality workflow; do not add orchestrators or reusable
workflows without demonstrated duplication.

Rule semantics: [available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).
Signed history must be checked through GitHub verification records, not just an
author name, a `Signed-off-by` line, or a local signature whose key is untrusted.
GitHub rebase-and-merge creates modified commits without preserving their
signature verification; regular merges retain the original commits.
[Signature verification reference](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification).

## Actions and security controls

Prefer organization Actions policy: restrict allowed actions to reviewed
publishers/actions, require full commit SHAs where the control is available,
use restricted default GITHUB_TOKEN permissions, and disable workflow-created
or approved PRs unless an approved automation needs them. Inventory exact
exceptions for each repository, including fork-workflow approvals and runner
access. Keep untrusted PR work on GitHub-hosted runners without privileged
secrets. A default token setting is not a permission ceiling: review explicit
workflow and job permissions as well.

Review reusable-workflow references separately: the platform's full-SHA action
restriction still allows reusable workflows referenced by tags.

In OpenTLV/.github retain `contents: read`, `persist-credentials: false`, and
full-SHA action pins. Review changes to executable hooks and dependencies as
code. Do not expose tokens or secret values in audit evidence; record only
whether secret scopes and access policies were inspected and approved.
[Actions policy reference](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization).

Dependency graph, Dependabot alerts/security updates, and private vulnerability
reporting must be inspected separately from committed configuration. Their
enablement and UI acceptance work remain tracked in #1/#2 through the
[adoption guide](adoption.md); do not create competing completion checklists here.

CodeQL is eligible for public repositories and supports this repository's Python
helpers and GitHub Actions workflows. It is a reasonable optional addition for
review, not a reason to add another orchestrator. Check default setup before
proposing advanced setup so scans are not duplicated. Absence of a CodeQL YAML
file does not prove that default setup is disabled. Product/visibility limits
must be rechecked for private repositories.
[CodeQL reference](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning).

## Reproduce an audit

Use read-only APIs or an authenticated owner-visible settings page. The optional
GitHub CLI commands below require the caller's existing authorized session; do
not paste credentials into reports. Replace OWNER/REPO and SHA with the target
repository and the captured immutable main commit. Record pagination and errors.

```sh
gh api repos/OWNER/REPO
gh api repos/OWNER/REPO/branches/main
gh api 'repos/OWNER/REPO/rulesets?includes_parents=true'
gh api repos/OWNER/REPO/branches/main/protection
gh api repos/OWNER/REPO/actions/permissions
gh api repos/OWNER/REPO/actions/permissions/workflow
gh api repos/OWNER/REPO/actions/permissions/selected-actions
gh api 'repos/OWNER/REPO/commits/SHA/check-runs?per_page=100' --paginate
gh api 'repos/OWNER/REPO/commits?sha=SHA&per_page=100' --paginate \
  --jq '.[] | {sha, parents: [.parents[].sha], verified: .commit.verification.verified, reason: .commit.verification.reason}'
```

Owners can additionally inspect `orgs/OWNER/actions/permissions`,
`orgs/OWNER/actions/permissions/workflow`, and
`orgs/OWNER/actions/permissions/selected-actions`. Capture allowed actions and
fork/runner policies in the UI where needed. Review secret access scopes without
printing secret values. Read security enablement from Advanced Security settings.

A denied or unsupported endpoint means **Unavailable to inspect**, not disabled.
Missing enablement evidence means **Not confirmed**. Use **Confirmed** only for a
returned API value, versioned configuration, or dated UI evidence. Keep workflow
permissions separate from repository and organization defaults.

## Application and safe enforcement verification

1. Audit each eligible new repository first. Save date, visibility, main SHA,
   signature records for all reachable commits, merge methods, checks, rulesets,
   bypass actors, Actions policies, and security settings. Exclude legacy repos.
2. Prepare a settings diff against this baseline, list unavailable evidence and
   exceptions, and obtain separate approval before any settings mutation.
3. If using ruleset export/import, review a repository-specific exported JSON
   file, target refs, check-source IDs, and bypass entries before creation.
   Importing or committing a JSON file is not proof of active enforcement.
4. Validate the approved configuration in an authorized disposable repository
   or sandbox branch with equivalent rules. Confirm unsigned updates and direct
   pushes are rejected, missing checks block merge, and a signed PR with passing
   checks can use a regular merge. Test deletion/force-push rejection only on
   authorized disposable refs, never main. Do not bypass rules for the test.
5. Inspect the new merge commit and every introduced commit through GitHub's
   verification API. Include a genuine Dependabot update when available; do not
   assume one historic verified bot commit proves all future updates are signed.
6. Re-read active production settings and bypass actors, capture dated evidence
   and approval references, then perform a normal signed PR/merge. If safe
   mutation tests were not authorized, record enforcement as unverified.
7. Compare new main ancestry and signatures to the previous snapshot; investigate
   unsigned commits without rewriting main. Review the baseline after team,
   workflow, plan, visibility, or status-check changes.

Track settings changes and separately approved enforcement validation in
[issue #10](https://github.com/OpenTLV/.github/issues/10). Do not mark the baseline
enforced until the corresponding evidence exists.
