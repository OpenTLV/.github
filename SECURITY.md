# Security Policy

## Scope and supported versions

This policy provides a private reporting and coordination path for OpenTLV Core,
CLI, bindings, documentation, workspace tooling and shared community files.
Examples include memory-safety errors when parsing untrusted TLV data, resource
exhaustion, unsafe command execution, dependency or packaging problems, and
credential disclosure in tooling or workflows.

Follow the affected repository's own security policy for its supported versions
and maintenance branches. This shared policy does not extend a component's support
window or promise fixes for every historical release. If support is unclear, report
the affected version privately so maintainers can assess it.

## Report privately

**Do not disclose suspected vulnerabilities in public issues, discussions or pull
requests.** Do not upload exploit inputs, credentials or sensitive logs there.

1. Open the affected repository's **Security > Advisories > Report a vulnerability**
   form. The [repository directory](https://github.com/OpenTLV/.github/blob/main/SUPPORT.md)
   identifies the component owner. GitHub requires sign-in to submit a private report.
2. If the affected component is unclear, several repositories are involved, or its
   private reporting form is unavailable, use the
   [OpenTLV coordination report](https://github.com/OpenTLV/.github/security/advisories/new).
   Name the affected repositories in the private report.
3. If you cannot use either form, use the contact information published by maintainer
   [Marek Cingel](https://github.com/marekcingel) to request a private reporting
   channel. A GitHub profile is not a private messaging service. Do not post
   vulnerability details publicly while arranging contact.

Include the repository, version/tag or full commit, affected files or API,
dependency versions and relevant platform/build options. Describe the impact and
provide minimal reproduction steps or a proof of concept through the private
channel. Include any mitigation, suggested fix and preferred attribution.
Remove credentials and unrelated personal data; use synthetic inputs where possible.

## Triage and coordination

The receiving repository's maintainers review the report, acknowledge it privately,
request missing information, reproduce the behavior and assess severity, affected
versions and exploit conditions. Marek Cingel coordinates reports that span
repositories and involves the relevant component maintainers on a need-to-know basis.
Response and resolution times depend on severity, complexity and availability;
there is no fixed service-level guarantee.

Maintain the report and fix details in private advisories or other agreed private
channels while investigating. Do not create public cross-repository tracking issues
that reveal an unresolved vulnerability. If separate advisories are needed, coordinate
their access and cross-references privately with the reporter.

For a Core fix, assess affected CLI and language bindings, their pinned or packaged
Core versions, binaries and published packages. For tooling or publication issues,
involve the owning repository and affected consumers. Each repository owns its fix,
tests, dependency update and release; a Core fix alone does not update consumers.

Coordinate mitigations, release timing, advisory publication and reporter credit.
Publish affected/fixed versions, upgrade instructions and a GitHub Security Advisory
where appropriate once disclosure is agreed. Assign or request a CVE when applicable.
Avoid publishing exploit details before users have an appropriate mitigation.

## Repository settings

Private vulnerability reporting must be enabled separately on each public repository;
adding or inheriting this file does not enable it. Maintainers also configure advisory
access and security-notification subscriptions per repository/account. See the
[adoption checklist](https://github.com/OpenTLV/.github/blob/main/docs/community-defaults.md).
Broader vulnerability management is tracked in
[Core #689](https://github.com/OpenTLV/opentlv/issues/689).
