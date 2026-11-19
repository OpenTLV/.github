# GitHub Actions checks

The repository-local `Community quality` workflow runs two independent jobs
in parallel on Ubuntu 24.04 x86-64 with the
[configured Python version](../.python-version).

- `quality` checks
  [lockfile reproducibility](dependencies.md#reproducing-and-updating-the-lock)
  and runs `pip check` and pre-commit (community validation, regression tests,
  Markdown lint, and REUSE).
- `workflow-analyzers` runs actionlint 1.7.12 and zizmor 1.32.0.

The workflow runs on pull requests, pushes to `main`, manual dispatch, and every
Monday at 06:23 UTC. Both jobs report on pull requests targeting `main`.
The [release workflow](../.github/workflows/release.yml) also calls this workflow
at the dispatch commit and requires both job conclusions to be `success`.
The [governance baseline](governance.md#main-branch-controls) lists
the required-check policy and the last verified ruleset state.
The job split is recorded in [issue #46](https://github.com/OpenTLV/.github/issues/46).

## Weekly run and notifications

GitHub runs the schedule from the default branch. It routes scheduled workflow
notifications to the account that last changed the cron expression. A maintainer
who re-enables a disabled workflow becomes the recipient instead. Delivery depends
on that account's GitHub Actions notification settings. See GitHub's
[workflow notification rules](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs).
The schedule and online audit rollout are recorded in
[issue #47](https://github.com/OpenTLV/.github/issues/47).

## Local reproduction

Run from this repository's root with its virtual environment activated.
Install zizmor from the hash-checked wheel requirements:

```sh
python -m pip install --require-hashes --only-binary=:all: -r requirements-actions.txt
zizmor --offline --strict-collection --collect=workflows .
```

For Linux x86-64, run the download, checksum verification, extraction, and
actionlint commands verbatim from `.github/workflows/quality.yml`.
On Windows, run the same commands in Ubuntu 24.04 under WSL 2.

actionlint discovers all `.yml` and `.yaml` workflows in `.github/workflows`.
Its optional ShellCheck and Pyflakes integrations are explicitly disabled so
results do not depend on tools preinstalled on a runner or developer machine;
workflow syntax, expressions, action inputs, and embedded-script injection
checks remain enabled. zizmor collects all workflows and fails on parsing
errors as well as findings at its default thresholds. No `--exit-codes` override,
severity filter, or `continue-on-error` weakens the checks.

The supplied hashes cover Linux x86-64.

## Security review and limits

The `quality.yml` workflow uses these controls:

- Explicit `contents: read` permissions and no write permissions or OIDC grants.
- Official checkout and setup-python actions pinned to full commit SHAs;
  checkout uses `persist-credentials: false`.
- `pull_request`, main-branch `push`, scheduled, and manual triggers.
- A short-lived `GITHUB_TOKEN` mapped to `GH_TOKEN` only in the online zizmor step.
- No untrusted PR titles, bodies, branch names, or other event values expanded
  into shell commands.
- GitHub-hosted ephemeral runners, no shared workflow cache or artifact handoff,
  and a ten-minute job timeout.

New runs for the same pull request share a concurrency group and cancel older
runs. Each push to `main`, scheduled run, and manual dispatch uses its own
`github.run_id`. Successive merges can therefore run their online audits in
parallel.

PRs execute contributor-controlled checks in an unprivileged job. Keep that
boundary when adding steps: never expose secrets or privileged tokens to PR code.
Pull requests and standalone manual quality runs use zizmor offline. Pushes to
`main`, scheduled runs on `main`, and release candidates on `main` run zizmor
online. The online step uses the built-in
token with the workflow's `contents: read` permission for checkout and GitHub
API lookups. The workflow uses public action references and grants no additional
permissions. See [zizmor's token requirements](https://docs.zizmor.sh/usage/#github-api-application-programming-interface-token-permissions).

Online mode enables `impostor-commit` for SHA provenance and
`ref-version-mismatch` for version comments that disagree with their pins.
The `stale-action-refs` rule checks whether a pin points to a tag and reports
untagged pins under zizmor's pedantic persona.
See the [zizmor audit rules](https://docs.zizmor.sh/audits/).

## Suppressions and updates

The release workflow uses `./.github/workflows/quality.yml` so actionlint 1.7.12
can validate its inputs. Its single `self-repository` exception covers that
call. Both `./` and `$/` load the workflow at the caller's exact commit.
Revisit the exception when updating actionlint.
[GitHub reusable workflow reference](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows#calling-a-reusable-workflow).

Fix findings first. If an exception is necessary, use the narrowest rule and location, record
the security rationale beside it, and describe the remaining risk in the PR.
Do not add blanket ignores or disable checks to make CI green.

See [tooling and updates](development.md#tooling-and-updates) for update ownership,
review cadence, and other tool pins. For actionlint, update the version, archive
URL, and hard-coded SHA-256 in CI together.
Compare hashes with the
[upstream actionlint release](https://github.com/rhysd/actionlint/releases);
verify release attestations when available. Never fetch a mutable installer or
accept a freshly downloaded checksum as the sole integrity check in CI.

Update the zizmor version and approved wheel hashes together in
`requirements-actions.txt`, using the release's
[PyPI metadata](https://pypi.org/pypi/zizmor/json). Keep binary-only, hash-required
installation; review any new dependencies before accepting them. These tools
are separate from `requirements-dev.txt` and introduce no transitive Python
dependencies. Run both analyzers and the existing quality checks on every update,
review changed findings, and update this guide's versions and audit assumptions.

See the upstream [actionlint usage guide](https://github.com/rhysd/actionlint/blob/main/docs/usage.md)
and [zizmor usage guide](https://docs.zizmor.sh/usage/) for rule and CLI details.
