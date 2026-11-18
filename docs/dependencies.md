# Python dependency integrity

## Policy and audit

The quality workflow installs `requirements-dev.txt` with pip's
hash verification. Every selected direct and transitive Python dependency has
an exact version and approved SHA-256 hashes. Missing pins, missing hashes, or
mismatched downloads fail installation. Wheels are required for all packages
except the explicitly reviewed REUSE source-build exception below.

REUSE 5.1.1's release has no compatible wheel for the supported environments.
`requirements-build.txt` pins and hashes its Poetry Core 2.2.1 backend, which has
no Python dependencies. CI installs that wheel first, then installs the full lock
with `--no-build-isolation --only-binary=:all: --no-binary=reuse`. This permits
only REUSE's hash-checked source archive and prevents pip from downloading
unlocked build dependencies. The backend is also included in the full graph.
This verifies source inputs, not a bit-for-bit reproducible locally built wheel.
A future REUSE update with compatible wheels can remove this exception.

Previously, only pre-commit, REUSE, and PyYAML were directly pinned. Their
transitive dependencies were resolved at installation, and the three local Python
hooks repeated unlocked installs in isolated environments. They now use
`language: system` to run from the already installed development environment.
Activate the repository virtual environment before invoking hooks, including
commits from an editor; dependencies are no longer installed automatically for
these hooks. Missing tools fail the checks.

The development graph includes pre-commit's environment helpers, REUSE's license
parsing and templating dependencies, PyYAML, and Python-version-specific branches.
`requirements-dev.in` holds direct pins; `requirements-dev.txt` is the generated
full graph. Existing zizmor wheel hashes and actionlint archive verification
remain separate and unchanged; see [GitHub Actions checks](actions-checks.md).

## Supported environments

The validation matrix is CPython 3.10 and 3.12 on Ubuntu 24.04 x86-64 in CI.
Windows x86-64 with those Python versions is supported for local development.
The universal lock includes environment markers so each interpreter selects its
compatible dependency versions. Generation uses Python 3.10 as the lower bound;
this does not claim validation of every newer interpreter or platform.

The build backend uses a universal Python wheel. The lock generator's approved
wheel hashes cover Linux and Windows x86-64.
Other platforms require review of wheel availability and approved hashes before
being added to the supported set. Use a fresh virtual environment for validation
so preinstalled packages cannot hide missing requirements. pip does not remove
unrelated packages from an existing environment, and may skip already satisfied
packages without rechecking their installed bytes.

## Reproducing and updating the lock

Use the uv version pinned in `requirements-lock.txt`. Its universal pip compiler
produces a pip-compatible requirements file with
the full graph, markers, and hashes from package-index metadata. This avoids
maintaining separate Linux and Windows locks. uv is a maintainer-only generator;
ordinary contributors and CI install the resulting lock with pip.

Create a separate virtual environment and activate it:

```sh
python -m venv .cache/lock-generator
```

Use `. .cache/lock-generator/bin/activate` on POSIX or
`.cache\lock-generator\Scripts\Activate.ps1` in PowerShell. Then run:

```sh
python -m pip install --require-hashes --only-binary=:all: -r requirements-lock.txt
uv --no-config pip compile --universal --python-version 3.10 --generate-hashes --only-binary=:all: --no-binary=reuse --output-file requirements-dev.txt requirements-dev.in
```

Run the compiler without package-index environment overrides so it uses the
default PyPI index.

Regeneration retains existing pins where possible. For deliberate updates, edit
direct pins in `requirements-dev.in`, then add `--upgrade` to the compiler
command to refresh the graph, or `--upgrade-package <name>` for a targeted update.
Do not hand-edit generated versions or hashes. When updating the build backend,
update its exact pin and approved wheel hash in `requirements-build.txt` before
regenerating the full graph. Review the diff, dependency
additions, environment markers, release notes, and upstream artifact metadata.
Hashes protect approved bytes; they do not prove a package is trustworthy.

When updating uv itself, update its exact version and approved wheel hashes in
`requirements-lock.txt` together and review the release. The generator has no
Python dependencies.

Validate each supported interpreter in a fresh environment with:

```sh
python -m pip install --require-hashes --only-binary=:all: -r requirements-build.txt
python -m pip install --require-hashes --no-build-isolation --only-binary=:all: --no-binary=reuse -r requirements-dev.txt
python -m pip check
pre-commit run --all-files
```

Also run the workflow analyzers when changing the workflow. Regenerate a second
time with the same generator and inputs and confirm the lock has no diff.
Keep the existing Python CI matrix, required check names, action SHAs, and
analyzer integrity checks intact. Review updates monthly and when relevant
security fixes appear, as part of [tooling maintenance](development.md#tooling-and-updates).

## Remaining installation boundaries

- The Python interpreter, bundled pip/venv bootstrap (including seeded
  setuptools on Python 3.10), GitHub-hosted runner tools,
  and setup-python downloads are outside the Python requirements lock. We do not
  add an unverified pip upgrade. CI retains SHA-pinned official setup/checkout
  actions, read-only permissions, and disabled checkout credential persistence.
- The Markdown hook still installs from a reviewed full Git commit SHA and uses
  the pinned Node.js 24.11.1 runtime. Its npm dependency resolution and Node
  download are outside pip hash verification and are not a repository-owned npm
  lock. Keeping the existing isolated hook avoids adding a second JavaScript
  dependency-management system solely for one linter. Review hook/runtime
  updates and retain the pinned source revision; evaluate npm locking separately
  if this tooling grows. The Python nodeenv helper itself is in the Python lock.
- Developer-installed unrelated tools and packages are outside this guarantee.
  Do not install unlocked extras into the CI environment or add Python
  `additional_dependencies` to hooks without extending this policy and lock.

See [uv's locking documentation](https://docs.astral.sh/uv/pip/compile/) and
[pip's secure-install guidance](https://pip.pypa.io/en/stable/topics/secure-installs/)
for the underlying resolver and hash-checking behavior.
