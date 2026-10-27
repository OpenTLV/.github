# Contributing to OpenTLV

These are shared contribution guidelines for OpenTLV repositories that use the
organization defaults. Follow the target repository's README, development guides
and local contribution instructions for its build, tests and release process.

All project spaces follow the
[Code of Conduct](https://github.com/OpenTLV/.github/blob/main/CODE_OF_CONDUCT.md).
Report suspected vulnerabilities privately using the affected repository's
Security tab and the
[security policy](https://github.com/OpenTLV/.github/blob/main/SECURITY.md).

## Choose the owning repository

Use the [support directory](https://github.com/OpenTLV/.github/blob/main/SUPPORT.md)
to find the component owner. Core owns C/C++ behavior and public contracts;
standalone bindings and CLI own their adapters, packaging, tests and technical
manuals. Docs owns portal assembly, navigation and publication. Workspace owns
the optional editor setup and integration. This repository owns shared community
guidance and templates.

Keep technical instructions with their owners. Opening the multi-root workspace
does not configure dependencies or make it a prerequisite for any component.

## Issues

Search the target repository's existing issues first. Use **Bug** for a reproducible
problem and **Chore** for maintenance, tooling or documentation; a blank issue is
available for other proposals. A repository's own forms may provide more specific
choices. Discuss substantial API or architecture changes before implementing them.

Include the affected version or commit, a minimal reproducer, expected and actual
behavior, and relevant operating system and tool versions. Remove secrets and
unrelated personal data from logs. Use a private security report for suspected
vulnerabilities, even if a public issue form appears suitable.

## Changes and validation

- Keep changes focused and respect the repository's architecture, memory ownership,
  API and compatibility contracts.
- Add meaningful regression tests for behavior changes and run the checks required
  by that repository. Use its documented build configuration and dependency pins.
- Update public API documentation, examples and owner-maintained technical manuals
  when the change affects them.
- Record meaningful changes at the top of the applicable `Unreleased` category in
  the repository's changelog, including the issue reference. Preserve released history.
- Use the repository's formatting and pre-commit configuration when provided.

Describe the problem, resulting behavior and compatibility impact in the pull
request. Link the relevant issues; use `Closes owner/repository#number` for a
cross-repository issue only when the change resolves it. State the commands,
platforms and results actually checked, and identify pending or unrun checks.
Local success does not establish hosted CI, merge, publication or release evidence.

## Licensing and attribution

OpenTLV projects use MIT for their original code and documentation unless a file
carries a different valid notice. Each repository distributes its own LICENSE,
SPDX/REUSE configuration, third-party notices and package license metadata.
Community defaults do not copy or replace those files.

Marek Cingel retains copyright in his original contributions. Other contributors
retain theirs; an MIT contribution does not assign copyright. OpenTLV is a GitHub
organization, not a separate legal copyright holder. Do not introduce a mandatory
CLA or DCO through these shared guidelines.

Use accurate SPDX identifiers and copyright notices in the syntax supported by
the file. For original work by Marek Cingel from 2026, the convention is:

```text
SPDX-License-Identifier: MIT
Copyright (c) 2026 Marek Cingel
```

Preserve shebangs and encoding declarations, existing contributor years and all
third-party notices. Do not apply the example's author or year to someone else's
work. Use repository-local REUSE annotations or license sidecars for formats that
cannot contain comments. Generated and vendored files retain their own attribution.
The adapted Contributor Covenant in this repository retains its CC BY 4.0 license.
