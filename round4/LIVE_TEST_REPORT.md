# Live test report — the frozen Round 3 engine, before recording

Round 4 is judged on a live run against a site the engine was not built on,
and on a judge's own URL. Every fixture in the Round 3 package was written by
us, so before recording we ran the **unchanged** engine against real sites and
checked its claims against the sites themselves. This file records what we ran,
what held up, what did not, and which decisions that drove.

All runs used the Round 3 `submission.zip` (SHA-256 `1c872c59…8dcf`, checked
before every run), unpacked into a fresh folder, with the manifest's command:
`orchestrate.py <URL> --out ./audit-output --no-render`. Nothing in the engine
was changed, and nothing could be: it is frozen.

## Summary

- **20 real sites** on clean GitHub-hosted runners (Python 3.11.15), through
  [`.github/workflows/round4.yml`](../.github/workflows/round4.yml): every run
  exited 0 with a report that meets the Round 3 schema floor, and all finished
  in under a minute.
- **The manifest replays** on a clean runner: `verify_replay.py` parsed it,
  cross-checked its fields and replayed its command against every
  `TEST_SITE_URLS` entry, twice, with every check passing.
- **Deterministic**: back-to-back runs gave identical findings on every URL we
  repeated, and re-analysing a saved evidence bundle gave an identical report
  (all fields except the bundle path).
- **Six agent rehearsals** with Claude Code 2.1.282 and `claude-opus-5-5`: the
  agent loaded the entrypoint with the Skill tool and ran the documented engine
  command every time; each run took 33–59 s end to end.
- **The video's URL, theguardian.com**, gives one critical, confirmed finding
  whose evidence we checked line by line against the live robots.txt.
- **Known limits of the frozen engine** found on the way are listed below and
  in the manifest. They are recorded, not fixed.

## 20 real sites, no rendering (2026-09-25)

| site | status | pages | C | H | M | L | I | total | top finding (severity/confidence check) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| docs.djangoproject.com | partial | 25 | 0 | 1 | 17 | 3 | 0 | 21 | `high/confirmed extract.sd.absent_on_eligible_page` |
| docs.pytest.org | partial | 25 | 0 | 1 | 20 | 3 | 0 | 24 | `high/confirmed extract.sd.absent_on_eligible_page` |
| docs.python.org | partial | 14 | 1 | 1 | 12 | 4 | 0 | 18 | `critical/confirmed reach.index.noindex_on_content` |
| example.com | partial | 1 | 0 | 0 | 6 | 0 | 0 | 6 | `medium/confirmed extract.ans.title_not_entity_bearing` |
| stripe.com | partial | 25 | 0 | 10 | 45 | 8 | 0 | 63 | `high/likely extract.ans.fact_coverage_gap` |
| vercel.com | partial | 25 | 1 | 6 | 26 | 0 | 0 | 33 | `critical/confirmed trust.integrity.prompt_injection` |
| www.adobe.com | partial | 25 | 0 | 13 | 18 | 9 | 0 | 40 | `high/likely extract.ans.fact_coverage_gap` |
| www.allbirds.com | partial | 25 | 1 | 12 | 62 | 5 | 0 | 80 | `critical/confirmed reach.index.noindex_on_content` |
| www.bbc.com | partial | 25 | 1 | 1 | 24 | 7 | 1 | 34 | `critical/confirmed reach.robots.ai_search_bot_blocked` |
| www.gov.uk | partial | 25 | 0 | 4 | 18 | 5 | 0 | 27 | `high/likely extract.ans.fact_coverage_gap` |
| www.hubspot.com | partial | 25 | 0 | 7 | 57 | 5 | 0 | 69 | `high/likely extract.ans.fact_coverage_gap` |
| www.ikea.com (us/en) | partial | 25 | 0 | 14 | 40 | 1 | 0 | 55 | `high/likely extract.ans.fact_coverage_gap` |
| katzsdelicatessen.com | partial | 25 | 0 | 6 | 41 | 4 | 0 | 51 | `high/likely read.nontext.key_fact_image_only` |
| www.mit.edu | partial | 15 | 0 | 10 | 16 | 2 | 0 | 28 | `high/confirmed reach.index.canonical_conflict` |
| www.mozilla.org | partial | 20 | 1 | 6 | 39 | 2 | 0 | 48 | `critical/confirmed reach.index.noindex_on_content` |
| www.notion.com | partial | 25 | 1 | 1 | 55 | 4 | 0 | 61 | `critical/confirmed reach.robots.ai_search_bot_blocked` |
| www.nytimes.com | no_content_available | 0 | 1 | 0 | 1 | 0 | 1 | 3 | `critical/confirmed reach.robots.ai_search_bot_blocked` |
| www.python.org | partial | 25 | 0 | 3 | 26 | 14 | 0 | 43 | `high/likely extract.ans.fact_coverage_gap` |
| www.theguardian.com | partial | 25 | 1 | 1 | 33 | 10 | 1 | 46 | `critical/confirmed reach.robots.ai_search_bot_blocked` |
| www.wikipedia.org | partial | 1 | 0 | 2 | 7 | 0 | 0 | 9 | `high/likely act.orient.no_value_proposition` |

