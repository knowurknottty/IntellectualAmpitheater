#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Iterable, NamedTuple
from pathlib import Path

TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".html", ".toml", ".json", ".sh"}
GPL_MARKERS = (
    "GNU GENERAL PUBLIC LICENSE",
    "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License",
)


class Issue(NamedTuple):
    code: str
    path: Path
    detail: str


def _text_files(roots: Iterable[Path]):
    for root in roots:
        if root.is_file():
            candidates = [root]
        elif root.exists():
            candidates = sorted(path for path in root.rglob("*") if path.is_file())
        else:
            continue
        for path in candidates:
            if path.suffix.lower() in TEXT_SUFFIXES:
                yield path


def scan_sources(roots: Iterable[Path], *, gpl_reference_path: Path | None) -> list[Issue]:
    issues: list[Issue] = []
    gpl_tokens: tuple[str, ...] = ()
    if gpl_reference_path is not None:
        resolved = str(gpl_reference_path.expanduser().resolve())
        gpl_tokens = (resolved, str(gpl_reference_path.expanduser()))
    for path in _text_files(roots):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in GPL_MARKERS:
            if marker in text:
                issues.append(Issue("gpl_header_marker", path, marker))
                break
        if gpl_tokens and any(token and token in text for token in gpl_tokens):
            issues.append(Issue("gpl_reference_path", path, str(gpl_reference_path)))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Narrow provenance tripwire for IntelAMP source trees")
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--gpl-reference-path", type=Path, default=None)
    args = parser.parse_args()
    issues = scan_sources(args.roots, gpl_reference_path=args.gpl_reference_path)
    for issue in issues:
        print(f"{issue.code}: {issue.path}: {issue.detail}")
    if issues:
        print(f"PROVENANCE_GUARD=FAIL issues={len(issues)}")
        return 1
    print("PROVENANCE_GUARD=PASS issues=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
