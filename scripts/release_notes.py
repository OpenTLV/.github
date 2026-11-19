"""Extract Markdown release notes from a candidate's Keep a Changelog file."""

import argparse
from datetime import date
from functools import cached_property
import html
import os
from pathlib import Path
import posixpath
import re
import subprocess
from urllib.parse import quote, unquote, urlsplit, urlunsplit


NUMBER = r"(?:0|[1-9][0-9]*)"
IDENTIFIER = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
SEMVER = re.compile(
    rf"{NUMBER}\.{NUMBER}\.{NUMBER}(?:-{IDENTIFIER}(?:\.{IDENTIFIER})*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
HEADING = re.compile(r"^ {0,3}##[ \t]+([^\n]+?)[ \t]*$", re.MULTILINE)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
ESCAPE = r"\\[!-/:-@\[-`{-~]"
LABEL = r"\[((?:\\.|[^\[\]\\])+)\]"
ANGLE_URL = r"<(?:\\.|[^<>\\\n])*>"
TITLE = r'''(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^()\\])*\))'''
DEFINITION = re.compile(
    rf"^ {{0,3}}(?!\[\^){LABEL}:[ \t]*(?:\n[ \t]*)?"
    rf"(?P<url>{ANGLE_URL}|(?:\\.|[^\s<>\\])+)"
    rf"(?:(?:[ \t]+|\n[ \t]*){TITLE})?[ \t]*$",
    re.MULTILINE,
)
LINK_TOKEN = re.compile(rf"{ESCAPE}|\[|\]")
INLINE_END = re.compile(rf"(?:\s+{TITLE})?\s*\)")
HTML_LITERAL = re.compile(
    r"<!--.*?(?:-->|\Z)|<(?P<tag>pre|code|script|style|textarea)\b[^>]*>.*?</(?P=tag)\s*>",
    re.IGNORECASE | re.DOTALL,
)
# CommonMark block tags suspend Markdown parsing through the next blank line.
HTML_BLOCK = re.compile(
    r"^ {0,3}</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|"
    r"col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|"
    r"form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|"
    r"nav|ol|p|param|section|summary|table|tbody|td|tfoot|th|thead|title|tr|ul)"
    r"(?=[ \t\n/>]|$)[^\n]*(?:\n(?![ \t]*$)[^\n]*)*",
    re.IGNORECASE | re.MULTILINE,
)
HTML_TAG = re.compile(r"""</?[A-Za-z][\w:-]*(?:\s+(?:[^<>'"]|"[^"]*"|'[^']*')*)?\s*/?>""")
HTML_ATTRIBUTE = re.compile(
    r"""(?P<name>[\w:-]+)(?:\s*=\s*(?P<value>"[^"]*"|'[^']*'|[^\s"'=<>`]+))?"""
)


def blank(text):
    """Keep offsets and lines intact while hiding a Markdown literal."""
    return re.sub(r"[^\n]", "\x00", text)


def block_mask(text):
    """Hide code blocks, including those nested inside lists and blockquotes."""
    result = []
    fence = None
    list_indents = []
    quote_depth = 0
    after_break = True
    for line in text.splitlines(keepends=True):
        quotes = re.match(r"(?: {0,3}> ?)*", line)
        depth = quotes[0].count(">")
        if depth != quote_depth:
            fence = None
            list_indents.clear()
            after_break = True
            quote_depth = depth
        content = line[quotes.end():].expandtabs(4)
        indent = len(content) - len(content.lstrip(" "))
        if content.strip():
            while list_indents and indent < list_indents[-1]:
                list_indents.pop()
        content = content[list_indents[-1]:] if list_indents else content
        if fence is None and (item := re.match(r" {0,3}(?:[-+*]|\d{1,9}[.)]) {1,4}(?! )", content)):
            list_indents.append((list_indents[-1] if list_indents else 0) + item.end())
            content = content[item.end():]
        match = FENCE.match(content)
        if fence is not None:
            result.append(blank(line))
            if match and match[1].startswith(fence) and not match[2].strip():
                fence = None
        elif match and not (match[1][0] == "`" and "`" in match[2]):
            fence = match[1]
            result.append(blank(line))
        elif after_break and content.startswith("    "):
            result.append(blank(line))
            continue
        elif list_indents and HEADING.match(line):
            # Its source must survive in the notes, but this heading belongs to a list.
            result.append(line.replace("#", "\x00", 1))
        else:
            result.append(line)
        after_break = not content.strip()
    return "".join(result)


def inline_mask(text):
    """Hide matched backtick spans, including spans that wrap within a paragraph."""
    def mask_paragraph(paragraph):
        runs = list(re.finditer(r"`+", paragraph))
        next_run = {}
        closers = {}
        for run in reversed(runs):
            closers[run.start()] = next_run.get(len(run[0]))
            next_run[len(run[0])] = run.end()
        pieces = []
        end = 0
        for run in runs:
            if run.start() < end:
                continue
            opener = run.start()
            while opener and paragraph[opener - 1] == "\\":
                opener -= 1
            if (run.start() - opener) % 2:
                continue
            close = closers[run.start()]
            if close:
                pieces.append(paragraph[end:run.start()])
                pieces.append(blank(paragraph[run.start():close]))
                end = close
        return "".join(pieces) + paragraph[end:]

    blocks = re.split(r"(^ {0,3}#{1,6}[ \t][^\n]*(?:\n|$)|\n[ \t]*\n)", text, flags=re.MULTILINE)
    return "".join(mask_paragraph(block) for block in blocks)


def section(mask, version):
    if not SEMVER.fullmatch(version):
        raise ValueError(f"invalid SemVer version: {version!r}")
    headings = HEADING.finditer(mask)
    first = next(headings, None)
    if not first or first[1] != "[Unreleased]":
        raise ValueError("expected ## [Unreleased] before the first release")
    latest = next(headings, None)
    if not latest:
        raise ValueError(f"expected {version!r} as the first release below Unreleased")
    dated = re.fullmatch(r"\[([^\]]+)\] - ([0-9]{4}-[0-9]{2}-[0-9]{2})", latest[1])
    if not dated:
        raise ValueError(f"expected a dated release heading for {version}")
    if dated[1] != version:
        raise ValueError(f"first changelog release is {dated[1]!r}, expected {version!r}")
    date.fromisoformat(dated[2])
    following = next((h for h in headings if re.match(rf"\[(?:{SEMVER.pattern})\](?: |$)", h[1])), None)
    return latest.end(), following.start() if following else len(mask)


class SourceLinks:
    """Resolve local URLs against the Git checkout containing the changelog."""

    def __init__(self, changelog):
        self.changelog = changelog.resolve()

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.changelog.parent), *args],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()

    @cached_property
    def source(self):
        repository = os.environ.get("GITHUB_REPOSITORY")
        if repository:
            server = os.environ.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
            base = f"{server}/{repository}"
        else:
            remote = self.git("remote", "get-url", "origin").removesuffix(".git")
            match = re.fullmatch(r"(?:https://|git@|ssh://git@)([\w.-]+)[:/]([\w.-]+/[\w.-]+)", remote)
            if not match:
                raise ValueError("cannot resolve relative links: set GITHUB_REPOSITORY and GITHUB_SERVER_URL")
            base = f"https://{match[1]}/{match[2]}"
        revision = self.git("rev-parse", "--verify", "HEAD^{commit}")
        path = self.git("rev-parse", "--show-prefix") + self.changelog.name
        return base, revision, path

    def resolve(self, target, image=False):
        destination = html.unescape(re.sub(ESCAPE, lambda m: m[0][1], target))
        url = urlsplit(destination)
        if url.scheme or url.netloc:
            return target
        base, revision, changelog_path = self.source
        path = changelog_path
        if url.path:
            path = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(url.path))).lstrip("/")
            if path == ".." or path.startswith("../"):
                raise ValueError(f"link leaves the candidate repository: {target}")
        route = "raw" if image else "blob"
        path = quote(path, safe="/")
        query = quote(url.query, safe="%=&+/?:,@")
        fragment = quote(url.fragment, safe="/%")
        return urlunsplit(("", "", f"{base}/{route}/{revision}/{path}", query, fragment))


