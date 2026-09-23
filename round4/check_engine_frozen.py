#!/usr/bin/env python3
"""The Round 3 engine is frozen. This is what stops it quietly thawing.

Round 4's integrity gate: "if the engine shown differs from what you submitted
in Round 3, the submission fails on integrity grounds." That failure is not
loud. Nobody edits the marketplace meaning to break it -- they fix a typo in a
SKILL.md, regenerate a golden, let an editor rewrite line endings -- and the
tree silently stops matching the artifact a judge holds.

So the invariant is checked, not remembered:

    every file in brand-ai-readiness-audit/ is byte-identical to the
    corresponding entry in submission.zip, with nothing extra and nothing
    missing

Hold that, and whatever you demo out of the working tree IS what was submitted.

    python3 round4/check_engine_frozen.py          # tree vs zip
    python3 round4/check_engine_frozen.py --pin    # record the zip's hash
    python3 round4/check_engine_frozen.py --against <uploaded.zip>

--pin writes round4/SUBMITTED.sha256. Run it ONCE, against the file you
actually uploaded to the Round 3 form -- confirm with `sha256sum` first. From
then on the guard also fails if submission.zip is rebuilt, which is the case a
tree-vs-zip comparison alone cannot see: rebuilding makes both sides agree with
each other and disagree with the judges' copy.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / "brand-ai-readiness-audit"
DEFAULT_ZIP = ROOT / "submission.zip"
PIN_FILE = Path(__file__).resolve().parent / "SUBMITTED.sha256"

# Mirrors package_submission.py. A file it never ships is not drift.
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".idea", ".vscode",
                "audit-output", "evidence", ".venv", "venv"}
EXCLUDE_NAMES = {".DS_Store", ".gitattributes", ".gitignore"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".zip"}


def tree_files() -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for path in MARKETPLACE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(MARKETPLACE)
        if any(p in EXCLUDE_DIRS for p in rel.parts):
            continue
        if path.name in EXCLUDE_NAMES or path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        out[rel.as_posix()] = path.read_bytes()
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--against", type=Path, default=DEFAULT_ZIP,
                    help="the zip to treat as the submitted artifact")
    ap.add_argument("--pin", action="store_true",
                    help="record this zip's SHA-256 as the submitted one")
    args = ap.parse_args(argv)

    zip_path: Path = args.against
    if not zip_path.is_file():
        print(f"FAIL: no such zip: {zip_path}", file=sys.stderr)
        return 1

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    if args.pin:
        PIN_FILE.write_text(
            f"# SHA-256 of the zip uploaded for Round 3. The engine demoed in the\n"
            f"# Round 4 video must be this one. Re-pin only if you re-upload.\n"
            f"{digest}  {zip_path.name}\n", encoding="utf-8")
        print(f"pinned {digest}  ({zip_path.name})\n  -> {PIN_FILE.relative_to(ROOT)}")
        return 0

    failures: list[str] = []

    # 1. The artifact itself has not been rebuilt under us.
    if PIN_FILE.is_file():
        pinned = next((l.split()[0] for l in PIN_FILE.read_text(encoding="utf-8").splitlines()
                       if l.strip() and not l.startswith("#")), "")
        if pinned == digest:
            print(f"[PASS] zip matches the pinned submission  {digest[:16]}...")
        else:
            print(f"[FAIL] zip does NOT match the pinned submission")
            print(f"       pinned : {pinned}")
            print(f"       on disk: {digest}")
            failures.append("zip differs from the pinned submission")
    else:
        print(f"[WARN] no pin recorded — run --pin against the uploaded zip")
        print(f"       on disk: {digest}")

    # 2. The working tree still equals the artifact.
    with zipfile.ZipFile(zip_path) as zf:
        packed = {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}
    tree = tree_files()

    only_tree = sorted(set(tree) - set(packed))
    only_zip = sorted(set(packed) - set(tree))
    differing = sorted(p for p in (set(tree) & set(packed)) if tree[p] != packed[p])

    for label, items in (("added to the tree but not in the zip", only_tree),
                         ("in the zip but missing from the tree", only_zip),
                         ("present in both but MODIFIED", differing)):
        if items:
            print(f"[FAIL] {len(items)} file(s) {label}:")
            for p in items[:10]:
                print(f"         {p}")
            if len(items) > 10:
                print(f"         ... and {len(items) - 10} more")
            failures.append(label)

    if not (only_tree or only_zip or differing):
        print(f"[PASS] working tree is byte-identical to the zip  "
              f"({len(tree)} files)")

    print()
    if failures:
        print("FROZEN ENGINE VIOLATED. The marketplace must not change after the")
        print("Round 3 submission — Round 4 demos the submitted engine, and a")
        print("mismatch is an integrity failure, not a deduction.")
        print("\nEither revert the marketplace changes, or — only if you have not")
        print("yet submitted — rebuild with `python3 package_submission.py` and")
        print("re-pin with `--pin`.")
        return 1

    print("OK: the engine is frozen. What you demo is what you submitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
