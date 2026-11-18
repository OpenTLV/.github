# GitHub Actions checks

The repository-local `Community quality` workflow runs pre-commit (community
validation, its regression tests, Markdown lint, and REUSE) and `pip check` on
the [configured Python version](../.python-version) on Ubuntu 24.04 x86-64.
It also verifies
[lockfile reproducibility](dependencies.md#reproducing-and-updating-the-lock)
and runs actionlint 1.7.12 and zizmor 1.32.0.
Every pull request, push to `main`, and manual dispatch runs the same workflow,
without path filters or separate orchestration. Analyzer failures fail the job.

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

The workflow audit for issue #12 found one workflow, `quality.yml`, with:

- Explicit `contents: read` permissions and no write permissions or OIDC grants.
- Official checkout and setup-python actions pinned to full commit SHAs;
  checkout uses `persist-credentials: false`.
- `pull_request`, main-branch `push`, and manual triggers; no
  `pull_request_target` or privileged `workflow_run` execution of PR code.
- No secrets, personal access tokens, environments, or tokens passed to scripts.
- No untrusted PR titles, bodies, branch names, or other event values expanded
  into shell commands.
- GitHub-hosted ephemeral runners, no shared workflow cache or artifact handoff,
  and a ten-minute job timeout.

Concurrency is grouped by workflow, event, and ref. New PR runs cancel older runs for the same
PR; pushes and manual runs are not canceled by that policy.

PRs execute contributor-controlled checks in an unprivileged job. Keep that
boundary when adding steps: never expose secrets or privileged tokens to PR code.
Analyzer installation uses public downloads, and zizmor runs explicitly offline
without a token. Offline analysis omits GitHub API-dependent checks such as
online reference resolution; it does not establish an action's provenance or
replace review of action updates and executable scripts. No SARIF upload or
`security-events: write` permission is needed.

## Suppressions and updates

There are currently no actionlint or zizmor finding suppressions. Fix findings
first. If an exception is necessary, use the narrowest rule and location, record
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