def label_key(label):
    return " ".join(label.split()).casefold()


def inline_url(text, start):
    """Return the destination span and end of a Markdown inline link."""
    opening = re.match(r"\(\s*", text[start:])
    if not opening:
        return None
    left = start + opening.end()
    if text.startswith("<", left):
        angle = re.compile(ANGLE_URL).match(text, left)
        if not angle:
            return None
        right = angle.end()
    else:
        right = left
        depth = 0
        while right < len(text) and not text[right].isspace():
            char = text[right]
            if char == "\\" and right + 1 < len(text):
                right += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if not depth:
                    break
                depth -= 1
            right += 1
        if depth:
            return None
    ending = INLINE_END.match(text, right)
    return (left, right, ending.end()) if ending else None


def replace_spans(text, edits):
    parts = []
    previous = 0
    for start, end, replacement in sorted(edits):
        parts.extend((text[previous:start], replacement))
        previous = end
    return "".join(parts) + text[previous:]


def rewrite_body(body, mask, definitions, links):
    used = {}
    edits = []
    for tag in HTML_TAG.finditer(mask):
        for attr in HTML_ATTRIBUTE.finditer(tag[0]):
            if attr["name"].lower() not in {"href", "src"} or not attr["value"]:
                continue
            start, end = attr.span("value")
            if attr["value"][0] in {"'", '"'}:
                start += 1
                end -= 1
            start += tag.start()
            end += tag.start()
            target = body[start:end]
            edits.append((start, end, links.resolve(target, attr["name"].lower() == "src")))
    mask = HTML_BLOCK.sub(lambda m: blank(m[0]), mask)
    mask = HTML_TAG.sub(lambda m: blank(m[0]), mask)
    stack = []
    skip = 0
    for token in LINK_TOKEN.finditer(mask):
        if token.start() < skip or token[0].startswith("\\"):
            continue
        if token[0] == "[":
            stack.append(token.start())
            continue
        if not stack:
            continue
        opener = stack.pop()
        image = mask[opener - 1:opener] == "!"
        after = token.end()
        inline = inline_url(body, after) if mask.startswith("(", after) else None
        if inline:
            left, right, skip = inline
            if body.startswith("<", left):
                left += 1
                right -= 1
            edits.append((left, right, links.resolve(body[left:right], image)))
            continue
        label = body[opener + 1:token.start()]
        explicit = re.compile(LABEL).match(mask, after)
        if explicit and label_key(explicit[1]) in definitions:
            label = explicit[1]
            skip = explicit.end()
        elif mask.startswith("[]", after):
            skip = after + 2
        key = label_key(label)
        if key in definitions:
            used[key] = image or used.get(key, False)
    return replace_spans(body, edits), used


