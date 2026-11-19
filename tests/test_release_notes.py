"""Exercise the standalone release notes command against a pinned Git checkout."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.release_notes import SEMVER, release_notes


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_notes.py"


class ReleaseNotesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.changelog = self.root / "CHANGELOG.md"
        self.output = self.root / "notes.md"

    def changelog_text(self, body, version="1.2.3"):
        return f"# Changelog\n\n## [Unreleased]\n\n## [{version}] - 2024-02-29\n\n" + body

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.root), *args], text=True,
        ).strip()

    def commit(self):
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git("-c", "user.name=Tester", "-c", "user.email=tester@example.org",
                 "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "candidate")
        return self.git("rev-parse", "HEAD")

    def test_full_versions(self):
        for version in ("0.0.0", "1.2.99999", "10.0.0-1",
                        "1.0.0-0.01alpha.-+2024.007", "1.2.3+build-with-hyphens"):
            with self.subTest(version=version):
                self.assertIsNotNone(SEMVER.fullmatch(version))
        for version in ("01.2.3", "1.2.03", "1.2", "v1.2.3", " 1.2.3",
                        "1.2.3-a.02", "1.0.0+", "1.0.0-a+", "1.2.3-",
                        "1.2.3-a_b", "١.2.3", "1.2.3+build..2", "1.2.3\n"):
            with self.subTest(version=version):
                self.assertIsNone(SEMVER.fullmatch(version))

    def test_missing_or_mismatched_first_section_and_invalid_dates(self):
        older = "\n## [1.2.3] - 2024-02-29\n\n- Older.\n"
        for header in ("", "## [Unreleased]\n", "## [2.0.0] - 2024-03-01\n" + older,
                       "## [1.2.3] - 2024-02-29\n\n- Released.\n\n## [Unreleased]\n",
                       "## [Unreleased]\n## [1.2.3-rc.1] - 2024-01-01\n" + older,
                       "## [Unreleased]\n## 2.0.0 - 2024-05-01\n" + older,
                       "## [Unreleased]\n## [1.2.3+build] - 2024-01-01\n",
                       "## [Unreleased]\n## [1.2.3] - 2025-02-29\n",
                       "## [Unreleased]\n## [1.2.3] - 2024-2-29\n"):
            with self.subTest(header=header):
                self.changelog.write_text(header + "\n- Notes.\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    release_notes(self.changelog, "1.2.3")

    def test_dated_release_first(self):
        body = "### Added\n\n- First release candidate.\n"
        self.changelog.write_text(
            "# Changelog\n\n## [1.2.3-rc.1] - 2024-02-29\n\n" + body
            + "\n## [1.2.2] - 2024-01-12\n\n- Earlier release.\n", encoding="utf-8",
        )
        self.assertEqual(release_notes(self.changelog, "1.2.3-rc.1"), body)

    def test_preserve_markdown_and_collect_only_referenced_definitions(self):
        header = "## [1.2.3-rc.1+build.007] - 2024-02-29\n\n"
        body = (
            "### Added\n\n- See [guide][  User   Guide ], [spec][], or [faq].\n"
            "- Leave `[code]` and \\[escaped] unchanged.\n\n"
            "~~~md\n## [2.0.0] - 2024-01-01\n[code](missing.md)\n~~~\n\n"
            "## More details\n\nRead [the website](https://example.org).\n"
        )
        definitions = (
            "[User guide]: https://example.org/guide \"Guide\"\n"
            "[spec]:\n  <https://example.org/spec>\n  'The specification'\n"
            "[faq]: https://example.org/faq\n"
        )
        self.changelog.write_text(
            "[silly]: https://unused.org\n\n## [Unreleased]\n\n" + header + body
            + "\n## [1.0.0] - 2024-01-01\n\n- Older.\n\n" + definitions
            + "[code]: ignored.md\n[escaped]: ignored.md\n",
            encoding="utf-8",
        )
        subprocess.run([sys.executable, str(SCRIPT), "--version", "1.2.3-rc.1+build.007",
                        "--changelog", str(self.changelog), "--output", str(self.output)],
                       check=True)
        self.assertEqual(self.output.read_bytes().decode(), body + "\n" + definitions)

    def test_eof_notes_and_pinned_links_in_consuming_repository(self):
        (self.root / "docs").mkdir()
        self.changelog = self.root / "docs" / "history.md"
        self.changelog.write_text(self.changelog_text(
            "- Read [notes](guide(v2).md?choice=1#top \"Title\") or [this](#added).\n"
            "- See [a file][file] or ![map][img].\n"
            '- <a class="doc" href="/README.md">Readme</a>\n'
            "- ``[example](keep.me) and ` [other]``\n\n"
            "[unused]: unrelated.md\n[file]: <../old notes.md> 'Notes'\n"
            "[img]: ../img/map.png\n"
        ), encoding="utf-8")
        sha = self.commit()
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "OpenTLV/consumer",
                                     "GITHUB_SERVER_URL": "https://github.com",
                                     "GITHUB_SHA": "f" * 40}):
            notes = release_notes(self.changelog, "1.2.3")
        blob = f"https://github.com/OpenTLV/consumer/blob/{sha}"
        raw = f"https://github.com/OpenTLV/consumer/raw/{sha}"
        self.assertEqual(notes, (
            f'- Read [notes]({blob}/docs/guide%28v2%29.md?choice=1#top "Title") or '
            f'[this]({blob}/docs/history.md#added).\n'
            "- See [a file][file] or ![map][img].\n"
            f'- <a class="doc" href="{blob}/README.md">Readme</a>\n'
            "- ``[example](keep.me) and ` [other]``\n\n"
            f"[file]: <{blob}/old%20notes.md> 'Notes'\n[img]: {raw}/img/map.png\n"
        ))

    def test_repeated_labels_and_code_blocks(self):
        self.changelog.write_text(self.changelog_text(
            "Use [link].\n\n[Link]: https://first.org\n\n"
            "```md\n[link]: https://inside.code\n```\n\n"
            "[link]: https://later.org\n"
        ), encoding="utf-8")
        notes = release_notes(self.changelog, "1.2.3")
        self.assertEqual(notes.count("https://first.org"), 1)
        self.assertNotIn("https://later.org", notes)
        self.assertIn("```md\n[link]: https://inside.code\n```", notes)

    def test_indented_and_quoted_code_and_nested_list_links(self):
        body = (
            "    [code](missing.md)\n    [example][unused]\n\n"
            "> ~~~markdown\n> [ignored](missing.md)\n> ~~~\n\n"
            "- Outer item\n  - Nested item\n    See [link](docs/help.md).\n"
            "    ```\n    [sample](leave.me)\n    ```\n"
        )
        self.changelog.write_text(self.changelog_text(body), encoding="utf-8")
        revision = self.commit()
        self.git("remote", "add", "origin", "git@github.com:another/repo.git")
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": ""}):
            self.assertEqual(release_notes(self.changelog, "1.2.3"),
                             body.replace("(docs/help.md)",
                                          f"(https://github.com/another/repo/blob/{revision}/docs/help.md)"))

    def test_section_boundaries_ignore_nested_headings_and_html_examples(self):
        examples = (
            "- List item\n  ## [9.0.0] - 2026-01-01\n  Continued item.\n\n"
            "<pre>\n## [8.0.0] - 2026-01-01\n[example](example.md)\n</pre>\n\n"
            "<div>\n## [7.0.0] - 2026-01-01\n</div>\n\n"
            "Inline `<!--` and ``[relative](example.md)`` remain literal.\n"
        )
        self.changelog.write_text(self.changelog_text(examples)
                                  + "\n## [0.0.1] - 2020-01-01\n\nOld.\n", encoding="utf-8")
        self.assertEqual(release_notes(self.changelog, "1.2.3"), examples)

    def test_cli_invalid_input_does_not_write_output(self):
        self.changelog.write_text(self.changelog_text("No release.\n"), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--version", "1.0.0", "--changelog",
             str(self.changelog), "--output", str(self.output)], capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
