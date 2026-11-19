# Release tags and GitHub Releases

This policy applies to every OpenTLV repository, including OpenTLV/.github.
Each repository owns its Full CI and release workflow. Only its release
workflow creates release tags. The tag, GitHub Release, and changelog entry
all identify the same version and the same commit from `main`.

The first production release will be in `OpenTLV/.github`. After the
[disposable repository checks](#test-in-a-disposable-repository) pass, open
**Actions → Release → Run workflow** in `OpenTLV/.github`, choose `main` and
enter the version from its changelog without the `v` prefix. For example,
`gh workflow run release.yml --repo OpenTLV/.github --ref main -f version=0.1.0-rc.1`.
The [release workflow](../.github/workflows/release.yml) uses the display name
`OpenTLV community defaults`.

## What each repository configures

| Setting | What maintainers record in the repository |
| --- | --- |
| Display name | The project name used in release titles, including its capitalization. |
| Full CI | The repository's trusted workflow and the jobs that must succeed for a release. In OpenTLV/.github these are the `quality` and `workflow-analyzers` jobs of `Community quality`. |
| Publication identity | A dedicated actor, such as a GitHub App installed on the repository. Limit access to its write credential and the signing key to the release workflow's publication job on protected `main`. Validation and Full CI run with read-only access. |
| Signing identity | The approved public key fingerprint, its maintainer or team owner, and the verification material used to check signatures. The owner controls key access, rotation, and revocation. |
| Changelog tool | One parameterized Python CLI maintained in OpenTLV/.github. In each consuming workflow, check out OpenTLV/.github at a reviewed full commit SHA in a separate directory. OpenTLV/.github uses the script in its own pinned candidate checkout. |

## Set up the OpenTLV/.github publisher

1. Protect `main` and review changes to workflows and release scripts as
   privileged code. In the owning account's **Settings → Developer settings →
   GitHub Apps**, choose **New GitHub App**. Give it a unique name and a
   homepage URL. Disable the webhook, grant the **Contents** and **Workflows**
   repository permissions **Read and write**, and limit installation to this
   account. GitHub can require Workflows permission to tag the original
   candidate if workflow files on `main` change after dispatch. Keep the App
   off every branch bypass list. [GitHub Release permissions](https://docs.github.com/en/rest/releases/releases#create-a-release)
   and [GitHub workflow-file tagging behavior](https://github.com/orgs/community/discussions/109715).
   Register the App, open **Install App**, and select only this repository. Record the App's
   owner, slug, numeric App ID and client ID. In its settings, use **Generate
   a private key** to download the PEM.
   [Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app).
2. Create the `release` environment under **Settings → Environments**. Under
   **Deployment branches and tags**, choose **Selected branches and tags**
   and add a single **Branch** rule for the literal name `main`. Keep the tag
   rule list empty. Only the release workflow's `publish` job should reference
   this environment. Keep the default Actions token read-only.
   [Managing deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).
3. On a trusted signing workstation, use a fresh private GnuPG home and a
   dedicated signing key with an expiration date. Set `GNUPGHOME` to a new
   directory outside the checkout and `SIGNER_UID` to the publisher's name and
   email. The following example creates an unattended primary signing key,
   signs a sample and verifies it using a fresh public-only keyring.

   ```sh
   set -e
   : "${GNUPGHOME:?Set a new GnuPG home}" "${SIGNER_UID:?Set the publisher name and email}"
   export GNUPGHOME
   umask 077
   mkdir "$GNUPGHOME"
   gpg --batch --pinentry-mode loopback --passphrase '' \
     --quick-generate-key "$SIGNER_UID" ed25519 sign 1y
   SIGNING_FINGERPRINT=$(gpg --with-colons --fingerprint "$SIGNER_UID" | awk -F: '$1 == "fpr" {print $10; exit}')
   test -n "$SIGNING_FINGERPRINT"
   gpg --armor --output "$GNUPGHOME/release-public.asc" --export "$SIGNING_FINGERPRINT"
   probe=$(mktemp -d)
   printf '%s\n' 'Release signer check' > "$probe/check.txt"
   gpg --local-user "${SIGNING_FINGERPRINT}!" --detach-sign "$probe/check.txt"
   gpg --homedir "$probe" --import "$GNUPGHOME/release-public.asc"
   gpg --homedir "$probe" --status-fd 1 --verify "$probe/check.txt.sig" "$probe/check.txt" > "$probe/status"
   grep -F "[GNUPG:] VALIDSIG $SIGNING_FINGERPRINT " "$probe/status"
   ```

   Retain `release-public.asc` and record the verified fingerprint, its owner
   and approval date independently of the publisher. Store the revocation
   certificate with the owner. For an existing primary key with a signing
   subkey, select the exact signing subkey fingerprint from
   `gpg --list-secret-keys --with-subkey-fingerprint` and test that subkey.
   [GnuPG key management](https://www.gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html).
4. Populate the following **environment** settings. The App key authorizes
   pushes and Release creation. The OpenPGP key signs the Git tag.

   | Kind | Name | Value |
   | --- | --- | --- |
   | Variable | `RELEASE_APP_CLIENT_ID` | Client ID from the App settings. |
   | Variable | `RELEASE_SIGNING_FINGERPRINT` | Independently approved full uppercase signing-key fingerprint. |
   | Secret | `RELEASE_APP_PRIVATE_KEY` | Contents of the App's PEM private key, including its header and footer. |
   | Secret | `RELEASE_SIGNING_KEY` | ASCII-armored, unencrypted OpenPGP secret signing key, including its header and footer. |

   For example, from a trusted shell set `REPO` to the destination
   `OWNER/REPOSITORY`. With a dedicated primary signing key, pipe its export
   directly to GitHub. For a dedicated signing subkey, use
   `--export-secret-subkeys "${SIGNING_FINGERPRINT}!"` in the second command.

   ```sh
   gh secret set RELEASE_APP_PRIVATE_KEY --repo "$REPO" --env release < app-private-key.pem
   gpg --armor --export-secret-keys "$SIGNING_FINGERPRINT" |
     gh secret set RELEASE_SIGNING_KEY --repo "$REPO" --env release
   gh variable set RELEASE_APP_CLIENT_ID --repo "$REPO" --env release --body "$APP_CLIENT_ID"
   gh variable set RELEASE_SIGNING_FINGERPRINT --repo "$REPO" --env release --body "$SIGNING_FINGERPRINT"
   ```

5. Configure the [two tag rulesets](#enforce-and-verify-immutable-tags) under
   the repository's normal settings change process. Complete the
   [disposable repository checks](#test-in-a-disposable-repository) before the
   first production release.

## Use the changelog CLI in another repository

In the consuming workflow's read-only job, use Python 3.10 or later and replace the `ref` placeholder with
the reviewed, full commit SHA of OpenTLV/.github containing the CLI. The
candidate checkout stays at the workspace root. The CLI resolves links in its
changelog against the consuming repository and its pinned commit.

```yaml
permissions:
  contents: read
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
    with:
      ref: ${{ github.sha }}
      persist-credentials: false
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
    with:
      repository: OpenTLV/.github
      ref: REPLACE_WITH_REVIEWED_FULL_COMMIT_SHA
      path: release-tools
      persist-credentials: false
  - name: Prepare release notes
    env:
      VERSION: ${{ inputs.version }}
    run: |
      python release-tools/scripts/release_notes.py \
        --changelog CHANGELOG.md --version "$VERSION" --output release-notes.md
```

## Publish a version

1. **Pin the candidate.** Dispatch the repository's release workflow from
   `refs/heads/main` with a full [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)
   version, such as `0.1.0-rc.1` or `0.1.0`. Reject other refs. Capture the
   dispatch commit SHA once and use it for checkout, validation, Full CI, and
   tagging, even if `main` advances during the run.
2. **Prepare the release notes.** Invoke the shared CLI directly with Python.
   Pass `--changelog` pointing to the candidate's root `CHANGELOG.md`,
   `--version` with the full input (without a leading `v`), and
   `--output release-notes.md`. Require the first release heading below
   `## [Unreleased]` to be `## [<version>] - YYYY-MM-DD` with a valid date
   and an exact version match, including any prerelease and build identifiers.
   Stop on a missing or mismatched section. Extract only that section's body,
   ending before the next version heading or at EOF. Preserve Markdown headings, lists, links,
   and code blocks. Include the definitions for references used in that body,
   even when they appear elsewhere in the changelog. Resolve relative link
   destinations against the pinned revision so they work on the Release page.
3. **Require Full CI for this commit.** Before creating any new tag, run the
   repository's Full CI for the pinned SHA and require every designated job
   to finish successfully. If CI runs separately, verify the repository,
   workflow identity, `head_sha`, and job conclusions for the candidate run.
   A skipped job, a passing PR check on a different SHA, or missing evidence
   blocks publication.
4. **Sign, verify, and push.** Serialize publication using a single
   repository-wide concurrency group across versions, with in-progress
   publication allowed to finish. Inside that group, check the remote tag
   first and apply the retry rules below if it exists. Otherwise create a
   signed annotated tag named `v<version>` directly on the pinned commit.
   Verify its signature against the repository's approved fingerprint, then
   inspect the signed tag object's embedded name, target type (`commit`), and
   target SHA. Push just that verified tag, without force.
5. **Publish the GitHub Release.** After confirming the verified tag exists
   on the remote, create the Release against it. Set the title to
   `<display name> <version>` and use the prepared Markdown file as its body.
   With GitHub CLI, use `gh release create` with `--verify-tag`, `--title`,
   and `--notes-file release-notes.md`. Add `--prerelease` exactly when the
   version has a SemVer prerelease component. [GitHub CLI release reference](https://cli.github.com/manual/gh_release_create).

## Retry an interrupted publication

Use **Re-run failed jobs** on the original release run within 30 days of its
initial run to retain the version and dispatch SHA even if `main` has advanced.
[Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs).
Under the same concurrency
group, read the remote state again, including after an ambiguous push or API
response. An access or network error leaves that state unknown and stops the run.

| Remote state | Workflow action |
| --- | --- |
| Tag and Release are absent | Follow the full publication sequence, including the exact-SHA Full CI gate. |
| Tag exists, Release is absent | Fetch the tag object. Verify its signature and approved signer, embedded name, and direct commit target exactly as for a new tag. Reuse the verified tag and publish the missing Release from the original candidate's notes. |
| Tag and published Release exist | Verify the tag, then compare the Release's tag, title, Markdown body, and prerelease flag to the expected values. A match completes the retry. |
| Tag is lightweight, unsigned, signed by an unapproved key, or names a different version or commit | Stop and report the conflict. The existing tag is immutable. |
| Release or remote state conflicts with the expected publication | Stop for maintainer review. Preserve the existing publication. |

## Signing key rotation

Store the private key in the repository's protected release environment or a
signing service restricted to its publisher. Keep trusted public verification
material independently of the tag being checked. For example, with OpenPGP,
use `git verify-tag --raw`, require successful verification, and match the
verified fingerprint to the approved key. [Git signature verification](https://git-scm.com/docs/git-verify-tag).

Before a planned rotation, finish any interrupted publications whose tags
were signed by the current key. The publisher checks the active fingerprint
when retrying. The owner reviews and records the replacement
fingerprint and its effective date, verifies a test signature, switches the
publisher to the new key, and retires the old private credential. Retain old
public keys and their approval periods for verifying historical releases. For a
suspected compromise, suspend publication, revoke the affected credential, and
review affected tags before resuming with an approved replacement. Existing
tags keep their original signatures.

## Enforce and verify immutable tags

Configure two **Active** tag rulesets. GitHub applies the bypass list to all
rules within one ruleset, so keep creation and immutability in separate rulesets.
[GitHub ruleset controls](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

| Target | Rules | Bypass actors |
| --- | --- | --- |
| Include all tags, with no exclusions | Restrict updates and restrict deletions | Empty, including for administrators and the release identity |
| Include tag pattern `v*`, with no exclusions | Restrict creations | Only the installed release App, with **Always allow** bypass |

The [immutable tags ruleset](../.github/rulesets/immutable-tags.json) is ready
to apply. Render the [release tag creation template](../.github/rulesets/create-release-tags.template.json)
with the installed App's numeric **App ID** from its registration. Set `REPO`
to the disposable `OWNER/REPOSITORY` for the rehearsal. From the checkout root,
prepare the payload and inspect existing rulesets, including inherited ones.

```sh
set -e
endpoint="repos/${REPO:?Set OWNER/REPOSITORY}/rulesets"
mkdir -p .cache
jq -e --arg id "${APP_ID:?Set numeric App ID}" \
  '($id | select(test("^[1-9][0-9]*$")) | tonumber) as $app | .bypass_actors[0].actor_id = $app' \
  .github/rulesets/create-release-tags.template.json > .cache/create-release-tags.json
gh api --paginate "$endpoint?includes_parents=true&per_page=100" --jq '.[] | [.id,.source,.target,.name] | @tsv'
```

Follow the [repository governance baseline](governance.md) for settings changes.
For each missing ruleset, review the destination and payload, run its creation
command once, and record the returned ID. For existing rulesets use their IDs.

```sh
gh api --method POST "$endpoint" --input .github/rulesets/immutable-tags.json --jq .id
gh api --method POST "$endpoint" --input .cache/create-release-tags.json --jq .id
```

Read each effective ruleset with an account that can inspect bypass actors.
Compare the returned fields to the reviewed payloads. An omitted
`bypass_actors` field leaves that part unverified.
[GitHub rulesets API](https://docs.github.com/en/rest/repos/rules#get-a-repository-ruleset).

```sh
for id in "${IMMUTABLE_RULESET_ID:?Set immutable tags ruleset ID}" "${CREATION_RULESET_ID:?Set release creation ruleset ID}"; do
  gh api "$endpoint/$id?includes_parents=true" --jq '{name,target,enforcement,conditions,rules,bypass_actors}'
done
```

## Test in a disposable repository

1. Create a new empty repository under an account or organization where you can
   administer Actions, environments, Apps and tag rulesets. On GitHub Free use
   a public repository and public test data. For example, with `TEST_REPO` set
   to the new `OWNER/NAME` and the reviewed release implementation committed
   in your checkout, the following commands create and seed it. Confirm its
   default branch is `main`, enable Actions and apply the same branch protections.

   ```sh
   gh repo create "$TEST_REPO" --public
   git push "https://github.com/$TEST_REPO.git" HEAD:refs/heads/main
   ```

2. Repeat [publisher setup](#set-up-the-opentlvgithub-publisher) there with
   a separate test App, signing key and `release` environment. Install this App
   only on the disposable repository. Use its own App ID in the creation
   ruleset and verify both active tag rules.
3. Run the exercises below against the disposable remote. Retain the
   repository name, run IDs, candidate SHAs, ruleset IDs, actor identities
   and remote tag object IDs with the outcomes.

| Exercise | Expected evidence |
| --- | --- |
| Put a dated `0.1.0-rc.1` section with a relative link and a reference definition on `main`. Dispatch that version. | Both Full CI jobs succeed for the dispatch SHA. The annotated tag verifies against the test key and points directly to the candidate. The published Release is a prerelease, has the configured title and matches the extracted notes, including working links. |
| Add a dated `0.1.0` section above the prerelease; dispatch the stable version. | Both jobs pass again on the new SHA. The verified tag is `v0.1.0` and the Release has `prerelease: false`. |
| Hold a candidate at the disposable `release` environment (for example, enable a required reviewer). Merge a harmless workflow-file edit to `main`, then approve the waiting publication. | The App can create the signed tag on the original dispatch SHA. The tag and notes still match the candidate. |
| Re-run a successful release. For the interrupted case, use the test App and approved test key to seed a correctly signed tag on a fresh candidate without creating a Release. Dispatch the corresponding version. | Both paths succeed with the original tag object ID. The tag-only case publishes the expected Release body and flags. |
| Dispatch from another branch, with a mismatched or missing dated section, and with a deliberately failing Full CI check, each using an unused version. | Publication never runs. Each candidate's tag and Release remain absent. |
| Prepare another candidate whose tag already exists at a different commit or with an unapproved signer, using the test App in the disposable setup. | Publication fails and the original tag object ID remains unchanged. |
| As an ordinary writer, try creating an unused `v*` tag and a nonrelease tag such as `qa/nested`. | Only the nonrelease tag can be created. The successful release run establishes that the App can create `v*` tags. |
| As the ordinary writer and the test release App, attempt a forced update to a different object and a deletion of both a release tag and `qa/nested`. | Rule insights show server-side rejections for all eight operations. The original remote object IDs still match. |

For the Release checks, inspect the published fields with
`gh release view TAG --repo OWNER/REPO --json tagName,name,body,isDraft,isPrerelease`.
Fetch and verify each tag with the independently retained test public key.
`git cat-file -p refs/tags/TAG` shows the signed name, the direct target type,
and its SHA. Capture remote object IDs with `git ls-remote --refs origin
refs/tags/TAG`. Re-read the active production settings and record their review
alongside the disposable run evidence before the first production dispatch.

## Example promotion from prerelease to stable

In `OpenTLV/.github`, the example heading
`## [0.1.0-rc.1] - 2026-11-10` yields tag `v0.1.0-rc.1` and a GitHub
prerelease titled `OpenTLV community defaults 0.1.0-rc.1`.

To promote it without code changes, keep that published section intact. Add a
new dated stable section immediately below Unreleased that links to the
prerelease. In this example the shared CLI carries the `rc-notes` definition
into the stable Release body.

```markdown
## [0.1.0] - 2026-11-12

### Changed

- Promote [0.1.0-rc.1][rc-notes] to stable without code changes.

[rc-notes]: https://github.com/OpenTLV/.github/releases/tag/v0.1.0-rc.1
```

Run Full CI on the new `main` commit containing this stable section. After it
passes, the workflow signs `v0.1.0` on that commit and publishes
`OpenTLV community defaults 0.1.0` as a stable Release. Its body includes
the link to the prerelease.
