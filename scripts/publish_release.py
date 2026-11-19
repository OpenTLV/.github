"""Publish a CI-approved candidate from its pinned checkout and verified tag."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from time import sleep

from scripts.release_notes import SEMVER


def run(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True,
                          encoding="utf-8", errors="replace")


def remote_tag(tag):
    ref = f"refs/tags/{tag}"
    # Without --exit-code, an empty *successful* lookup means no such ref.
    line = run("git", "ls-remote", "--refs", "origin", ref).stdout.rstrip("\n")
    if not line:
        return None
    oid, _, found_ref = line.partition("\t")
    if found_ref != ref or not re.fullmatch(r"[0-9a-f]{40}", oid):
        raise ValueError(f"Unexpected remote ref lookup for {ref}")
    return oid


def verify_tag(oid, tag, sha, fingerprint):
    if run("git", "cat-file", "-t", oid).stdout.strip() != "tag":
        raise ValueError(f"{tag} is not an annotated tag")
    # These fields are part of the signed payload. Peeling the ref to a
    # commit would also allow a differently named tag or a tag of another tag.
    payload = subprocess.check_output(["git", "cat-file", "tag", oid])
    header = f"object {sha}\ntype commit\ntag {tag}\n".encode("ascii")
    if not payload.startswith(header):
        raise ValueError(f"Tag object {oid} does not directly name {tag} on {sha}")
    status = run("git", "verify-tag", "--raw", oid).stderr
    signatures = re.findall(r"^\[GNUPG:\] VALIDSIG ([0-9A-F]+) ", status, re.MULTILINE)
    invalid = tuple(f"[GNUPG:] {code} " for code in
                    ("BADSIG", "ERRSIG", "REVKEYSIG", "EXPKEYSIG", "EXPSIG"))
    if signatures != [fingerprint] or any(line.startswith(invalid) for line in status.splitlines()):
        raise ValueError(f"{tag} does not have a valid signature by {fingerprint}")


def remote_release(repo, tag):
    # Listing includes drafts for the publisher and avoids mistaking a 404
    # caused by a missing repository or insufficient access for an absent tag.
    pages = json.loads(run("gh", "api", "--paginate", "--slurp",
                           f"repos/{repo}/releases?per_page=100").stdout)
    if not isinstance(pages, list) or not pages or not all(isinstance(p, list) for p in pages):
        raise ValueError("Unexpected response when looking up published and draft releases")
    matches = [release for page in pages for release in page if release["tag_name"] == tag]
    if len(matches) > 1:
        raise ValueError(f"Multiple releases already refer to {tag}")
    return matches[0] if matches else None


def publish(repo, version, sha, display_name, fingerprint, notes):
    if not SEMVER.fullmatch(version):
        raise ValueError("Expected a full SemVer version without a leading v")
    if (not re.fullmatch(r"[0-9a-f]{40}", sha) or
            run("git", "rev-parse", "--verify", "HEAD").stdout.strip() != sha):
        raise ValueError("The checkout must match the full candidate SHA")
    fingerprint = fingerprint.upper()
    if not re.fullmatch(r"(?:[0-9A-F]{40}|[0-9A-F]{64})", fingerprint):
        raise ValueError("Expected a full OpenPGP signing key fingerprint")
    if not display_name.strip():
        raise ValueError("Missing repository display name")

    tag = f"v{version}"
    ref = f"refs/tags/{tag}"
    title = f"{display_name} {version}"
    prerelease = "-" in version.partition("+")[0]
    expected = {"tag_name": tag, "name": title, "body": notes.read_bytes().decode("utf-8"),
                "prerelease": prerelease, "draft": False}
    oid = remote_tag(tag)
    release = remote_release(repo, tag)
    if oid is None:
        if release is not None:
            raise ValueError(f"A Release already exists without the expected tag {tag}")
        run("git", "-c", "gpg.format=openpgp", "tag", "--sign", "--local-user",
            fingerprint + "!", "--message", title, tag, sha)
        oid = run("git", "rev-parse", "--verify", ref).stdout.strip()
        verify_tag(oid, tag, sha, fingerprint)
        push = run("git", "push", "--no-follow-tags", "origin", f"{oid}:{ref}", check=False)
        # A transport failure can happen after the ref was accepted.
        if remote_tag(tag) != oid:
            push.check_returncode()
            raise ValueError(f"The remote tag {tag} does not match the verified object {oid}")
    else:
        run("git", "fetch", "--no-tags", "origin", ref)
        if run("git", "rev-parse", "--verify", "FETCH_HEAD").stdout.strip() != oid:
            raise ValueError(f"Remote tag {tag} changed during verification")
        verify_tag(oid, tag, sha, fingerprint)

    if release is None:
        args = ["gh", "release", "create", tag, "--repo", repo, "--verify-tag",
                "--title", title, "--notes-file", str(notes)]
        if prerelease:
            args.append("--prerelease")
        create = run(*args, check=False)
        # The releases list can lag behind a successful create, even if the
        # create response was lost. Repeat only the lookup.
        for delay in (0, 2, 4, 8, 16, 32):
            if delay:
                sleep(delay)
            release = remote_release(repo, tag)
            if release is not None:
                break
        else:
            create.check_returncode()
            raise ValueError(f"Could not confirm the GitHub Release for {tag} after repeated lookups")
    differences = [field for field, value in expected.items() if release[field] != value]
    if differences:
        raise ValueError(f"Existing Release for {tag} differs in {', '.join(differences)}")
    if remote_tag(tag) != oid:
        raise ValueError(f"Remote tag {tag} changed during publication")
    return oid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--notes", type=Path, required=True)
    args = parser.parse_args()
    try:
        oid = publish(os.environ["GITHUB_REPOSITORY"], args.version, args.sha, args.display_name,
                      args.fingerprint, args.notes)
    except subprocess.CalledProcessError as error:
        sys.exit(f"{error}\n{(error.stderr or '').strip()}")
    except (KeyError, ValueError, OSError) as error:
        sys.exit(str(error))
    print(f"Verified Release v{args.version} on {args.sha} (tag object {oid})")


if __name__ == "__main__":
    main()
