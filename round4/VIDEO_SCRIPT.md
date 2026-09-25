# Video script — IT_Professionals, Round 4

Hard cap **5:00**: **Part 1 ≤ 3:00** (methodology), **Part 2 ≤ 2:00** (live run).
The narration below is written to fit: Part 1 is about 380 spoken words (about 2:35 at
a normal pace), Part 2 about 220 (the rest of its two minutes is the agent
working on screen). Rehearse both against a stopwatch.

**How to read this script.** Quoted blocks are what you say. The *On screen*
line under each beat is what must be visible **while** you say it: the
handout gives no credit for "narration that cannot be traced to the submitted
code". Paths are relative to the marketplace root, which is the top level of
the Round 3 `submission.zip` (SHA-256 `1c872c59…8dcf`). Line numbers refer to
that unchanged package. Open the files from the unzipped folder you record
from, not from a working copy.

---

## Part 1 — How we built it (≤ 3:00)

### 0:00–0:12 · What it is

> We're team IT_Professionals. Our Round 3 marketplace takes any URL and
> reports why AI assistants don't find or cite a brand, and why visitors leave.
> Nine skills, one entrypoint: ai-readiness-orchestrator, declared here.

*On screen:* `marketplace.json` lines 7–12, the `"entrypoint": true` entry.

### 0:12–1:15 · How we discovered the findings

> Our signals start from one sentence in the Round-2 appendix: a crawler must
> be let in, read the page, then pick out the fact — in that order. So every
> check belongs to a stage: reach, read, extract, trust, act.
>
> Field research changed what we check. Training crawlers and answer-time
> retrieval crawlers are separate pipelines, so ai-bots.json classifies
> twenty-nine crawlers, and check_robots.py reports a blocked retrieval crawler
> as critical, a training crawler as info, a contested one as medium.
>
> Then we audited five live sites: 365 findings. We named twelve false
> positives before touching a threshold; each is now a regression test, R1 to
> R12. That run also exposed a shell detector that never fired, so it now keys
> on the noscript "enable JavaScript" notice. And no check hardcodes a number:
> thresholds come from a profile per site archetype.

*On screen, in this order:*

1. `skills/ai-readiness-orchestrator/references/gate-rules.md` lines 10–14 — the appendix quote
2. `skills/crawl-access-audit/references/ai-bots.json` lines 24–40 — the three categories
3. `skills/crawl-access-audit/scripts/check_robots.py` line 286 (retrieval → `critical`), line 318 (training → `info`), line 351 (contested → `medium`)
4. `DESIGN.md` lines 374–380 — 365 findings, twelve false positives, 205 after
5. `tests/test_regressions.py` — scroll the `# R1.` … `# R12.` headers (lines 50–504)
6. `skills/site-evidence-collector/scripts/dom.py` lines 53–59 and 249–260 — the noscript signal
7. `skills/site-profile-classifier/references/threshold-profiles.json` lines 1–5, then the `archetypes` block (line 41 on)

### 1:15–2:05 · How we assigned severities

> Severity is what a finding costs if it's true: critical, the machine can't
> see the page; high, a specific capability is lost; info, a choice, not a
> defect. Confidence — confirmed, likely, hypothesis — is a separate field:
> how bad and how sure are different questions. Each check declares its
> default in a CHECKS registry.
>
> Then the gate cascade: a critical, or two highs in one stage, closes that
> gate. Downstream discoverability findings stay, capped at medium and tagged
> blocked_by the root cause — one cause first, not fifteen criticals.
> Engagement is never capped by crawler access; but where we never saw what a
> visitor sees, an empty JavaScript shell, those checks are suppressed, not
> guessed.

*On screen, in this order:*

1. `skills/ai-readiness-orchestrator/references/severity-model.md` lines 5–15, then 17–23 (confidence)
2. `skills/crawl-access-audit/scripts/check_robots.py` lines 24–37 — a `CHECKS` registry with `default_severity`
3. `skills/ai-readiness-orchestrator/scripts/gate_model.py` lines 81–114 (`build_gate_state`, Rule 1), then 117–147 (`apply_cascade`: line 128 Rule 0, line 137 the cap to `medium`, line 138 `blocked_by`)
4. `skills/engagement-audit/scripts/gating.py` lines 31–47 — `RULE_0B_SUPPRESSIBLE`

### 2:05–2:50 · How we derived and prioritised the fixes

> Every fix goes through one action contract: summary, mechanism — why it
> works — source, a paste-ready patch, and a command to verify it.
> validate_finding refuses any finding without a mechanism. Patches reuse
> values observed on the page; a missing value becomes FILL_IN, never an
> invented one.
>
> Priority is ICE, in severity.py: impact from post-cascade severity,
> confidence as nine, six or three, ease from effort. The sort is severity,
> ICE, stage, check id — a total order, so the same evidence always ranks the
> same.

*On screen, in this order:*

1. `skills/answerability-audit/scripts/bundle.py` lines 175–190 — `action()` (the same file is in every audit skill)
2. `skills/ai-readiness-orchestrator/scripts/orchestrate.py` lines 242–254 — `validate_finding`
3. `skills/structured-data-audit/scripts/extract_markup.py` lines 203–225 — `_starter_patch`, "Never invented"
4. `skills/ai-readiness-orchestrator/scripts/severity.py` lines 27–29, 48–53, 68–81

