"""Validate repository text, local Markdown links, and GitHub issue forms."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


def check() -> list[str]:
    errors = []
    # Include new files so a direct invocation is useful before staging too.
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True,
    )
    paths = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
    for name in paths:
        path = ROOT / name
        if not path.is_file():
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{name}: expected UTF-8 text; review binary asset checks")
            continue
        if "\r" in text or text.startswith("\ufeff"):
            errors.append(f"{name}: use UTF-8 without BOM and LF line endings")
        if text and not text.endswith("\n"):
            errors.append(f"{name}: missing final newline")
        if any(line.rstrip() != line for line in text.splitlines()):
            errors.append(f"{name}: trailing whitespace")
        if re.search(r"^(?:<{7}|={7}|>{7})(?: |$)", text, re.MULTILINE):
            errors.append(f"{name}: possible merge conflict marker")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
                link = urlsplit(target)
                if link.scheme or link.netloc or not link.path:
                    continue
                if not (path.parent / unquote(link.path)).exists():
                    errors.append(f"{name}: missing local link target {target}")
        if path.suffix in {".yml", ".yaml"}:
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as exc:
                errors.append(f"{name}: invalid YAML: {exc}")
                continue
            if path.parent.name == "ISSUE_TEMPLATE" and path.name != "config.yml":
                errors.extend(check_form(name, data))
    return errors


def check_form(name: str, data: object) -> list[str]:
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
        if kind not in {"markdown", "input", "textarea", "dropdown", "checkboxes"}:
            errors.append(f"{name}: unsupported field type {kind}")
        attrs = item.get("attributes", {})
        if not isinstance(attrs, dict):
            errors.append(f"{name}: field attributes must be a mapping")
            continue
        if not attrs.get("value" if kind == "markdown" else "label"):
            errors.append(f"{name}: field missing content or label")
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
    print("Community text, local links, YAML, and basic issue form structure passed.")
