# TE Literature Radar

[中文说明 / Chinese README](README.zh-CN.md)

TE Literature Radar is an open-source, Codex-assisted workflow for discovering, ranking, and summarizing high-quality thermoelectric literature. It searches Crossref, OpenAlex, arXiv, and optional RSS feeds; applies a hard thermoelectric relevance gate; asks Codex to judge novelty only from supplied evidence; validates generated scientific numbers; and computes deterministic A/B/C grades.

## What it does

- Finds recent thermoelectric and Seebeck-related papers from multiple public metadata sources.
- Supports target journals, target authors, materials/topics, doping/transport, and ML/materials-discovery priorities.
- Deduplicates by DOI first, then title/author fallback.
- Supports recurring `auto`, recent-N-days `lookback`, and explicit `range` searches.
- Prioritizes strong peer-reviewed work while allowing unusually innovative lower-tier work.
- Includes preprints only under stricter thresholds and labels them `Preprint — not peer reviewed`.
- Produces structured A/B/C digests with purpose, innovation, approach, results, mechanism, significance, limitations, and a radar note.

## How it works

```text
Crossref + OpenAlex + arXiv + RSS
              ↓
     normalize + deduplicate
              ↓
      TE relevance hard gate
              ↓
deterministic relevance/quality/fit/recency scores
              ↓
Codex novelty + scientific summary from supplied evidence
              ↓
        validation layer
              ↓
deterministic final A/B/C grade
              ↓
 Markdown / JSON / optional HTML email
```

## Trust and evidence rules

- Journal prestige cannot override a failed TE relevance gate.
- Codex does not directly assign the final total or A/B/C grade.
- Generated numerical scientific claims must already appear in the supplied title/abstract/metadata evidence; unsupported numbers fail validation.
- Title/abstract/metadata analysis is never presented as full-text review.
- State advances only after the required final output succeeds, and after email delivery when email is enabled.

## Requirements

- Python 3.11 or newer.
- Internet access for real Crossref/OpenAlex/arXiv/RSS searches.
- No third-party Python package is required in V1.
- No paid literature API is required for the default discovery sources.
- Codex is used for the novelty/scientific-summary stage of the full workflow; deterministic fetch/scoring is ordinary Python.

## 5-minute Quick Start

```bash
git clone https://github.com/953836942-dot/TE-literature-update.git
cd TE-literature-update
cp config.example.json config.json
python3 scripts/radar_cli.py fetch --config config.json --mode lookback --lookback-days 7
```

The last command performs deterministic discovery, normalization, deduplication, relevance gating, and base scoring. It outputs a fetch JSON containing `analysis_candidates`. It does **not** pretend to complete the Codex novelty/scientific-summary step by itself.

`config.json` is ignored by git, so you can customize it locally.

## Use with Codex

This repository includes `SKILL.md` and `agents/openai.yaml` for the repository workflow. Open/clone this repository in Codex and use the `te-literature-radar` repository Skill (commonly referenced as `$te-literature-radar`) with your local `config.json`.

The full workflow is:

```text
repository Skill
→ deterministic fetch
→ Codex novelty/summary JSON from supplied evidence
→ validate-analysis
→ deterministic A/B/C finalization
→ Markdown/JSON and optional email
```

The Skill intentionally does not hard-code a schedule. Scheduling can be added later with Codex Automation, cron, or another scheduler.

## Search time windows

Recurring, state-aware search:

```bash
python3 scripts/radar_cli.py fetch --config config.json --mode auto
```

Recent 30 days without moving the recurring cursor by default:

```bash
python3 scripts/radar_cli.py fetch --config config.json --mode lookback --lookback-days 30
```

Explicit historical interval:

```bash
python3 scripts/radar_cli.py fetch --config config.json --mode range --start-date 2026-01-01 --end-date 2026-06-30
```

`auto` uses the previous successful recurring run and overlaps 48 hours by default to reduce misses from delayed indexing. Manual `lookback` and `range` runs do not advance recurring state unless `--advance-auto-state` is explicitly requested.

## Configuration

Copy `config.example.json` to `config.json`, then edit the fields you need. Common changes are:

- `research_profile.core` — broad TE/Seebeck concepts.
- `research_profile.transport` — zT, power factor, Seebeck coefficient, thermal/electrical transport.
- `research_profile.design` — doping, alloying, band/defect/phonon engineering.
- `research_profile.data_driven` — ML/AI/materials discovery.
- `research_profile.priority_topics` and `watched_materials` — your own priorities.
- `target_journals` — verified journal names/ISSNs and quality tiers.
- `target_authors` — optional researcher watch list.
- `openalex.queries`, `arxiv.queries`, and `rss_feeds` — discovery coverage.
- `language` — output-language preference for the analysis workflow.

The score weights are intentionally fixed at:

```text
TE relevance 30
Research quality 30
Novelty 20
Research fit 10
Recency 10
```

## Optional email delivery

Email is disabled by default. If enabled, keep the SMTP password only in:

1. the configured environment variable, or
2. the local ignored `.secrets/` file.

Do not put passwords into `config.json`, source files, or Git commits.

## Outputs

Default output root: `te-literature-radar-output/`.

- `data/fetch-*.json` — normalized candidates and deterministic base scores.
- `final/YYYY-MM-DD.json` — validated analysis plus final scores/grades.
- `YYYY-MM-DD.md` — human-readable A/B/C digest.
- `state.json` — successful recurring seen IDs and last-success timestamp.

The output directory is git-ignored.

## Synthetic example output

See `example-output/sample-digest.md` and `example-output/sample-final.json`. These files are **synthetic demonstrations**: the paper titles, identifiers, and scientific claims are fictional and are included only to show the format.

## Tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts
```

All source-adapter tests mock network access; the unit test suite does not require live Crossref/OpenAlex/arXiv/RSS calls.

## Privacy and credential safety

The repository ignores:

```text
config.json
te-literature-radar.config.json
.secrets/
.env
.env.*
te-literature-radar-output/
```

`config.example.json` contains no personal email address, password, API secret, or private endpoint, and email delivery is disabled by default.

## Known limitations

- V1 uses title/abstract/metadata evidence rather than automatic paywalled full-text retrieval.
- Metadata providers can have indexing delays or incomplete abstracts.
- Novelty judgment is a Codex scientific assessment constrained by the supplied evidence; it is not a citation-count or peer-review substitute.
- Journal quality tiers are practical prioritization rules, not a universal measure of scientific merit.
- Author-name matching can be ambiguous when a stable author identifier is unavailable.
- One-click Codex installation, GUI, Zotero integration, database/vector storage, and scheduled GitHub Actions are intentionally outside this source-code edition.

## License and attribution

This project is released under the MIT License. See [LICENSE](LICENSE).

The literature-radar architecture was inspired by and partially adapted from `lishn6/daily-econ-literature-radar` under the MIT License. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for attribution. The upstream author does not endorse this TE-specific project merely by being credited here.
