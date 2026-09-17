#!/usr/bin/env python3
"""Lightweight, dependency-free validation for this static OAuth info site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
PAGES = {
    "home": ROOT / "index.html",
    "privacy": ROOT / "privacy" / "index.html",
    "terms": ROOT / "terms" / "index.html",
}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
REQUIRED = {
    "home": [
        "Personal automation, under Robert’s direction.",
        "private, single-user automation service",
        "Gmail, Google Calendar, Google Contacts, Google Drive, Google Docs, and Google Sheets",
        'href="/privacy/"',
        'href="/terms/"',
    ],
    "privacy": [
        "Operator and contact",
        "piazzr2@gmail.com",
        "Gmail message content and mail metadata",
        "Google Calendar event details",
        "Google Contacts profile data",
        "Google Docs document content",
        "Google Drive files and file metadata",
        "Google Sheets spreadsheets and their data",
        "gmail.modify",
        "calendar.events",
        "contacts.readonly",
        "documents.readonly",
        "drive.file",
        "drive.readonly",
        "spreadsheets",
        "configured AI model or provider",
        "not sold, used for advertising, or used for data brokerage",
        "as needed to carry out Robert’s user-directed functionality, as required by law, or as Robert explicitly directs",
        "Access, retention, and removal",
        "Security",
        "Updates and contact",
    ],
    "terms": [
        "personal, non-public Hermes service",
        "Permitted use",
        "No warranty",
        "Changes and contact",
        "piazzr2@gmail.com",
    ],
}
BANNED_PUBLIC_CLAIMS = (
    "end-to-end encrypted",
    "encrypted at rest",
    "iso 27001",
    "soc 2",
    "certified",
    "never leaves the host",
    "we never share",
)


class StructureParser(HTMLParser):
    """Report a small, useful subset of malformed HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.scripts = 0
        self.external_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.scripts += 1
        attributes = dict(attrs)
        for key in ("href", "src"):
            value = attributes.get(key)
            if value and re.match(r"https?://", value):
                self.external_assets.append(value)
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.scripts += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"unexpected closing </{tag}>")
        elif self.stack[-1] != tag:
            self.errors.append(f"expected </{self.stack[-1]}> before </{tag}>")
        else:
            self.stack.pop()


def validate_page(name: str, path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{name}: missing {path.relative_to(ROOT)}"]

    source = path.read_text(encoding="utf-8")
    parser = StructureParser()
    parser.feed(source)
    parser.close()
    if parser.stack:
        parser.errors.append("unclosed tags: " + ", ".join(parser.stack))
    for error in parser.errors:
        errors.append(f"{name}: HTML structure: {error}")
    if "<!doctype html>" not in source.lower():
        errors.append(f"{name}: missing HTML5 doctype")
    if parser.scripts:
        errors.append(f"{name}: scripts are not permitted")
    if parser.external_assets:
        errors.append(f"{name}: external assets are not permitted: {', '.join(parser.external_assets)}")
    for required in REQUIRED[name]:
        if required not in source:
            errors.append(f"{name}: missing required copy or link: {required!r}")
    normalized = source.casefold()
    for claim in BANNED_PUBLIC_CLAIMS:
        if claim in normalized:
            errors.append(f"{name}: unsupported public claim: {claim!r}")
    return errors


def main() -> int:
    errors: list[str] = []
    cname = ROOT / "CNAME"
    if not cname.is_file() or cname.read_text(encoding="utf-8").strip() != "hermes.robertpiazza.com":
        errors.append("CNAME must contain exactly hermes.robertpiazza.com")
    for name, path in PAGES.items():
        errors.extend(validate_page(name, path))
    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALIDATION PASSED: CNAME, three pages, required policy copy, and static-only constraints are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
