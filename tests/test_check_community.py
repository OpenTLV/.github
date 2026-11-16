"""Exercise validation against temporary repositories without staging files."""

from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.check_community import MAX_FILE_BYTES, check


class CommunityValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(
            ["git", "init", "--quiet", str(self.root)], check=True,
            capture_output=True,
        )

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def test_valid_untracked_files_and_local_links(self):
        self.write("README.md", b"# Guide\n\n[Settings](settings.json)\n")
        self.write("settings.json", b'{"enabled": true}\n')
        self.write("settings.yml", b"enabled: true\n")
        self.assertEqual(check(self.root), [])

    def test_malformed_json_and_nonstandard_constants(self):
        self.write("broken.json", b'{"enabled":}\n')
        self.write("nonstandard.json", b'{"value": NaN}\n')
        errors = check(self.root)
        self.assertTrue(any("broken.json: invalid JSON" in e for e in errors))
        self.assertTrue(any("nonstandard.json: invalid JSON" in e for e in errors))

    def test_invalid_yaml_whitespace_and_missing_link(self):
        self.write("broken.yml", b"items: [\n")
        self.write("README.md", b"# Guide \r\n\r\n[Missing](missing.md)")
        errors = check(self.root)
        for expected in ("invalid YAML", "LF line endings", "final newline",
                         "trailing whitespace", "missing local link target"):
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in e for e in errors), errors)

    def test_file_size_boundary(self):
        self.write("allowed.txt", b"x" * (MAX_FILE_BYTES - 1) + b"\n")
        self.assertEqual(check(self.root), [])
        self.write("large.txt", b"x" * MAX_FILE_BYTES + b"\n")
        self.assertTrue(any("large.txt: file exceeds" in e for e in check(self.root)))

    def test_invalid_issue_form(self):
        self.write(".github/ISSUE_TEMPLATE/broken.yml", b"name: Broken\nbody: []\n")
        errors = check(self.root)
        self.assertTrue(any("missing description" in e for e in errors))
        self.assertTrue(any("form needs body fields" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
