#!/usr/bin/env python3
"""Dry-run the REPLAY manifest's agent steps headless, exactly as written.

Recording is one take, so the take should not be the first time the steps run.
This script follows TEST_STEPS from a clean folder and prints what the agent
did, so a mismatch surfaces here instead of on camera:

  1. copies submission.zip into a fresh folder, unpacks it, and makes the
     .claude/skills copy -- the same three operations as step 1;
  2. takes the prompt verbatim from step 2 of the manifest and appends the URL;
  3. starts Claude Code with the manifest's own `claude --model ...` line, in
     print mode, and records the session as stream-json.

It then reports: the harness version, the model the session ran on, whether
the agent loaded the entrypoint with the Skill tool, the exact engine command
it ran, whether the report landed at EXPECTED_OUTPUT, and the agent's reply.

    python3 round4/tools/rehearse_agent.py https://www.theguardian.com/
    python3 round4/tools/rehearse_agent.py https://example.com/ --keep ./rehearsal

Needs the disclosed harness installed and signed in. Costs one agent session.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "round4" / "REPLAY_IT_Professionals.txt"
ZIP = REPO / "submission.zip"


def manifest_parts(path: Path) -> tuple[str, list[str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    prompt = ""
    for i, line in enumerate(lines):
        if "Paste this prompt verbatim" in line:
            prompt = lines[i + 1].strip()
            break
    claude_line = next((l.strip() for l in lines if l.strip().startswith("claude --model")), "")
    expected = re.search(r"^EXPECTED_OUTPUT:\s*(\S+)", text, re.M)
    if not prompt or not claude_line or not expected:
        sys.exit("error: could not find the prompt, the claude command or EXPECTED_OUTPUT in the manifest")
    return prompt, shlex.split(claude_line), expected.group(1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--zip", type=Path, default=ZIP)
    ap.add_argument("--keep", type=Path, help="run in this folder and keep it (default: a temp folder)")
    ap.add_argument("--timeout", type=float, default=900)
    args = ap.parse_args(argv)

    prompt, claude_argv, expected = manifest_parts(args.manifest)
    top = args.keep.resolve() if args.keep else Path(tempfile.mkdtemp(prefix="rehearse-"))
    if top.exists() and any(top.iterdir()):
        sys.exit(f"error: {top} is not empty; give an empty or new folder")
    top.mkdir(parents=True, exist_ok=True)

    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    print(f"harness: {version}")
    print(f"folder:  {top}")

    # Step 1, the same three operations the manifest lists.
    shutil.copy2(args.zip, top / "submission.zip")
    with zipfile.ZipFile(top / "submission.zip") as zf:
        zf.extractall(top / "brand-ai-readiness-audit")
    root = top / "brand-ai-readiness-audit"
    shutil.copytree(root / "skills", root / ".claude" / "skills")

    # Steps 2-3: the manifest's own claude line, headless, with the verbatim prompt.
    full_prompt = f"{prompt} {args.url}"
    cmd = claude_argv + ["-p", full_prompt, "--output-format", "stream-json", "--verbose"]
    print(f"$ {' '.join(shlex.quote(c) for c in claude_argv)}  (print mode)")
    print(f"prompt: {len(prompt)} characters from step 2, then: {args.url}\n")
    started = time.monotonic()
    proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=args.timeout,
                          stdin=subprocess.DEVNULL)
    elapsed = time.monotonic() - started
    (top / "session.jsonl").write_text(proc.stdout, encoding="utf-8")

    skill_loaded, engine_cmds, model, final = False, [], "", ""
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            model = event.get("model", "")
        if event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") != "tool_use":
                    continue
                if block["name"] == "Skill" and block["input"].get("skill") == "ai-readiness-orchestrator":
                    skill_loaded = True
                if block["name"] == "Bash" and "orchestrate.py" in block["input"].get("command", ""):
                    engine_cmds.append(block["input"]["command"])
                print(f"  tool: {block['name']:<5} {json.dumps(block['input'])[:220]}")
        if event.get("type") == "result":
            final = event.get("result") or ""

    report = top / expected
    print(f"\nmodel the session ran on: {model}")
    print(f"[{'PASS' if skill_loaded else 'FAIL'}] agent loaded the entrypoint with the Skill tool")
    print(f"[{'PASS' if engine_cmds else 'FAIL'}] agent ran the marketplace entrypoint: "
          f"{engine_cmds[-1] if engine_cmds else '-'}")
    print(f"[{'PASS' if report.is_file() else 'FAIL'}] report at EXPECTED_OUTPUT ({expected})")
    print(f"elapsed: {elapsed:.0f} s, exit {proc.returncode}\n")
    print(final)
    if not args.keep:
        shutil.rmtree(top, ignore_errors=True)
    return 0 if (skill_loaded and engine_cmds and report.is_file() and proc.returncode == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
