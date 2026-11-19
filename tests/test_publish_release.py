"""Exercise release retries with local Git remotes and an in-memory Releases API."""

from contextlib import chdir
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import publish_release as publisher


def command(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(f"Fixture command failed: {args}\n{result.stderr}")
    return result.stdout.strip()


@unittest.skipUnless(shutil.which("gpg") and shutil.which("gpgconf"), "requires GnuPG")
class PublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        home = cls.enterClassContext(tempfile.TemporaryDirectory())
        if os.name == "nt":
            cygpath = Path(shutil.which("gpg")).with_name("cygpath.exe")
            if cygpath.exists():  # GnuPG bundled with Git for Windows uses MSYS paths.
                home = command(cygpath, "-u", home)
        cls.enterClassContext(patch.dict(os.environ, {
            "GNUPGHOME": home, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
        }))
        cls.addClassCleanup(command, "gpgconf", "--kill", "all")
        command("gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase", "",
                "--quick-generate-key", "Release Test <release@example.invalid>",
                "ed25519", "sign", "1d")
        keys = command("gpg", "--batch", "--with-colons", "--list-secret-keys").splitlines()
        cls.fingerprint = next(line.split(":")[9] for line in keys if line.startswith("fpr:"))

    def setUp(self):
        self.enterContext(chdir(self.enterContext(tempfile.TemporaryDirectory())))
        command("git", "init", "--bare", "remote.git")
        command("git", "init", "--initial-branch=main", "work")
        self.enterContext(chdir("work"))
        command("git", "config", "user.name", "Release Test")
        command("git", "config", "user.email", "release@example.invalid")
        command("git", "commit", "--allow-empty", "-m", "candidate")
        command("git", "remote", "add", "origin", "../remote.git")
        self.sha = command("git", "rev-parse", "HEAD")
        self.notes = Path("release-notes.md")
        self.notes.write_bytes(b"### Changed\n\n- Details.\n")
        self.releases = []
        self.creates = 0
        self.hidden_release_reads = 0
        self.sleep = self.enterContext(patch.object(publisher, "sleep"))
        self.interrupted = set()
        self.git_run = publisher.run
        self.enterContext(patch.object(publisher, "run", side_effect=self.api))

    def api(self, *args, check=True):
        if args[0] == "git":
            result = self.git_run(*args, check=check)
            if args[1] == "push" and "push" in self.interrupted:
                return subprocess.CompletedProcess(args, 1, stderr="connection lost after push")
            return result
        if args[:2] == ("gh", "api"):
            if "lookup" in self.interrupted:
                raise subprocess.CalledProcessError(1, args, stderr="repository unavailable")
            if self.releases and self.hidden_release_reads:
                self.hidden_release_reads -= 1
                return subprocess.CompletedProcess(args, 0, stdout=json.dumps([self.releases[:-1]]))
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps([self.releases]))
        self.assertEqual(args[:3], ("gh", "release", "create"))
        self.assertIn("--verify-tag", args)
        self.creates += 1
        if "before create" in self.interrupted:
            return subprocess.CompletedProcess(args, 1, stderr="could not reach GitHub")
        self.releases.append({
            "tag_name": args[3], "name": args[args.index("--title") + 1],
            "body": Path(args[args.index("--notes-file") + 1]).read_bytes().decode(),
            "prerelease": "--prerelease" in args, "draft": False,
        })
        return subprocess.CompletedProcess(args, int("after create" in self.interrupted))

    def publish(self, version="1.0.0", fingerprint=None):
        publisher.publish("example/repo", version, self.sha, "Example",
                          fingerprint or self.fingerprint, self.notes)

    def test_stable_prerelease_and_completed_retries(self):
        for version, prerelease in [("1.0.0+build-4", False), ("1.1.0-rc.1+build", True)]:
            with self.subTest(version=version):
                self.publish(version)
                oid = publisher.remote_tag("v" + version)
                self.publish(version)
                self.assertEqual(oid, publisher.remote_tag("v" + version))
                self.assertEqual(self.releases[-1], {
                    "tag_name": "v" + version, "name": "Example " + version,
                    "body": self.notes.read_bytes().decode(), "prerelease": prerelease,
                    "draft": False,
                })
        self.assertEqual(self.creates, 2)

    def test_new_release_appears_after_delayed_reads(self):
        self.hidden_release_reads = 2
        self.publish()
        self.assertEqual(self.creates, 1)
        self.assertEqual(self.sleep.call_count, 2)
        self.assertEqual(self.releases[0]["tag_name"], "v1.0.0")

    def test_unconfirmed_successful_create_fails_without_creating_again(self):
        self.hidden_release_reads = 100
        with self.assertRaisesRegex(ValueError, "Could not confirm"):
            self.publish()
        self.assertEqual(self.creates, 1)
        self.assertGreater(self.hidden_release_reads, 0)

    def test_reconcile_dropped_responses_and_resume_tag_only(self):
        self.interrupted.update(["push", "before create"])
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish()
        oid = publisher.remote_tag("v1.0.0")
        self.assertIsNotNone(oid)
        self.interrupted = {"after create"}
        self.hidden_release_reads = 1
        self.publish()
        self.assertEqual(oid, publisher.remote_tag("v1.0.0"))
        self.assertEqual(len(self.releases), 1)

    def test_conflicting_tag_types_names_and_targets(self):
        sign = ("git", "tag", "-s", "-u", self.fingerprint + "!", "-m", "test")
        command("git", "tag", "v1.0.0")
        command("git", "tag", "-a", "-m", "unsigned", "v2.0.0")
        command(*sign, "other")
        command(*sign, "v4.0.0", "other")
        command("git", "commit", "--allow-empty", "-m", "other commit")
        command(*sign, "v5.0.0")
        command("git", "checkout", "--detach", self.sha)
        for version, target in [("1.0.0", "v1.0.0"), ("2.0.0", "v2.0.0"),
                                ("3.0.0", "other"), ("4.0.0", "v4.0.0"), ("5.0.0", "v5.0.0")]:
            with self.subTest(version=version):
                command("git", "push", "origin", f"{target}:refs/tags/v{version}")
                with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                    self.publish(version)
        self.assertEqual(self.creates, 0)

    def test_reject_unapproved_signer_and_conflicting_release(self):
        self.publish()
        with self.assertRaisesRegex(ValueError, "signature"):
            self.publish(fingerprint="0" * 40)
        for field, value in [("body", "different"), ("name", "different"),
                             ("prerelease", True), ("draft", True)]:
            with self.subTest(field=field), patch.dict(self.releases[0], {field: value}):
                with self.assertRaisesRegex(ValueError, field):
                    self.publish()
        self.assertEqual(self.creates, 1)

    def test_lookup_failure_and_orphan_draft_block_tag_creation(self):
        self.interrupted.add("lookup")
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish()
        self.interrupted.clear()
        self.releases.append({"tag_name": "v1.0.0", "draft": True})
        with self.assertRaisesRegex(ValueError, "without the expected tag"):
            self.publish()
        self.assertIsNone(publisher.remote_tag("v1.0.0"))
        self.assertEqual(self.creates, 0)
