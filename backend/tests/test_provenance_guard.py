from __future__ import annotations

import importlib.util
from pathlib import Path

GUARD_PATH = Path(__file__).parents[2] / "scripts" / "provenance_guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("intelamp_provenance_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load provenance guard")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_guard_accepts_clean_source(tmp_path: Path) -> None:
    guard = load_guard()
    source = tmp_path / "source"
    source.mkdir()
    (source / "clean.py").write_text("from pathlib import Path\n", encoding="utf-8")
    gpl_reference = tmp_path / "chathub-dev"
    gpl_reference.mkdir()
    assert guard.scan_sources([source], gpl_reference_path=gpl_reference) == []


def test_guard_rejects_configured_gpl_reference_path(tmp_path: Path) -> None:
    guard = load_guard()
    source = tmp_path / "source"
    source.mkdir()
    gpl_reference = tmp_path / "chathub-dev"
    gpl_reference.mkdir()
    (source / "bad.ts").write_text(f'const copiedFrom = "{gpl_reference}";\n', encoding="utf-8")
    issues = guard.scan_sources([source], gpl_reference_path=gpl_reference)
    assert [issue.code for issue in issues] == ["gpl_reference_path"]


def test_guard_rejects_copied_gpl_header_marker(tmp_path: Path) -> None:
    guard = load_guard()
    source = tmp_path / "source"
    source.mkdir()
    (source / "bad.ts").write_text("GNU GENERAL PUBLIC LICENSE version 3\n", encoding="utf-8")
    issues = guard.scan_sources([source], gpl_reference_path=None)
    assert [issue.code for issue in issues] == ["gpl_header_marker"]