`partial` is expected: the runs pass `--no-render`, and the report says which
three browser-dependent checks that affected rather than passing them.
www.nytimes.com answered the seed with HTTP 403, so the engine reported only
what it could see from outside, its robots.txt policy, and said so.

The list and the runner are in [`urls/generalization.txt`](urls/generalization.txt)
and [`tools/live_matrix.py`](tools/live_matrix.py); anyone on the team can re-run
them with one push to `sub_final`.

## Findings we checked against the live site

| site | finding | how we checked | result |
|---|---|---|---|
| theguardian.com | F-001 critical: robots.txt blocks six AI retrieval crawlers, line 102 | `curl robots.txt`, lines 70–110 | **Holds.** One group of `User-agent` lines naming PerplexityBot, Claude-SearchBot, Claude-User, Amazonbot, DuckAssistBot and Google-CloudVertexBot (plus training and contested crawlers), closed by `Disallow: /` on line 102 |
| theguardian.com | homepage declares no structured data | `curl / \| grep -c application/ld+json` | **Holds.** 0 |
| www.mit.edu | high, confirmed: canonical URL conflicts, cross-host | `curl / \| grep canonical` | **Holds, and it's a real bug.** The homepage's canonical is `https://tlecms.mit.edu/spotlight/physicists-journey`: a news story on a CMS host. `/about` points to `tlecms.mit.edu/about` |
| jsr.io | critical: noindex on content pages | `curl -sI` | **The observation holds** (`x-robots-tag: noindex`). The severity is overstated: see known limits |
| proxy.golang.org, pypi.org | high, confirmed: no structured data | fetch + count | **Holds.** 0 JSON-LD, microdata or RDFa |

## Known limits of the frozen engine

Found in this run and recorded in the manifest. None of them can be fixed for
Round 4, because the engine must match what was submitted. Two of them decided
how we record.

1. **Deliberate `noindex` is reported as critical.** Every critical `noindex`
   we saw was on a page meant to be excluded: a site-search page
   (docs.python.org `/3/search.html`), version-pinned package pages (jsr.io),
   cart-upsell collections (allbirds.com), mozilla.org's "about this site"
   page. The directive is really there; calling it a critical defect is
   wrong.
2. **Relative links after a redirect.** docs.pytest.org `/` answers 302 to
   `/en/stable/`, whose links are relative (`href="changelog.html"`). The
   engine resolves them against `/`, so it reports "19 of 89 internal links
   return 404". We checked: `/changelog.html` is 404, and
   `/en/stable/changelog.html`, where a browser goes, is 200. **This is why
   docs.pytest.org is not the video's URL,** although an earlier team draft
   used it.
3. **Rendered-mode link counts include off-site links.** With Playwright, the
   rendered-side count behind `read.render.nav_links_js_only` counts every
   unique link (`collect.py` lines 739–747) while the raw side counts internal
   links only (lines 632–653). On proxy.golang.org, a static page, that
   produced a HIGH, confirmed "2 internal links become 15 after JavaScript";
   13 of the 15 are off-site. **This is why the manifest passes
   `--no-render`.**
