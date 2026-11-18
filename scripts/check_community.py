"""Validate repository text, local Markdown links, and GitHub issue forms."""

from html.parser import HTMLParser
from pathlib import Path
import html
import json
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 1024 * 1024
REPOSITORY_FILES = r"/(?i:OpenTLV/\.github)/blob/main/"
BINARY_SUFFIXES = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
    ".zip", ".gz", ".7z", ".exe", ".dll", ".so", ".pyc",
    ".woff", ".woff2", ".ttf", ".sqlite", ".db", ".docx", ".xlsx", ".pptx",
})


def without_fences(text: str) -> str:
    """Blank fenced code, retaining line boundaries for heading detection."""
    lines = []
    fence = None
    for line in text.splitlines():
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) +
                            "{" + str(fence[1]) + r",}\s*", line):
                fence = None
            lines.append("")
        else:
            match = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", line)
            if match and not (match[1][0] == "`" and "`" in match[2]):
                fence = (match[1][0], len(match[1]))
                lines.append("")
            else:
                lines.append(line)
    return "\n".join(lines)


def without_code_spans(text: str) -> str:
    """Mask spans with matching backtick runs within a paragraph."""
    paragraphs = re.split(r"(\n[ \t]*\n)", text)
    for index in range(0, len(paragraphs), 2):
        paragraph = paragraphs[index]
        runs = list(re.finditer(r"`+", paragraph))
        next_run = {}
        closing = {}
        for run in reversed(runs):
            length = len(run[0])
            closing[run.start()] = next_run.get(length)
            next_run[length] = run
        parts = []
        end = 0
        for run in runs:
            if run.start() < end:
                continue
            opener = run.start()
            while opener and paragraph[opener - 1] == "\\":
                opener -= 1
            if (run.start() - opener) % 2:
                continue
            match = closing[run.start()]
            if match:
                parts.append(paragraph[end:run.start()])
                parts.append(re.sub(r"[^\n]", " ", paragraph[run.start():match.end()]))
                end = match.end()
        parts.append(paragraph[end:])
        paragraphs[index] = "".join(parts)
    return "".join(paragraphs)


class MarkdownHTML(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.anchors = set()
        self.links = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if not value:
                continue
            if name == "id":
                self.anchors.add(value)
            elif name == "href":
                self.links.append(value)


def heading_anchors(text: str) -> set[str]:
    """Anchors for ordinary ATX/single-line setext headings, including duplicates."""
    anchors = set()
    text = without_fences(text)
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r" {0,3}#{1,6}(?:[ \t]+(.*)|$)", line)
        if match:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", match[1] or "")
        elif (index and lines[index - 1].strip() and
              re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", line) and
              not re.match(r"\s*(?:#|>|[-+*] |\d+[.)] )", lines[index - 1])):
            title = lines[index - 1].strip()
        else:
            continue
        # Preserve visible inline text, not link destinations or HTML tags.
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
        title = html.unescape(re.sub(r"<[^>]*>", "", title))
        title = re.sub(r"(?<!\w)_{1,2}(.+?)_{1,2}(?!\w)", r"\1", title)
        title = re.sub(r"[*`~\\]", "", title).lower()
        slug = "".join(
            "-" if char == " " else char
            for char in title
            if char in " -_" or unicodedata.category(char)[0] in "LNM"
        )
        candidate = slug
        number = 0
        while candidate in anchors:
            number += 1
            candidate = f"{slug}-{number}"
        anchors.add(candidate)
    return anchors | MarkdownHTML(without_code_spans(text)).anchors


def markdown_links(text: str) -> list[str]:
    """Extract supported destinations outside fenced and inline code."""
    text = without_code_spans(without_fences(text))
    reference = (
        r"^ {0,3}\[(?:\\.|[^\[\]\\\n])+\]:[ \t]*(?:\n[ \t]*)?"
        r"(?:<([^>\n]+)>|([^\s<>]+))"
        r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\)))?[ \t]*$"
    )
    targets = [angle or plain for angle, plain in re.findall(reference, text, re.MULTILINE)]
    text = re.sub(reference, "", text, flags=re.MULTILINE)
    inline = r"\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:[^\n)]*)\)"
    links = re.findall(inline, text)
    targets.extend(angle or plain for angle, plain in links)
    text = re.sub(inline, "", text)
    targets.extend(re.findall(r"<((?:https?://|#)[^<>\s]+)>", text))
    targets.extend(MarkdownHTML(text).links)
    text = re.sub(r"<[^>\n]*>", "", text)
    # GitHub also autolinks bare same-repository file URLs.
    targets.extend(target.rstrip(".,;!?") for target in re.findall(
        r"(?i:https?://github\.com)" + REPOSITORY_FILES + r"[^\s<>\])]*", text,
    ))
    return sorted(set(targets))


