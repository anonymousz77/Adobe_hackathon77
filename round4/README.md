# Round 4 — Prototype Showcase (Live Agent Demo)

**Team IT_Professionals** · Lakshya, Tanmay, Kalpit · Adobe University Hackathon 2026

Round 4 shows the Round 3 marketplace working live, driven by an AI agent in a
CLI, and makes the run reproducible. The engine is **not** rebuilt: the
Round 3 package is used exactly as submitted.

## What to submit

| Upload | File |
|---|---|
| The video (≤ 5:00; Part 1 ≤ 3:00, Part 2 ≤ 2:00) | recorded from [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md) following [`RECORDING_RUNBOOK.md`](RECORDING_RUNBOOK.md) |
| The reproduction manifest | [`REPLAY_IT_Professionals.txt`](REPLAY_IT_Professionals.txt), unchanged |

The Round 3 `submission.zip` is not resubmitted; the judges already hold it.

## The run at a glance

| | |
|---|---|
| Engine | Round 3 `submission.zip`, unchanged: SHA-256 `1c872c598dcac741c712cbf9e671f024881a9ba251e2b4da66995f81b6cf8dcf` (pinned in [`SUBMITTED_ZIP.sha256`](SUBMITTED_ZIP.sha256)) |
| Entrypoint skill | `skills/ai-readiness-orchestrator` (`SKILL.md` → `scripts/orchestrate.py`) |
| Agent harness | Claude Code v2.1.282 |
| Model | Claude Opus 5.5 (`claude-opus-5-5`) |
| Video URL | https://www.theguardian.com/ (the manifest also lists https://example.com/) |
| Engine command | `python skills/ai-readiness-orchestrator/scripts/orchestrate.py <URL> --out ./audit-output --no-render` |
| Report | `brand-ai-readiness-audit/audit-output/audit-report.json`, plus `report.md`, `fix_patches/`, `evidence/` |
| Setup | Python 3.9+, standard library only; Node.js for the harness |

## In this folder

| File | What it is for |
|---|---|
| `REPLAY_IT_Professionals.txt` | **The manifest.** Six fixed fields, then commentary: a harness-free fallback, what the video's run finds, determinism, and the frozen engine's known limits |
| `VIDEO_SCRIPT.md` | Word-budgeted narration. Every Part 1 claim names the file and line on screen; Part 2 is a shot list for the live run |
| `RECORDING_RUNBOOK.md` | Pinned setup, same-day pre-flight, how to record and edit within the rules, upload checklist |
| `LIVE_TEST_REPORT.md` | What we ran before recording: 20 real sites, rendering on and off, determinism, seven agent rehearsals, the findings we checked by hand, and the decisions that followed |
| `SUBMITTED_ZIP.sha256` | The pinned hash of the Round 3 artifact |
| `urls/generalization.txt` | The 20 sites used to test generalisation |
| `tools/check_engine_frozen.py` | Proves this repo's marketplace, and the folder you record from, are byte-identical to the pinned zip |
| `tools/verify_replay.py` | Replays the manifest like a judge: parses and cross-checks every field, runs the documented command on each URL, checks the report lands at `EXPECTED_OUTPUT`; `--twice` adds run-to-run and saved-bundle determinism |
| `tools/rehearse_agent.py` | Runs the manifest's agent steps headless (`claude -p`), prompt taken verbatim from the file |
| `tools/live_matrix.py` | Runs the unchanged engine on any list of URLs from a fresh unzip; `--verify N` re-checks the top confirmed findings against the live site |
| `tools/digest.py` | One reviewable table for a folder of reports, including pages a CDN answered with a bot check |

All tools use the Python standard library only.

## Checks that run on every push

[`.github/workflows/round4.yml`](../.github/workflows/round4.yml), on a clean
runner with Python 3.11.15:

1. **frozen-engine**: the zip matches the pinned hash, the repo's marketplace
   is byte-identical to it, and the engine's own suites (validator, goldens,
   ten test files) pass from a fresh unzip.
2. **replay-manifest**: `verify_replay.py --twice` on the manifest.
3. **generalization** + **digest**: the unchanged engine on the 20 sites in
   `urls/generalization.txt`, and one table of the results.

The Round 3 `ci.yml` still runs too and still fails its golden step on Python
3.9 and 3.12, exactly as on `final-submission`: the goldens record the Python
version they were made with (3.11.15). It is a Round 3 file, so it stays as it
was; the `frozen-engine` job above runs the same goldens on 3.11.15 and passes.

## Integrity

This branch adds files and changes none. Compared with `final-submission`,
the only additions are this `round4/` folder and
`.github/workflows/round4.yml`; `brand-ai-readiness-audit/`, `submission.zip`
and every other Round 3 file are untouched, which `check_engine_frozen.py`
proves byte for byte.