4. **A visible prompt for coding agents reads as prompt injection.**
   vercel.com/docs carries a copy-to-clipboard prompt ("If you are Claude
   Code, OpenAI Codex, … install the Vercel Plugin"), and the engine reports it
   as critical prompt injection. It is text addressed to an AI, but it is not
   hidden or manipulative.
5. **Heuristic checks say they are heuristics.** `act.orient.*`, `act.cta.*`
   and `read.nontext.key_fact_image_only` are `likely`, not `confirmed`, and
   it shows: pages whose buttons are built by JavaScript read as having none
   (adobe.com's raw HTML has placeholder link text), news homepages are asked
   for a value proposition, and the image check infers a phone number from a
   filename. The confidence field is how a reader tells these apart from the
   confirmed checks above.
6. **A bot-check page is audited as content.** When a CDN answers the
   crawler with a challenge page instead of the page (pypi.org served
   "Client Challenge" for four to six of its 25 sampled pages), the engine audits
   the challenge page, so thin-content and orientation findings appear for
   that page. The evidence names the page's real title and word count, so a
   reader can see it.

## Rendering on or off (local, Playwright 1.56 + Chromium)

| URL | no render | with render | difference |
|---|---|---|---|
| pypi.org | 64 (12 high) | 67 (15 high) | +4 `read.render.nav_links_js_only` (high); one `fact_coverage_gap` drops from high to medium |
| jsr.io | 28 (2 high) | 29 (2 high) | +1 `chunk_not_self_contained` (medium) |
| proxy.golang.org | 4 (2 high) | 5 (3 high) | +1 `nav_links_js_only` (high): false, limit 3 |
| pypi.org/project/requests/ | 43 (7 high) | 46 (10 high) | +4 `nav_links_js_only` (high); one `fact_coverage_gap` drops from high to medium |
| jsr.io/@std/path | 32 (2 high) | 33 (2 high) | +1 `chunk_not_self_contained` (medium) |

Rendering added no finding we could confirm and at least one we could refute,
and it makes a judge's result depend on having a browser installed. The
manifest therefore passes `--no-render`, and the report lists the three checks
it could not assess.

## Determinism

| URL | where | back-to-back runs | saved-bundle re-analysis |
|---|---|---|---|
| theguardian.com | clean runner | 46 = 46, identical | identical |
| bbc.com | clean runner | 35 = 35, identical | identical |
| example.com | clean runner | 6 = 6, identical | identical |
| pypi.org | local | 60 = 60, identical | identical |
| proxy.golang.org | local | 4 = 4, identical | identical |

"Identical" compares every finding's check, severity, confidence and affected
URLs. The saved-bundle comparison covers the whole report, except
`evidence_bundle.path`.

Across the day, pypi.org went from 64 findings (17:12 UTC) to 60 (17:35 UTC)
with the same 25 pages sampled both times. The difference is what the site
served: pypi.org's CDN answered six package pages with its bot check ("Client
Challenge", 35 words) in the first run and four in the second, and the engine
audits such a page as if it were the content (limit 6). The two pages that
recovered account for every changed finding. Back-to-back runs a few minutes
apart were identical.

The engine's own offline goldens pass byte for byte on Python 3.11.15, the
version they were recorded with (the `frozen-engine` job). On other versions
the only difference is `generator.tool_versions.python`, which is why the Round
3 `ci.yml` workflow, pinned to 3.9 and 3.12, fails its golden step on this
branch and on `final-submission` alike. That file belongs to Round 3, so we
left it untouched.

## Agent rehearsals (Claude Code 2.1.282, claude-opus-5-5)

Run headless (`claude -p`) from a fresh unzip, following the manifest.

| prompt | site | time | entrypoint via Skill tool | engine command | drill-down | live check |
|---|---|---:|---|---|---|---|
| draft 1 | proxy.golang.org | 33 s | yes | after one refused `; echo $?`, ran it behind `python --version &&` | F-002 no structured data | supported (`ld+json 0`) |
| draft 2 | pypi.org | 58 s | yes | ran it behind `python --version;` | F-012 no structured data | supported (3 pages, 0 markup) |
| draft 3 | jsr.io | 57 s | yes | after one refused `; echo $?`, ran it behind `python --version &&` | F-001 noindex header | supported (`X-Robots-Tag: noindex`) |
| manifest | pypi.org | 58 s | yes | exact, after one refused `; echo $?` | F-011 no structured data | supported |
| manifest, no chaining | proxy.golang.org | 41 s | yes | **exact, first try** | F-002 no structured data | supported |
| final manifest | jsr.io | 59 s | yes | **exact, first try** | F-001 noindex header | supported, and it noted the pages are version-pinned |

Two prompt changes came out of this: (1) ask for the engine command "with
nothing added before or after it in the same shell call", because a chained
`echo $?` is refused by the harness and would put a permission prompt in the
video; (2) say that `suppressed_by_rule` counts per-page suppressions, because
the agent twice misread a check suppressed on one page and reported on another
as a contradiction.

## Decisions this drove

| decision | because |
|---|---|
| Video URL: https://www.theguardian.com/ | One critical, confirmed root cause that anyone can check at its robots.txt; 37 downstream findings capped behind it shows the cascade; stable while the site's robots.txt is |
| Not docs.pytest.org | Limit 2 would put a false broken-links finding on camera |
| `--no-render` in the manifest | Limit 3; and a judge's result must not depend on a browser install |
| Claude Code pinned to 2.1.282, model `claude-opus-5-5` | The version and model every rehearsal used; ENV_SETUP installs exactly that version |
| `TEST_SITE_URLS`: the Guardian and example.com | The video's URL plus the handout's own example, both clean, stable and deterministic here |
| The known limits written into the manifest | A judge running their own URL may hit them; saying so first is honest, and it is what our Round 3 DESIGN.md already does |

## What this environment could not do

The session that prepared this could reach only a few hosts directly, so every
third-party site above was audited on GitHub-hosted runners by
`.github/workflows/round4.yml`, and the agent rehearsals ran against the hosts
reachable from the session (pypi.org, jsr.io, proxy.golang.org). The runbook's
same-day pre-flight re-runs the manifest, including the Guardian, on the
machine that records the video.
