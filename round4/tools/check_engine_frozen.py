#!/usr/bin/env python3
"""Prove the engine you are about to demo is the Round 3 submission, byte for byte.

Round 4, Section 6: "a demo engine that differs from the submitted engine" is an
integrity failure, forced to the bottom whatever the rubric score. That failure
is quiet -- a typo fixed in a SKILL.md, an editor rewriting line endings -- so
this checks it instead of trusting anyone to remember:

  1. submission.zip has the SHA-256 pinned in round4/SUBMITTED_ZIP.sha256,
     i.e. it is the file the judges already hold;
  2. brand-ai-readiness-audit/ in this repo is byte-identical to that zip,
     nothing added, nothing missing (same exclusions package_submission.py uses);
  3. with --unzipped DIR: the folder you will actually record from is also
     byte-identical to the zip. Run outputs (audit-output/, __pycache__/) and the
     harness's own skill copy (.claude/, checked separately) are allowed.

    python3 round4/tools/check_engine_frozen.py
    python3 round4/tools/check_engine_frozen.py --unzipped ~/round4-demo/brand-ai-readiness-audit

Standard library only. Exit 0 = frozen, 1 = anything differs.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO / "brand-ai-readiness-audit"
ZIP = REPO / "submission.zip"
PIN_FILE = REPO / "round4" / "SUBMITTED_ZIP.sha256"

# Mirrors package_submission.py: a file it never ships is not drift.
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".idea", ".vscode",
                "audit-output", "evidence", ".venv", "venv"}
EXCLUDE_NAMES = {".DS_Store", ".gitattributes", ".gitignore"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".zip"}

# In the folder a demo runs from, these are outputs of the run or the harness's
# wiring, never part of the engine. Any other top-level folder that holds an
# audit-report.json (e.g. ./audit-replay from a --bundle re-analysis) is run
# output too.
DEMO_ALLOWED_TOP = {"audit-output", ".claude", "__pycache__"}

FAILURES: list[str] = []


def ok(passed: bool, label: str, detail: str = "") -> bool:
    print(f"[{'PASS' if passed else 'FAIL'}] {label}{('  ' + detail) if detail else ''}")
    if not passed:
        FAILURES.append(label)
    return passed


def pinned() -> str:
    for line in PIN_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line.split()[0]
    return ""


def zip_files(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as zf:
        return {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}


def tree_files(root: Path, demo: bool = False) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    outputs = set(DEMO_ALLOWED_TOP)
    if demo:
        outputs |= {d.name for d in root.iterdir() if d.is_dir() and (d / "audit-report.json").is_file()}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if demo and rel.parts[0] in outputs:
            continue
        if any(p in EXCLUDE_DIRS for p in rel.parts):
            continue
        if path.name in EXCLUDE_NAMES or path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        out[rel.as_posix()] = path.read_bytes()
    return out


def compare(label: str, tree: dict[str, bytes], packed: dict[str, bytes]) -> None:
    only_tree = sorted(set(tree) - set(packed))
    only_zip = sorted(set(packed) - set(tree))
    changed = sorted(p for p in set(tree) & set(packed) if tree[p] != packed[p])
    ok(not (only_tree or only_zip or changed), f"{label} is byte-identical to submission.zip",
       f"{len(tree)} files" if not (only_tree or only_zip or changed) else "")
    for name, items in (("extra", only_tree), ("missing", only_zip), ("MODIFIED", changed)):
        for p in items[:10]:
            print(f"         {name}: {p}")
        if len(items) > 10:
            print(f"         ... and {len(items) - 10} more {name}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", type=Path, default=ZIP, help="the zip to check (default: repo submission.zip)")
    ap.add_argument("--unzipped", type=Path, help="also check the folder you will record the demo from")
    args = ap.parse_args(argv)

    if not ok(args.zip.is_file(), "submission.zip present", str(args.zip)):
        return 1
    digest = hashlib.sha256(args.zip.read_bytes()).hexdigest()
    ok(digest == pinned(), "submission.zip is the pinned Round 3 artifact", digest)

    packed = zip_files(args.zip)
    compare("brand-ai-readiness-audit/ (repo)", tree_files(MARKETPLACE), packed)

    if args.unzipped:
        root = args.unzipped.expanduser().resolve()
        if ok((root / "marketplace.json").is_file(), "demo folder is a marketplace root", str(root)):
            compare(f"demo folder {root.name}/", tree_files(root, demo=True), packed)
            skills_copy = root / ".claude" / "skills"
            if skills_copy.exists():
                # Claude Code discovers skills under .claude/skills. That copy must
                # be the submitted skills/ exactly, or the harness would load
                # something other than what was submitted.
                shipped = {k[len("skills/"):]: v for k, v in packed.items() if k.startswith("skills/")}
                compare(".claude/skills (harness copy)", tree_files(skills_copy), shipped)

    print()
    if FAILURES:
        print("NOT FROZEN. The engine differs from the Round 3 submission, which is an")
        print("integrity failure in Round 4. Re-unpack submission.zip; never edit the engine.")
        return 1
    print("FROZEN: what you demo is exactly what was submitted in Round 3.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
