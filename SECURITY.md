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

## Leaked credentials and secret-scanning alerts

Treat an exposed credential as compromised. Handle alert details privately with
the credential owner and repository maintainers. Never paste its value into an
issue, PR, screenshot, log, or test fixture.

1. Review the alert in GitHub's restricted secret-scanning view. Identify the
   provider, owner, affected locations, and exposure scope without copying the
   credential elsewhere. Do not try it against a service.
2. Have the authorized owner revoke the exposed credential promptly, issue a
   replacement if needed, and update affected services through approved secret
   stores. Removing a file does not invalidate the credential; do not rely on
   automatic provider action alone.
3. Review provider audit logs and affected access with the owner. Coordinate
   incident response privately and share only sanitized findings publicly.
4. Remove the value from current files and relevant artifacts through the normal
   reviewed change process. History rewriting, force pushes, and protection
   bypasses require separate approval and are not the default remediation.
5. Close the alert with an accurate resolution after remediation. For a false
   positive, establish that the match is not a usable credential and record a
   sanitized explanation. Do not dismiss a real exposure just to unblock CI or
   because the value was removed from the latest file.

Investigate push-protection blocks privately before retrying. Never bypass a
block to publish a real credential. Justified false-positive exceptions must
follow approved repository policy and be recorded without the matched value.

GitHub's [alert remediation guidance](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-secret-scanning-alerts/resolving-alerts)
describes alert resolution controls. Setup and safe verification are documented
in the shared [adoption guide](https://github.com/OpenTLV/.github/blob/main/docs/adoption.md).

## Supported versions and response

Each repository defines supported releases and security updates locally.
Without a published support table, no release support or response deadline is
promised. Maintainers assess reports, agree on remediation and disclosure where
possible, and credit reporters with their consent.

Maintainer setup and verification:
<https://github.com/OpenTLV/.github/blob/main/docs/adoption.md>.