def has_exact_path(root: Path, path: Path) -> bool:
    """Check checkout spelling even on case-insensitive filesystems."""
    parent = root
    for part in path.relative_to(root).parts:
        if part != ".." and not any(child.name == part for child in parent.iterdir()):
            return False
        parent = parent / part
    return True


def check_link_targets(root: Path, path: Path, targets: list[str]) -> list[str]:
    errors = []
    for target in targets:
        try:
            link = urlsplit(target)
            repository_file = False
            if link.scheme or link.netloc:
                prefix = re.match(REPOSITORY_FILES, link.path)
                if (link.scheme not in {"http", "https"} or
                        link.netloc.lower() != "github.com" or
                        not prefix):
                    continue
                base = root
                raw_path = link.path[prefix.end():]
                repository_file = True
            else:
                base = root if link.path.startswith("/") else path.parent
                raw_path = link.path.lstrip("/")
            decoded = unquote(raw_path)
            # Reject Windows separators, drive/ADS syntax, and NUL on every OS.
            if any(char in decoded for char in ("\\", ":", "\0")):
                raise ValueError("invalid local path")
            requested = base / decoded if decoded or repository_file else path
            destination = requested.resolve()
            destination.relative_to(root.resolve())
            exists = destination.exists() and has_exact_path(root, requested)
        except (ValueError, OSError, RuntimeError):
            errors.append(f"unsafe local link target {target}")
            continue
        if not exists or (repository_file and not destination.is_file()):
            errors.append(f"missing local link target {target}")
            continue
        if link.fragment and destination.is_file() and destination.suffix.lower() == ".md":
            if destination.stat().st_size > MAX_FILE_BYTES:
                errors.append(f"link target exceeds the 1 MiB repository limit {target}")
                continue
            try:
                anchors = heading_anchors(destination.read_text(encoding="utf-8"))
            except (OSError, UnicodeError):
                errors.append(f"unreadable Markdown link target {target}")
                continue
            if unquote(link.fragment) not in anchors:
                errors.append(f"missing local Markdown anchor {target}")
    return errors


def has_conflict_markers(text: str, markdown: bool) -> bool:
    if re.search(r"^(?:<{7,}|>{7,}|\|{7,})(?:[ \t]|$)", text, re.MULTILINE):
        return True
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if re.fullmatch(r"={7,}[ \t]*", line):
            # In Markdown this can be a legitimate setext heading underline.
            if not markdown or not index or not lines[index - 1].strip():
                return True
    return False


