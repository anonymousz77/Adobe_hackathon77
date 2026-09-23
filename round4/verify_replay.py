#!/usr/bin/env python3
"""Prove REPLAY_<TeamName>.txt actually replays, before a judge finds out it doesn't.

Round 4 has an unverified floor: a missing or unparseable manifest, or no
working invoke path, and the submission is tagged ran-blocked regardless of how
good the engine is. That failure is silent until someone else runs it, so this
script is the someone else.

It parses the manifest the way a judge reading fixed labelled fields would,
refuses anything still carrying a placeholder, then actually executes the
documented run against each declared URL and checks the report lands where
EXPECTED_OUTPUT promises and satisfies the Round 3 schema floor.

    python3 round4/verify_replay.py round4/REPLAY_TeamName.txt
    python3 round4/verify_replay.py round4/REPLAY_TeamName.txt --offline
    python3 round4/verify_replay.py round4/REPLAY_TeamName.txt --no-run

--offline swaps the declared URLs for a shipped fixture, so the manifest's
shape and the invoke path can be checked with no network. --no-run stops after
parsing.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / "brand-ai-readiness-audit"
ENTRYPOINT = MARKETPLACE / "skills" / "ai-readiness-orchestrator" / "scripts" / "orchestrate.py"

REQUIRED_FIELDS = [
    "TEST_SITE_URLS",
    "LLM_MODEL",
    "AGENT_HARNESS",
    "ENV_SETUP",
    "TEST_STEPS",
    "EXPECTED_OUTPUT",
]

# Anything that means "not filled in yet".
PLACEHOLDER = re.compile(r"<<.*?>>|YourTeamName|TeamName|TODO|FIXME|xxx", re.IGNORECASE)

FAILURES: list[str] = []
CHECKS = 0


def check(ok: bool, label: str, detail: str = "") -> bool:
    global CHECKS
    CHECKS += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{('  ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(label)
    return ok


def parse_manifest(path: Path) -> dict[str, str]:
    """Fixed labelled fields, comments stripped, continuations folded in.

    Deliberately forgiving in the same way a human reader is: a blank line or a
    comment does not end a field, but the next LABEL: at column zero does.
    """
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]*):\s*(.*)$", raw)
        if m:
            current = m.group(1)
            fields[current] = [m.group(2).strip()]
        elif current and raw.strip():
            fields[current].append(raw.strip())
    return {k: "\n".join(v).strip() for k, v in fields.items()}


def schema_floor(report: dict) -> list[str]:
    """The Round 3 report floor the Round 4 run still has to satisfy."""
    problems = []
    for key in ("site", "audited_at", "summary", "findings"):
        if key not in report:
            problems.append(f"missing top-level {key!r}")
    for key in ("total_findings", "critical", "high", "medium", "low"):
        if key not in report.get("summary", {}):
            problems.append(f"missing summary.{key}")
    needed = {"id", "title", "severity", "evidence", "suggested_action"}
    for f in report.get("findings", []):
        gap = needed - set(f)
        if gap:
            problems.append(f"{f.get('id', '?')} missing {sorted(gap)}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--offline", action="store_true",
                    help="audit a shipped fixture instead of the declared URLs")
    ap.add_argument("--no-run", action="store_true", help="parse and validate only")
    ap.add_argument("--time-budget", default="300")
    args = ap.parse_args(argv)

    print(f"\nmanifest: {args.manifest}\n")

    if not check(args.manifest.is_file(), "manifest exists", str(args.manifest)):
        return 1

    name_ok = args.manifest.name.startswith("REPLAY_") and args.manifest.suffix == ".txt"
    check(name_ok, "named REPLAY_<TeamName>.txt", args.manifest.name)
    check(not PLACEHOLDER.search(args.manifest.name),
          "team name filled into the filename", args.manifest.name)

    fields = parse_manifest(args.manifest)
    print()
    for key in REQUIRED_FIELDS:
        value = fields.get(key, "")
        if not check(bool(value), f"{key} present"):
            continue
        check(not PLACEHOLDER.search(value), f"{key} has no placeholder left",
              "" if not PLACEHOLDER.search(value) else f"-> {PLACEHOLDER.search(value).group(0)!r}")

    print()
    urls = [u.strip() for u in fields.get("TEST_SITE_URLS", "").split(",") if u.strip()]
    check(bool(urls), "TEST_SITE_URLS parses to at least one URL", f"{len(urls)} found")
    check(all(u.startswith(("http://", "https://")) for u in urls),
          "every URL is an exact full URL", ", ".join(urls[:3]))

    # The brief names the model version and the harness version explicitly.
    check(bool(re.search(r"\d", fields.get("LLM_MODEL", ""))),
          "LLM_MODEL names a version or date", fields.get("LLM_MODEL", ""))
    check(bool(re.search(r"\d", fields.get("AGENT_HARNESS", ""))),
          "AGENT_HARNESS names a version", fields.get("AGENT_HARNESS", ""))

    steps = fields.get("TEST_STEPS", "")
    check("orchestrate.py" in steps,
          "TEST_STEPS points at the marketplace entrypoint")
    check(bool(re.search(r"^\s*1[.)]", steps, re.M)),
          "TEST_STEPS is an ordered, copy-pasteable list")

    check(ENTRYPOINT.is_file(), "entrypoint exists where the manifest says",
          str(ENTRYPOINT.relative_to(ROOT)))

    if args.no_run:
        return report_out()

    # ---- actually run it -------------------------------------------------
    expected = fields.get("EXPECTED_OUTPUT", "")
    targets = ["offline-fixture"] if args.offline else urls
    print()
    for target in targets:
        out = Path(tempfile.mkdtemp(prefix="replay-"))
        try:
            cmd = [sys.executable, str(ENTRYPOINT)]
            if args.offline:
                cmd += ["--offline-root", "tests/fixtures/site_b"]
            else:
                cmd.append(target)
            cmd += ["--out", str(out), "--time-budget", args.time_budget]

            proc = subprocess.run(cmd, cwd=str(MARKETPLACE), capture_output=True,
                                  text=True, timeout=float(args.time_budget) + 120)
            label = target if len(target) < 48 else target[:45] + "..."
            if not check(proc.returncode == 0, f"run exits 0 · {label}",
                         proc.stderr.strip()[:160]):
                continue

            report_path = out / "audit-report.json"
            if not check(report_path.is_file(), f"report written · {label}"):
                continue

            # EXPECTED_OUTPUT must name the file a judge will actually look for.
            check(Path(expected).name == report_path.name,
                  f"EXPECTED_OUTPUT names the emitted file · {label}", expected)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            problems = schema_floor(report)
            check(not problems, f"report satisfies the Round 3 schema floor · {label}",
                  "; ".join(problems[:2]))

            s = report["summary"]
            print(f"         -> {s['total_findings']} findings "
                  f"({s['critical']} critical, {s['high']} high, {s['medium']} medium) "
                  f"· status {report.get('audit_status')}")

            # A judge who picks their own URL sees this too: a run that assessed
            # nothing is not a clean bill of health.
            if report.get("audit_status") not in ("complete", "partial"):
                print(f"         !! audit_status={report.get('audit_status')!r} — "
                      f"the audit could not see this site; pick a different demo URL")
        finally:
            shutil.rmtree(out, ignore_errors=True)

    return report_out()


def report_out() -> int:
    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)} of {CHECKS} checks:")
        for f in FAILURES:
            print("  - " + f)
        print("\nA judge following this manifest would be blocked. Fix these first.")
        return 1
    print(f"OK: {CHECKS} checks passed. A judge can replay this manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