def release_notes(changelog: Path, version: str) -> str:
    text = changelog.read_text(encoding="utf-8")
    mask = inline_mask(block_mask(text))
    mask = HTML_LITERAL.sub(lambda m: blank(m[0]), mask)
    markdown = HTML_BLOCK.sub(lambda m: blank(m[0]), mask)
    start, end = section(markdown, version)
    definitions = {}
    inside = []
    for definition in DEFINITION.finditer(markdown):
        key = label_key(definition[1])
        definitions.setdefault(key, definition)
        if start <= definition.start() < end:
            inside.append((definition.start() - start, definition.end() - start, ""))
    body = replace_spans(text[start:end], inside)
    body_mask = replace_spans(mask[start:end], inside)
    links = SourceLinks(changelog)
    body, used = rewrite_body(body, body_mask, definitions, links)
    body = body.strip("\n")
    if not body.strip():
        raise ValueError(f"release {version} has no notes")
    required = []
    for key, definition in definitions.items():
        if key not in used:
            continue
        left, right = definition.span("url")
        if text[left] == "<":
            left += 1
            right -= 1
        required.append(text[definition.start():left] + links.resolve(text[left:right], used[key])
                        + text[right:definition.end()])
    if required:
        body += "\n\n" + "\n".join(required)
    return body + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changelog", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        notes = release_notes(args.changelog, args.version)
        args.output.write_text(notes, encoding="utf-8", newline="\n")
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"release notes: {exc}\n")


if __name__ == "__main__":
    main()