def contains_symlink(root: Path, relative_path: Path) -> bool:
    """Check from the root down, including parents of paths in Git's index."""
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def check(root: Path = ROOT) -> list[str]:
    errors = []
    # Include new files so a direct invocation is useful before staging too.
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, check=True, capture_output=True,
    )
    paths = sorted(set(result.stdout.split(b"\0")) - {b""})
    for raw_name in paths:
        try:
            name = raw_name.decode("utf-8")
        except UnicodeDecodeError:
            name = raw_name.decode("utf-8", errors="backslashreplace")
            errors.append(f"{name}: expected a UTF-8 path")
            continue
        relative_path = Path(name)
        if contains_symlink(root, relative_path):
            errors.append(f"{name}: symbolic links are not allowed")
            continue
        path = root / relative_path
        suffix = path.suffix.lower()
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(f"{name}: file exceeds the 1 MiB repository limit")
            continue
        if suffix in BINARY_SUFFIXES:
            errors.append(f"{name}: binary asset type is not approved")
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{name}: expected UTF-8 text; binary assets are not approved")
            continue
        if "\0" in text:
            errors.append(f"{name}: unexpected binary content (NUL byte)")
            continue
        if "\r" in text or text.startswith("\ufeff"):
            errors.append(f"{name}: use UTF-8 without BOM and LF line endings")
        if text and not text.endswith("\n"):
            errors.append(f"{name}: missing final newline")
        if any(line.rstrip() != line for line in text.splitlines()):
            errors.append(f"{name}: trailing whitespace")
        if has_conflict_markers(text, suffix == ".md"):
            errors.append(f"{name}: possible merge conflict marker")
        if suffix == ".md":
            link_errors = check_link_targets(root, path, markdown_links(text))
            errors.extend(f"{name}: {error}" for error in link_errors)
        if path.suffix == ".json":
            try:
                json.loads(text, parse_constant=reject_json_constant)
            except ValueError as exc:
                errors.append(f"{name}: invalid JSON: {exc}")
        if suffix in {".yml", ".yaml"}:
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as exc:
                errors.append(f"{name}: invalid YAML: {exc}")
                continue
            if path.parent.name == "ISSUE_TEMPLATE":
                if path.stem + suffix == "config.yml":
                    problems = check_contact_links(root, path, data)
                    errors.extend(f"{name}: {error}" for error in problems)
                else:
                    errors.extend(check_form(root, name, data))
    return errors


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard constant {value}")


def check_contact_links(root: Path, path: Path, data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["issue chooser configuration must be a mapping"]
    contacts = data.get("contact_links", [])
    if not isinstance(contacts, list):
        return ["contact_links must be a list"]
    errors = []
    for index, contact in enumerate(contacts):
        url = contact.get("url") if isinstance(contact, dict) else None
        field = f"contact_links[{index}].url"
        if not isinstance(url, str) or not url.strip():
            errors.append(f"{field}: expected a non-empty URL")
            continue
        errors.extend(f"{field}: {error}" for error in check_link_targets(root, path, [url]))
    return errors


def check_form(root: Path, name: str, data: object) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return [f"{name}: form must be a mapping"]
    for field in ("name", "description"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{name}: missing {field}")
    body = data.get("body")
    if not isinstance(body, list) or not body:
        return errors + [f"{name}: form needs body fields"]
    identifiers = set()
    for item in body:
        if not isinstance(item, dict):
            errors.append(f"{name}: body item must be a mapping")
            continue
        kind = item.get("type")
        if kind not in {"markdown", "input", "textarea", "dropdown", "checkboxes", "upload"}:
            errors.append(f"{name}: unsupported field type {kind}")
        attrs = item.get("attributes", {})
        if not isinstance(attrs, dict):
            errors.append(f"{name}: field attributes must be a mapping")
            continue
        if kind == "markdown":
            value = attrs.get("value")
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{name}: markdown field needs a non-empty text value")
            else:
                problems = check_link_targets(root, root / name, markdown_links(value))
                errors.extend(f"{name}: {error}" for error in problems)
        elif not attrs.get("label"):
            errors.append(f"{name}: field missing content or label")
        if kind in {"dropdown", "checkboxes"}:
            options = attrs.get("options")
            if not isinstance(options, list) or not options:
                errors.append(f"{name}: {kind} options must be a non-empty list")
            else:
                labels = set()
                for index, option in enumerate(options):
                    if kind == "dropdown":
                        label = option
                    elif isinstance(option, dict):
                        label = option.get("label")
                        if "required" in option and not isinstance(option["required"], bool):
                            errors.append(f"{name}: checkbox option {index + 1} required must be boolean")
                    else:
                        errors.append(f"{name}: checkbox option {index + 1} must be a mapping")
                        continue
                    if not isinstance(label, str) or not label.strip():
                        errors.append(f"{name}: {kind} option {index + 1} needs a non-empty string label")
                    elif label in labels:
                        errors.append(f"{name}: {kind} duplicate option label {label}")
                    else:
                        labels.add(label)
        if kind != "markdown":
            identifier = item.get("id")
            if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", identifier):
                errors.append(f"{name}: invalid field id")
            elif identifier in identifiers:
                errors.append(f"{name}: duplicate field id {identifier}")
            else:
                identifiers.add(identifier)
    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    print("File sizes, text, local links, JSON, YAML, and basic issue form structure passed.")
