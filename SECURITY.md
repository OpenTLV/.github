# Security policy

## Reporting a vulnerability

Do not publish undisclosed vulnerabilities, exploit details, credentials, tokens,
or personal data in public issues, pull requests, discussions, or profile comments.
Use a private reporting route:

1. Open the affected repository's **Security > Advisories** page and select
   **Report a vulnerability**. For OpenTLV/opentlv, use its
   [private vulnerability report form](https://github.com/OpenTLV/opentlv/security/advisories/new).
2. If the affected repository does not offer private reporting, or the finding
   spans repositories, use the
   [central OpenTLV private report form](https://github.com/OpenTLV/.github/security/advisories/new).
   Name the affected repository in the private report so it can be routed.

The responsible organization contact is
[@marekcingel](https://github.com/marekcingel). A GitHub profile is public and
does not provide private direct messaging; do not post a report there or tag the
account in a public issue to disclose details. The private forms above are the
reporting channels. Sign in to GitHub to use them.

Private reporting must be enabled separately in each eligible public repository;
this policy does not enable it or guarantee availability for other visibility
types. If neither private form is available, retain the report privately and wait
until a working private route is available. There is no email or off-GitHub
fallback published by this policy. Do not submit vulnerability details to public
issues or GitHub's abuse-reporting service as a substitute for reporting to OpenTLV.

Include the affected repository and revision, affected versions if known,
impact, reproduction steps, and a minimal sanitized proof of concept. Share
only the data needed to investigate. Coordinate publication with maintainers
and avoid testing systems without their owner's authorization.

## Maintainer triage and coordinated disclosure

The affected repository's maintainers own triage and remediation. Keep the
report and reproduction material in the private reporting channel. Confirm the
affected revisions and impact, request missing details privately, and assess
severity and affected components before deciding on a fix.

The responsible contact is responsible for monitoring central private reports and
coordinating routing with affected maintainers. Maintain access to private reports
and notification preferences when maintainers change. Periodically verify the
reporting routes using the
[setup and verification procedure](https://github.com/OpenTLV/.github/blob/main/docs/adoption.md#private-reporting-routes-and-verification).

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
