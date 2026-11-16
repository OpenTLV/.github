# Security policy

## Reporting a vulnerability

Do not publish exploit details, secrets, or personal data in issues or pull
requests. Open the affected repository's **Security > Advisories** page and use
**Report a vulnerability**, if available, to submit a private report.

Private vulnerability reporting must be enabled separately in each repository;
this policy does not enable it. If the button is unavailable, use a private
security contact explicitly published by that repository's maintainers. If no
private contact exists, open an issue asking only for a private reporting
channel. Withhold all sensitive details until a private channel is established.

Include the affected repository and revision, affected versions if known,
impact, reproduction steps, and a minimal sanitized proof of concept. Share
only the data needed to investigate. Coordinate publication with maintainers
and avoid testing systems without their owner's authorization.

## Maintainer triage and coordinated disclosure

The affected repository's maintainers own triage and remediation. Keep the
report and reproduction material in the private reporting channel. Confirm the
affected revisions and impact, request missing details privately, and assess
severity and affected components before deciding on a fix.

For cross-repository findings, coordinate privately with the relevant component
maintainers and share only the information they need. Agree on remediation,
release coordination, and disclosure timing with the reporter where possible.
Publish an advisory describing affected versions, available fixes or mitigations,
and agreed credit when disclosure is appropriate. Never copy a private report
into a public tracker as part of routine triage.

## Supported versions and response

Each repository defines supported releases and security updates locally.
Without a published support table, no release support or response deadline is
promised. Maintainers assess reports, agree on remediation and disclosure where
possible, and credit reporters with their consent.

Maintainer setup and verification:
<https://github.com/OpenTLV/.github/blob/main/docs/adoption.md>.