### 2:50–3:00 · Hand-off

> Seventy-three validator checks and six golden reports hold all of this in
> place. Now, live.

*On screen:* `tests/validate_marketplace.py` output (`73 passed`), or cut straight to the terminal.

---

## Part 2 — The live run (≤ 2:00)

One real, continuous run that follows `REPLAY_IT_Professionals.txt` exactly.
You may trim **idle waiting only** (the engine crawling, the agent thinking).
Never cut between typing the URL and the findings appearing, and never splice
two takes. The URL must be one of `TEST_SITE_URLS`.

Before you press record: the terminal is in the folder that holds
`submission.zip` (nothing else in it), font large, window about 140 columns so
the agent's table does not wrap. Everything below happens on camera.

### 0:00–0:12 · The package and the harness

Type:

```
sha256sum submission.zip          # macOS: shasum -a 256 submission.zip
claude --version
```

> This is our Round 3 submission.zip, unchanged — that's its SHA-256. The
> harness is Claude Code 2.1.282, and the model is Claude Opus 5.5.

### 0:12–0:22 · Step 1 of the manifest

Paste the four step-1 lines from the REPLAY file (unzip, `cd`, the
`.claude/skills` copy, `claude --model claude-opus-5-5 --allowedTools …`).
If Claude Code asks whether to trust the folder, answer yes. Type `/status` so
the version and model are on screen (or point at the model in the welcome
banner), then `Esc`.

> Claude Code only discovers skills under .claude/skills, so that's an unchanged
> copy; the agent runs the scripts in skills/.

### 0:22–0:32 · The URL, entered on camera

Show step 2 of the manifest for two seconds (a long paste appears as
`[Pasted text #1]`, so this is how the viewer sees the prompt), paste it, then
**type** `https://www.theguardian.com/` after it and press Enter.

> The Guardian — not one of our fixtures, and the engine is frozen, so nothing
> was tuned for it.

### 0:32–0:50 · The agent invokes the entrypoint (trim the waits)

Keep on screen: `Skill(ai-readiness-orchestrator)`, then the Bash call
`python skills/ai-readiness-orchestrator/scripts/orchestrate.py https://www.theguardian.com/ --out ./audit-output --no-render`,
then the JSON summary it prints.

> One line on wiring: the agent loaded our entrypoint skill and is running
> orchestrate.py from the submitted package — nothing precomputed; every
> finding comes from what the site serves right now.

### 0:50–1:10 · Status, cascade, priority order

Scroll to parts (1)–(3) of the agent's reply.

> One critical, and the gate cascade capped thirty-seven findings behind it.
> What it couldn't assess — we ran without a browser — is listed, not passed.
> This table is the engine's priority order: severity, then ICE, from sort_key
> in severity.py.

(Read the numbers off the screen; on 2026-09-25 they were 46 findings: 1
critical, 1 high, 37 capped behind F-001.)

### 1:10–1:48 · Drill-down on F-001

Scroll to part (4): evidence, script, severity reason, fix, patch, live check.

(Say what the agent actually printed in its live check. In the rehearsal of a
robots.txt drill-down it fetched the file and matched every cited line number,
which is what the lines below assume.)

> F-001, critical and confirmed: robots.txt line 102, Disallow slash, blocks
> six AI retrieval crawlers — PerplexityBot, Claude-SearchBot and four more —
> from check_robots.py. Critical, because a refused retrieval crawler can't
> cite the site at all; the training-only crawlers are reported separately, as
> info — a licensing choice. The fix is this paste-ready robots.txt block, and
> the agent just fetched the live file: line 102 is exactly there. Supported.

### 1:48–2:00 · Close

> Everything is in audit-output/audit-report.json — the path in our REPLAY
> file. Recommend-only: nothing was written to the site.

---

## If the run surprises you

- **F-001 is missing** (the Guardian changed its robots.txt): stop, and do not
  edit the take. Re-check with `python3 round4/tools/verify_replay.py
  round4/REPLAY_IT_Professionals.txt`, then pick a new video URL, update
  `TEST_SITE_URLS` and the "what the video's run finds" comment in the
  manifest, and re-record. The manifest must match the video.
- **The agent asks for permission** to run a command: approve it on camera.
  That is real interaction, not an edit.
- **The run is slow:** trim the waiting in the edit. Never trim the moment the
  URL is typed or the moment the findings appear.
- **Anything else goes wrong mid-take:** discard the whole take and record
  again. A second continuous take is fine; a spliced one is not.

## Checklist before upload

- [ ] Part 1 ≤ 3:00, Part 2 ≤ 2:00, total ≤ 5:00 (timed, not estimated)
- [ ] Harness **and** model said out loud and visible (`claude --version`, `/status`)
- [ ] The URL typed on camera is in `TEST_SITE_URLS`
- [ ] Every Part 1 claim had its file on screen while it was said
- [ ] From URL to findings is one continuous run; only idle time trimmed
- [ ] `REPLAY_IT_Professionals.txt` uploaded unchanged alongside the video
