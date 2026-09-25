# Recording runbook — Round 4

Everything needed to record the video and submit, in order. Budget about 45
minutes the first time: 15 to set up, 10 for the pre-flight checks, the rest
for takes. The narration and shot list are in [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md).

What you submit: **the video** (≤ 5:00) and **`REPLAY_IT_Professionals.txt`**
(this folder, uploaded unchanged). The Round 3 package is not resubmitted.

---

## 1. Set up the recording machine (once)

| Need | Command | Check |
|---|---|---|
| Python 3.9+ | already installed on most machines | `python3 --version` (Windows: `python --version`) |
| Node.js 18+ | nodejs.org installer | `node --version` |
| Claude Code, **exactly 2.1.282** | `npm install -g @anthropic-ai/claude-code@2.1.282` | `claude --version` → `2.1.282 (Claude Code)` |
| Sign in | `claude` once, follow the login, then `/exit` | |
| Keep the version pinned while recording | set `DISABLE_AUTOUPDATER=1` in the shell you record from (PowerShell: `$env:DISABLE_AUTOUPDATER = "1"`) | `claude --version` still 2.1.282 |

The manifest discloses **Claude Code v2.1.282** and **Claude Opus 5.5
(`claude-opus-5-5`)**. The video must show exactly those. If you record with a
different version or model, change `AGENT_HARNESS`, `LLM_MODEL`, the
`npm install …@version` in `ENV_SETUP` and the `--model` flag in `TEST_STEPS`
together, then re-run the check in §2c. A mismatch between video and manifest
is an integrity failure, not a deduction.

## 2. Pre-flight (run on the recording machine, same day)

From the root of this repository (`sub_final` branch):

**a. The engine is the submitted one.**

```bash
python3 round4/tools/check_engine_frozen.py
```

Expect `FROZEN: what you demo is exactly what was submitted in Round 3.`
If you have a copy of the zip you actually uploaded in Round 3, compare it too:
`python3 round4/tools/check_engine_frozen.py --zip /path/to/uploaded.zip`.

**b. The manifest parses and replays on this machine** (runs the engine, no
agent, about two minutes, both URLs twice):

```bash
python3 round4/tools/verify_replay.py round4/REPLAY_IT_Professionals.txt --twice
```

Expect `OK: all … checks passed`, and on the Guardian
`F-001 critical/confirmed ICE 9.3 reach.robots.ai_search_bot_blocked` citing
line 102. If F-001 is gone, the Guardian changed its robots.txt: see
"If the run surprises you" in `VIDEO_SCRIPT.md` before recording anything.

**c. The agent steps work on this machine** (one agent session, about a
minute; uses example.com so the video's URL stays fresh for the take):

```bash
python3 round4/tools/rehearse_agent.py https://example.com/
```

Expect three `[PASS]` lines: the entrypoint loaded with the Skill tool, the
exact engine command ran, the report landed at `EXPECTED_OUTPUT`.

## 3. Prepare the take

1. Make an **empty** folder, e.g. `~/round4-take`, and copy `submission.zip`
   into it. Nothing else goes in it. This is where Part 2 is recorded.
2. Terminal: font 18 pt or larger, window about 140 columns wide, dark theme,
   notifications off. Clear the scrollback.
3. Screen recorder at 1920×1080 (OBS, QuickTime or the Windows Game Bar).
   Test the microphone once.
4. For Part 1, unzip a second copy you can browse in an editor, and open the
   files at the lines in `VIDEO_SCRIPT.md` in order. With VS Code:

   ```bash
   mkdir -p ~/round4-browse && cd ~/round4-browse && python3 -m zipfile -e /path/to/submission.zip .
   code -g marketplace.json:7
   code -g skills/ai-readiness-orchestrator/references/gate-rules.md:10
   code -g skills/crawl-access-audit/references/ai-bots.json:24
   code -g skills/crawl-access-audit/scripts/check_robots.py:271
   code -g DESIGN.md:367
   code -g tests/test_regressions.py:50
   code -g skills/site-evidence-collector/scripts/dom.py:53
   code -g skills/site-profile-classifier/references/threshold-profiles.json:1
   code -g skills/ai-readiness-orchestrator/references/severity-model.md:5
   code -g skills/ai-readiness-orchestrator/scripts/gate_model.py:81
   code -g skills/engagement-audit/scripts/gating.py:31
   code -g skills/answerability-audit/scripts/bundle.py:175
   code -g skills/ai-readiness-orchestrator/scripts/orchestrate.py:242
   code -g skills/structured-data-audit/scripts/extract_markup.py:203
   code -g skills/ai-readiness-orchestrator/scripts/severity.py:27
   ```

   Those are the same files, byte for byte, as the zip the judges hold, so
   every line number in the script matches what they will find.

## 4. Record

- **Part 1**: editor on screen, narrate from `VIDEO_SCRIPT.md`, switching files
  as each beat says. Several takes are fine; keep the best. ≤ 3:00.
- **Part 2**: terminal in `~/round4-take`, one continuous take following the
  shot list. Type the URL on camera. Say the harness and the model out loud.
  ≤ 2:00 after trimming idle time.

The four step-1 lines, for pasting (macOS / Linux):

```bash
python3 -m zipfile -e submission.zip brand-ai-readiness-audit
cd brand-ai-readiness-audit
python3 -c "import shutil; shutil.copytree('skills', '.claude/skills')"
claude --model claude-opus-5-5 --allowedTools "Skill" "Bash(python:*)" "Bash(python3:*)" "Read" "Grep" "Glob"
```

On Windows use `python` instead of `python3` and
`Get-FileHash submission.zip -Algorithm SHA256` (PowerShell) or
`certutil -hashfile submission.zip SHA256` (cmd) for the hash. The step-2
prompt is in the manifest; copy it from there so it is word for word.

## 5. Edit

- Allowed: cutting dead time while the engine crawls or the agent thinks;
  titles "Part 1 — Methodology" and "Part 2 — Trial run"; zooming in on text.
- Not allowed: any cut between the typed URL and the findings that is not
  idle time; joining two takes of the live run; re-ordering the run; any
  overlay that shows findings the run did not produce.
- Check the lengths: Part 1 ≤ 3:00, Part 2 ≤ 2:00, total ≤ 5:00.

## 6. Submit

- [ ] Video, ≤ 5:00, Part 1 ≤ 3:00, Part 2 ≤ 2:00
- [ ] `REPLAY_IT_Professionals.txt`, exactly this file, name unchanged
- [ ] The URL in the video is in `TEST_SITE_URLS`; the harness and model said
      and shown in the video are the ones in `AGENT_HARNESS` and `LLM_MODEL`
- [ ] `check_engine_frozen.py` and `verify_replay.py` both passed on the day
