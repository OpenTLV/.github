# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Use the pinned uv version for dependency lock regeneration and align the documented command with the generated lockfile header. (#41)
- Catch broken reference-style and HTML links, validate explicit HTML anchors, and keep Markdown validation running after unmatched backticks and invalid UTF-8 Git paths. (#40)
- Validate dropdown and checkbox option structure and document the text-only asset policy, with explicit rejection of unexpected binary content. (#27)
- Validate same-repository file links and local heading anchors, skip fenced link examples, and distinguish setext headings from merge-conflict markers. (#25)
- Add the shared security-reporting and sensitive-data notice to the feature request form. (#24)
- Use four-space indentation for Python files in EditorConfig while preserving other formatting defaults. (#22)

### Added

- CI verifies development lockfile reproducibility and checks installed Python dependencies. (#44)
- Default Task and Epic issue types for the corresponding shared forms. (#42)
- Default `bug`, `enhancement`, and `chore` labels for the corresponding shared issue forms. (#42)
- Pinned, integrity-checked actionlint and zizmor checks in community CI, with local reproduction and workflow security guidance. (#12)
- Organization-wide changelog guidance with newest-first releases and entries within each category. (#17)
- Private credential-exposure triage and secret-scanning alert resolution guidance. (#13)
- Native push-protection setup, safe verification, coverage limits, and local detector evaluation. (#13)
- Shared Task and Epic issue forms with native sub-issue tracking guidance. (#11)
- Optional Validation field in the Chore form. (#11)
- GitHub Free governance baseline and procedures for repository audits and approved settings changes. (#10)
- Repository setup and verification guidance for dependency graph, Dependabot alerts, and security updates. (#3)
- Issue and PR label conventions, including `chore` for repository maintenance and tooling. (#3)
- Monthly Dependabot updates for SHA-pinned workflow actions.
- SPDX file notice conventions for headers, sidecars, and preserved third-party notices.
- Optional logs and additional context fields in the Bug report form.
- PR template prompts for API/ABI, wire format, packaging, and cross-repository impact.
- Pinned Markdown linting, JSON syntax and file-size checks, and validation regression tests. (#3)
- Python 3.10+ setup guidance, minimum-version CI coverage, and workspace tooling boundaries. (#3)
- Repository-neutral Chore issue form for maintenance, tooling, and documentation work. (#2)
- Component ownership and support routing guidance and private security triage procedures. (#2)
- Adoption guidance for the shared form set and verification of valid submissions. (#2)
- Maintainers-only blank issue option; general contributors use the issue forms. (#2)
- Organization profile with bootstrap status and verified public repository links. (#1)
- Contribution, conduct, security, and support policies. (#1)
- Branch naming conventions and PR title, description, and issue reference guidelines. (#1)
- Shared bug and feature issue forms and a pull request template. (#1)
- Repository-local quality checks and REUSE licensing metadata. (#1)
- Adoption, local override, attribution, and deployment verification guidance. (#1)

### Changed

- Clarify that new changelog categories go at the top of their version section. (#43)
- Publish the maintainer-designated private email for security fallback and project conduct reports, replacing the GitHub-only contact limitation. (#28)
- Document GitHub-only private security routes, the responsible maintainer, conduct-reporting options, and remaining contact and verification limits. (#28)
- Hash-lock the Python development dependency graph and run local Python hooks from the verified environment, with reproducible update guidance. (#23)
- Replace session-specific deployment notes with dated verification evidence and explicit pending authenticated checks. (#21)
- Include the issue number directly after the type prefix in new branch names for issue-related work. (#26)
- Simplify contribution and validation guidance, consolidate tooling update rules, and clarify tracked and untracked file coverage. (#26)
- Separate inherited contribution rules from community-repository development instructions and remove obsolete bootstrap guidance. (#20)
- Changelog uses standard change categories; verification evidence and outstanding checks remain in the adoption guide. (#3)
