# Combined INDX + Gen 2 guide builder

This folder generates the repo's `index.html` (with photos in `img/`): one offline guide that merges three Prusa sources in assembly order.

- **INDX conversion guide:** "Prusa INDX Conversion kit for the Prusa CORE One/+", all 6 chapters.
- **Gen 2 upgrade guide:** "Prusa CORE One+ to (Gen 2) upgrade". Only the steps the companion article sends you to are used.
- **Companion article:** "Assemblling the Prusa INDX Core one with the Gen 2 upgrade". It says when to switch guides and has a few steps of its own.

Each step keeps its text, annotated photos, and a filtered set of community comments.

Requirements: Python 3.10+ (standard library only). Run all commands from this folder.

## Commands

| Command | What it does |
|---|---|
| `python fetch.py` | Downloads a fresh snapshot into `data/`, keeps the previous one in `data.prev/`, and writes `CHANGES.md` (what changed, plus every new comment). Takes 1–2 minutes. `--report-only` skips the download and only writes `CHANGES.md`, comparing the existing `data.prev/` with `data/`. |
| `python build.py` | Builds `../index.html` and downloads any missing images into `../img/`. `--noimg` skips the downloads. `--prune` deletes images the page no longer uses. |
| `python verify.py` | Runs deterministic checks on the config, the data and the built page. Exits with code 1 if any check fails. |

Run `build.py` before `verify.py`, because one of the checks is that the page matches the configured sequence.

## Weekly automatic check

`.github/workflows/weekly-update.yml` runs every Monday, and can also be started from the Actions tab. It runs `fetch.py`, `build.py --prune` and `verify.py`. If anything changed, it pushes the result to the `auto-update` branch and opens or updates a pull request whose description is the change report. It never commits to `main` and never edits notes or comment lists, so nothing is published until someone reviews and merges the PR. The `review-auto-update` skill does that review.

While that PR is open with review commits on it, the next run stops instead of overwriting them. The repository setting "Allow GitHub Actions to create and approve pull requests" (Settings → Actions → General) must be on.

## Previewing

To preview the page in the Claude desktop app, the repo's `.claude/launch.json` defines a `combined-guide` server on port 8765. Opening `index.html` directly in a browser also works.

## Files

| File | Contents |
|---|---|
| `config.py` | Sources, the merge order (`SEQUENCE`), phase and roadmap grouping, article section anchors, `LINK_REMAP` (fixes for Prusa links that point to the wrong guide edition), and `ARTICLE_COMMENTS` (useful article comments → section). |
| `notes.py` | Compiler's notes (yellow boxes), keyed by step id. |
| `comments_keep.txt` | Curated step comments to show. The first token on each line is the comment id; the rest is a human-readable reminder. Prusa staff comments are always shown. |
| `comments_seen.txt` | Every comment id already reviewed, whether kept or rejected. `fetch.py` lists anything not in here as new. |
| `template.html` | Page shell: CSS, the header cards and JS (progress checkboxes, contents filter, lightbox, dark mode, print). |
| `common.py` | Shared helpers: data access, sequence resolution, step labels, references. |
| `data/` | The snapshot the page is built from: guide JSON, comment threads, article body, article comments, `meta.json`. |

## How the merge order works

`SEQUENCE` in `config.py` is a list of these items:

- `Phase(title)`: starts a heading and a contents group.
- `Row(description)`: starts a roadmap row. The step-range label is computed.
- `Steps(guide, chapter, first_id, last_id)`: an inclusive range of steps.
- `Article(h3_id)`: one article section.

Ranges use Prusa's **step ids**, which don't change when steps are inserted or renumbered. A step Prusa adds inside a range is picked up automatically. All displayed numbers ("INDX 3.17") are computed from the live data.

**Article anchors (`art-1` … `art-8`) and step anchors (`s-<id>`) are also the keys for readers' progress checkboxes, which are stored in their browser.** Never renumber them. A new article section gets a new anchor (`art-9`, …).

## References in notes, roadmap rows and the template

| Syntax | Renders as |
|---|---|
| `{s:1111025}` | A linked label such as "Gen 2 4.19" |
| `{s:1110993..1111043}` | A linked range such as "Gen 2 4.11–4.20" |
| `{a:fixing-the-heatbed}` | The linked title of that article section |

Write step numbers this way, not by hand, so they stay correct when Prusa renumbers. The build fails on any reference it can't resolve.

## Editorial rules

- **Step and article text is copied verbatim.** Never edit it. Anything added goes in a compiler's note, the "Read first" card or the roadmap.
- **Notes must be supported** by Prusa's text or by comments. If a claim comes only from comments, say so ("from comments").
- **Which comments to keep:**
  - Keep: practical tips, problems with their fixes, corrections to the instructions, where to find parts, warnings, and answers to real ambiguities.
  - Drop: "+1/same/thanks" replies, jokes, complaints with nothing actionable, duplicates of a kept tip, and outdated remarks about things since fixed.
  - Prusa staff comments are always shown.
- **The project skills** handle the routine work: `/update-guide` refreshes the guide from Prusa, `/review-auto-update` finishes the weekly workflow's PR, and `/review-guide` runs an independent review. They're in `../.claude/skills/`. The reviewer's brief is `review-prompt.md`.
