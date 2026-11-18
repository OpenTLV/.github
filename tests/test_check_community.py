"""Exercise validation against temporary repositories without staging files."""

from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

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

    def test_issue_chooser_checks_exact_contact_urls(self):
        self.write("docs/policy(v2).md", b"# Reporting\n")
        config = ".github/ISSUE_TEMPLATE/config.yml"
        base = "https://github.com/OpenTLV/.github/blob/main/"
        urls = [
            base + "docs/policy(v2).md#reporting",
            "https://example.invalid/support",
            base + "missing.md",
            base + "docs/policy(v2).md#absent",
        ]
        self.write(config, yaml.safe_dump({"contact_links": [
            {"name": "Help", "url": url, "about": "Read the policy."} for url in urls
        ]}).encode())
        self.assertEqual(check(self.root), [
            f"{config}: contact_links[2].url: missing local link target {urls[2]}",
            f"{config}: contact_links[3].url: missing local Markdown anchor {urls[3]}",
        ])

    def test_issue_form_checks_rendered_markdown_links(self):
        self.write("SUPPORT.md", b"# Getting help\n")
        form = ".github/ISSUE_TEMPLATE/support.yml"
        base = "https://github.com/OpenTLV/.github/blob/main/"
        self.write(form, yaml.safe_dump({
            "name": "Support", "description": "Get help.",
            "body": [
                {"type": "markdown", "attributes": {"value": (
                    f"See {base}SUPPORT.md#getting-help.\n"
                    f"Report using {base}missing.md.\n"
                    f"[Contact]({base}SUPPORT.md#absent)\n"
                    "`[example](example.md)`\n"
                )}},
                {"type": "textarea", "id": "question", "attributes": {
                    "label": "Question", "placeholder": "[example](example.md)",
                }},
            ],
        }).encode())
        self.assertCountEqual(check(self.root), [
            f"{form}: missing local link target {base}missing.md",
            f"{form}: missing local Markdown anchor {base}SUPPORT.md#absent",
        ])

    def test_invalid_issue_link_values_report_file_and_field(self):
        config = ".github/ISSUE_TEMPLATE/config.yml"
        form = ".github/ISSUE_TEMPLATE/example.yml"
        self.write(config, b"contact_links:\n  - url: []\n")
        self.write(form, b"name: Help\ndescription: Get help.\nbody:\n"
                         b"  - type: markdown\n    attributes:\n      value: [bad]\n")
        self.assertCountEqual(check(self.root), [
            f"{config}: contact_links[0].url: expected a non-empty URL",
            f"{form}: markdown field needs a non-empty text value",
        ])

    def test_valid_upload_field(self):
        self.write(".github/ISSUE_TEMPLATE/attachment.yml", yaml.safe_dump({
            "name": "Attachment",
            "description": "Submit a screenshot.",
            "body": [{
                "type": "upload",
                "id": "screenshot",
                "attributes": {"label": "Screenshot"},
                "validations": {"required": True, "accept": ".png,.jpg"},
            }],
        }).encode())
        self.assertEqual(check(self.root), [])

    def write_choice_form(self, kind, attributes):
        self.write(".github/ISSUE_TEMPLATE/choices.yml", yaml.safe_dump({
            "name": "Choices",
            "description": "Test a choice field.",
            "body": [{"type": kind, "id": "choices", "attributes": {
                "label": "Choose", **attributes,
            }}],
        }).encode())

    def test_valid_choice_options(self):
        cases = (
            ("dropdown", {"options": ["One", "Two"]}),
            ("dropdown", {"options": ["One"], "multiple": True, "default": 0}),
            ("checkboxes", {"options": [
                {"label": "I agree", "required": True},
                {"label": "Optional", "required": False},
                {"label": "**Markdown** [policy](https://example.org)"},
            ]}),
        )
        for kind, attributes in cases:
            with self.subTest(kind=kind, attributes=attributes):
                self.write_choice_form(kind, attributes)
                self.assertEqual(check(self.root), [])

    def test_choice_options_must_be_nonempty_lists(self):
        for kind in ("dropdown", "checkboxes"):
            for attributes in ({}, {"options": None}, {"options": []},
                               {"options": "One"}, {"options": {"label": "One"}}):
                with self.subTest(kind=kind, attributes=attributes):
                    self.write_choice_form(kind, attributes)
                    self.assertTrue(any("options must be a non-empty list" in e
                                        for e in check(self.root)))

    def test_dropdown_option_types_and_duplicates(self):
        for options in ([None], [True], [1], [""], ["  "], [[]],
                        [{"label": "One"}], ["One", "One"]):
            with self.subTest(options=options):
                self.write_choice_form("dropdown", {"options": options})
                self.assertTrue(any("dropdown option" in e or "duplicate option" in e
                                    for e in check(self.root)))

    def test_checkbox_option_structure(self):
        for options in (["One"], [None], [False], [[]], [{}], [{"label": ""}],
                        [{"label": "  "}], [{"label": 1}],
                        [{"label": "One", "required": "true"}],
                        [{"label": "One", "required": 1}],
                        [{"label": "One", "required": None}],
                        [{"label": "One"}, {"label": "One", "required": True}]):
            with self.subTest(options=options):
                self.write_choice_form("checkboxes", {"options": options})
                self.assertTrue(any("checkbox option" in e or "checkboxes option" in e
                                    or "duplicate option" in e for e in check(self.root)))

    def test_unexpected_binary_files_are_rejected_everywhere(self):
        for name, content in (
            ("unexpected.bin", b"\xff\xfe\x80"),
            ("profile/assets/logo.png", b"\x89PNG\r\n\x1a\n"),
            ("docs/renamed.md", b"\xff\xfe\x80"),
            ("with-nul.txt", b"valid UTF-8\0but not text\n"),
            ("ascii.PDF", b"%PDF-1.7\nASCII-only content\n"),
            ("renamed.data", b"\0\x01\x02\n"),
        ):
            self.write(name, content)
        errors = check(self.root)
        for name in ("unexpected.bin", "docs/renamed.md"):
            self.assertTrue(any(e.startswith(f"{name}: expected UTF-8 text") for e in errors), errors)
        for name in ("profile/assets/logo.png", "ascii.PDF"):
            self.assertTrue(any(e.startswith(f"{name}: binary asset type is not approved")
                                for e in errors), errors)
        self.assertTrue(any("with-nul.txt: unexpected binary content" in e for e in errors), errors)
        self.assertTrue(any("renamed.data: unexpected binary content" in e for e in errors), errors)

    def test_same_repository_links_and_fragments(self):
        self.write("docs/guide.md", "# Caf\u00e9 & *Setup*!\n\n## Again\n\n## Again\n".encode())
        self.write("README.md", (
            "# Guide\n\n"
            "[Local](docs/guide.md#caf%C3%A9--setup)\n"
            "[Duplicate](docs/guide.md#again-1)\n"
            "[Self](#guide)\n"
            "[Absolute](https://github.com/OpenTLV/.github/blob/main/docs/guide.md#again)\n"
            "<https://github.com/OpenTLV/.github/blob/main/docs/guide.md>\n"
            "See https://github.com/OpenTLV/.github/blob/main/docs/guide.md.\n"
        ).encode())
        self.assertEqual(check(self.root), [])
        self.write("README.md", (
            "# Guide\n\n"
            "[Missing](https://github.com/OpenTLV/.github/blob/main/missing.md)\n"
            "<https://github.com/OpenTLV/.github/blob/main/missing-autolink.md>\n"
            "[Anchor](docs/guide.md#absent)\n"
            "[Self](#absent)\n"
        ).encode())
        errors = check(self.root)
        self.assertEqual(sum("missing local link target" in e for e in errors), 2, errors)
        self.assertEqual(sum("missing local Markdown anchor" in e for e in errors), 2, errors)

    def test_reference_html_and_case_insensitive_repository_links(self):
        self.write("docs/Guide.md", b"# Guide\n")
        self.write("README.md", (
            '[Missing][ref]\n\n[ref]: <missing reference.md> "Title"\n'
            '<a HREF="missing&amp;html.md">HTML link</a>\n'
            '[Wrong case](https://github.com/oPeNtLv/.GITHUB/blob/main/docs/guide.md)\n'
            '<https://GITHUB.com/opentlv/.Github/blob/main/missing-angle.md>\n'
            'See https://github.com/opentlv/.Github/blob/main/missing-bare.md.\n'
            '[Valid][ok]\n\n[ok]: docs/Guide.md#guide\n'
            '[Valid](https://github.com/opentlv/.GITHUB/blob/main/docs/Guide.md)\n'
        ).encode())
        self.assertEqual(check(self.root), [
            f"README.md: missing local link target {target}"
            for target in sorted((
                "missing reference.md", "missing&html.md",
                "https://github.com/oPeNtLv/.GITHUB/blob/main/docs/guide.md",
                "https://GITHUB.com/opentlv/.Github/blob/main/missing-angle.md",
                "https://github.com/opentlv/.Github/blob/main/missing-bare.md",
            ))
        ])

    def test_unmatched_backticks_leave_links_visible(self):
        self.write("README.md", (
            '`unmatched [Visible](absent.md)\n'
            '`` multi-line ``` [Hidden](example.md)\n'
            '<a href="example.html">Example</a> ``\n\n'
            '```markdown\n[hidden]: example-reference.md\n```\n\n'
            '`[Hidden](another-example.md)`\n'
        ).encode())
        self.assertEqual(check(self.root), ["README.md: missing local link target absent.md"])

    def test_uppercase_suffixes_and_explicit_anchors(self):
        self.write("Guide.MD", (
            '<a ID="KeepCase"></a>\n<span id=plain></span>\n'
            '`<a id="example"></a>`\n\n'
            '```html\n<a id="fenced"></a>\n```\n\n'
            '[Valid](#KeepCase) [Also valid](#plain)\n'
            '[Wrong case](#keepcase) [Missing](#example) [Fenced](#fenced)\n'
            '[Broken](absent.md)\n'
        ).encode())
        self.write("broken.YML", b"items: [\n")
        errors = check(self.root)
        self.assertEqual(errors[:4], [
            "Guide.MD: missing local Markdown anchor #example",
            "Guide.MD: missing local Markdown anchor #fenced",
            "Guide.MD: missing local Markdown anchor #keepcase",
            "Guide.MD: missing local link target absent.md",
        ])
        self.assertEqual(len(errors), 5)
        self.assertTrue(errors[4].startswith("broken.YML: invalid YAML"), errors)

    def test_non_utf8_git_path_does_not_interrupt_validation(self):
        self.write("broken.YAML", b"items: [\n")
        blob = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"], input=b"text\n",
            cwd=self.root, check=True, capture_output=True,
        ).stdout.strip()
        subprocess.run(
            ["git", "update-index", "-z", "--index-info"],
            input=b"100644 " + blob + b"\tbad\xff.md\0",
            cwd=self.root, check=True, capture_output=True,
        )
        errors = check(self.root)
        self.assertEqual(errors[0], r"bad\xff.md: expected a UTF-8 path")
        self.assertTrue(errors[1].startswith("broken.YAML: invalid YAML"), errors)

    def test_fenced_and_inline_code_are_not_links_or_headings(self):
        self.write("README.md", (
            "# Guide\n\n"
            "```markdown\n[Missing](absent.md)\n## Hidden\n```\n\n"
            "~~~~\n<https://github.com/OpenTLV/.github/blob/main/absent.md>\n"
            "~~~\n[Still inside](absent.md)\n~~~~\n\n"
            "  ```\n[Indented fence](absent.md)\n  ```\n\n"
            "`[Inline example](absent.md)`\n\n[Visible](#guide)\n"
        ).encode())
        self.assertEqual(check(self.root), [])
        with (self.root / "README.md").open("ab") as stream:
            stream.write(b"[Not a heading](#hidden)\n")
        self.assertTrue(any("missing local Markdown anchor" in e for e in check(self.root)))

    def test_heading_normalization_and_duplicate_collisions(self):
        self.write("README.md", (
            "# `GITHUB_TOKEN` and [Links](other.md) ###\n\n"
            "## An _emphasized_  heading &amp; more!\n\n"
            "## Same\n\n## Same\n\n## Same-1\n\n## Same\n\n"
            "Setext heading\n=======\n\n"
            "[Code](#github_token-and-links)\n"
            "[Emphasis](#an-emphasized--heading--more)\n"
            "[Second](#same-1)\n[Collision](#same-1-1)\n[Third](#same-2)\n"
            "[Setext](#setext-heading)\n"
        ).encode())
        self.write("other.md", b"# Other\n")
        self.assertEqual(check(self.root), [])

    def test_repository_blob_links_require_files(self):
        self.write("docs/guide.md", b"# Guide\n")
        self.write("README.md", (
            "# Guide\n\n"
            "[Directory](https://github.com/OpenTLV/.github/blob/main/docs)\n"
            "[Empty](https://github.com/OpenTLV/.github/blob/main/)\n"
        ).encode())
        errors = check(self.root)
        self.assertEqual(sum("missing local link target" in e for e in errors), 2, errors)

    def test_encoded_and_angle_wrapped_destinations(self):
        self.write("docs/a (b).md", b"# A heading\n")
        self.write("README.md", (
            "# Guide\n\n"
            "[Encoded](docs/a%20%28b%29.md#a-heading)\n"
            "[Angle](<docs/a (b).md#a-heading>)\n"
            "[Remote](<https://github.com/OpenTLV/.github/blob/main/docs/a%20(b).md#a-heading>)\n"
            "[Title](docs/a%20%28b%29.md \"Optional title\")\n"
        ).encode())
        self.assertEqual(check(self.root), [])

    def test_symlink_target_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.md"
            target.write_text("# Outside\n", encoding="utf-8")
            try:
                (self.root / "escape.md").symlink_to(target)
            except OSError as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            self.write("README.md", b"# Guide\n\n[Escape](escape.md#outside)\n")
            self.assertTrue(any("unsafe local link target" in e for e in check(self.root)))

    def test_rejects_file_and_dangling_symlinks_without_reading_targets(self):
        self.write("notes.txt", b"Plain text\n")
        try:
            (self.root / "linked.json").symlink_to("notes.txt")
            (self.root / "dangling.md").symlink_to("missing.md")
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        self.assertEqual(check(self.root), [
            "dangling.md: symbolic links are not allowed",
            "linked.json: symbolic links are not allowed",
        ])

    def test_rejects_tracked_file_under_a_replaced_directory(self):
        self.write("docs/guide.md", b"# Guide\n")
        subprocess.run(
            ["git", "add", "docs/guide.md"], cwd=self.root, check=True, capture_output=True,
        )
        docs = self.root / "docs"
        docs.rename(self.root / "moved")
        try:
            docs.symlink_to("moved", target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        self.assertIn("docs/guide.md: symbolic links are not allowed", check(self.root))

    def test_links_cannot_escape_repository(self):
        self.write("README.md", (
            "# Guide\n\n"
            "[Parent](../outside.md)\n"
            "[Encoded](https://github.com/OpenTLV/.github/blob/main/%2e%2e/outside.md)\n"
            "[Windows](%5c%5cserver%5cshare.md)\n"
            "[Drive](C%3a/secret.md)\n"
            "[Nul](bad%00.md)\n"
        ).encode())
        errors = check(self.root)
        self.assertEqual(sum("unsafe local link target" in e for e in errors), 5, errors)

    def test_external_links_and_other_refs_do_not_use_network(self):
        self.write("README.md", (
            "# Guide\n\n"
            "[Other](https://example.invalid/absent.md#missing)\n"
            "[Repo](https://github.com/other/repo/blob/main/absent.md)\n"
            "[Tag](https://github.com/OpenTLV/.github/blob/v1.0/absent.md)\n"
        ).encode())
        self.assertEqual(check(self.root), [])

    def test_setext_and_real_conflict_markers(self):
        self.write("README.md", b"A valid heading\n=======\n\nAnother\n-------\n")
        self.assertEqual(check(self.root), [])
        for content in (
            b"<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> topic\n",
            b"<<<<<<<\nours\n=======\ntheirs\n>>>>>>>\n",
            b"||||||| base\nold\n",
            b"=======\n",
        ):
            with self.subTest(content=content):
                self.write("README.md", content)
                self.assertTrue(any("merge conflict marker" in e for e in check(self.root)))
        self.write("README.md", b"# Guide\n")
        self.write("orphan.txt", b"content\n=======\n")
        self.assertTrue(any("orphan.txt: possible merge conflict" in e for e in check(self.root)))


if __name__ == "__main__":
    unittest.main()
