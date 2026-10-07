# Review prompt: combined INDX + Gen 2 guide

Use this prompt for an independent review of the generated `index.html` at the root of this repo. It's written for a subagent or a fresh Claude session that has no context from the session that built the guide. Paste everything below the line as the task.

---

You are reviewing a compiled assembly guide for correctness. **Do not edit any files.** Report findings only. Don't read the builder's code or config in `guide-builder/`; derive everything from Prusa's sources so your review is independent.

## What was built

`C:\misc\prusa\combined-guide\index.html` (images are in `img/` next to it) merges three official Prusa sources into a single document in assembly order:

1. **The INDX conversion guide.** "Prusa INDX Conversion kit for the Prusa CORE One/+", 6 chapters. A PDF export may be at `C:\misc\prusa\prusa-indx-conversion-kit-for-the-prusa-core-one_2432_en_*.pdf` (outside the repo). If it isn't there, skip the PDF comparison and say so.
2. **The Gen 2 upgrade guide.** "Prusa CORE One+ to (Gen 2) upgrade". Only some of its steps are used.
3. **The companion article** "Assemblling the Prusa INDX Core one with the Gen 2 upgrade". It says when to switch between the two guides and adds a few steps of its own.
   https://help.prusa3d.com/article/assemblling-the-prusa-indx-core-one-with-the-gen-2-upgrade_1147602

The compiled page marks each step with a badge (`INDX c.n`, `GEN 2 c.n`, or `ARTICLE`) and gives each step an `id="s-<stepId>"` (article sections use `id="art-N"`). Yellow "Compiler's note" boxes and the "Read first" / "Roadmap" cards at the top were written by the compiler; they are not Prusa text. Comments under each step were filtered to the useful ones.

## Getting the source data

Fetch everything fresh. The site sits behind Cloudflare, but plain requests with a browser User-Agent work (`curl -A "Mozilla/5.0"`, or Python `urllib` with that header).

- Guide chapter as JSON: `https://help.prusa3d.com/edge/guide-bundle?locale=en&slug=<chapter-slug>`
  - `data.steps[]` gives each step's `id`, `title`, `lines[]` (`title` holds the HTML text; `meta.color`/`meta.icon`/`meta.level` give formatting), `media.gallery[]` and `comments` (the count).
  - `data.siblings[]` lists every chapter of the same guide with its slug and step list.
  - INDX chapter slugs: `1-introduction_1096223`, `2-printer-preparation-disassembly_1096231`, `3-z-axis-upgrade_1096239`, `4-indx-toolhead-side-filament-sensors_1096247`, `5-spoolholders-tool-dock-assembly_1096255`, `6-preflight-check_1096263`
  - Gen 2 chapter slugs: `1-introduction_1110653`, `2-printer-disassembly_1110664`, `3-belts-upgrade_1110672`, `4-heatbed-upgrade_1110680`, `5-preflight-check_1110689`
- Comments for a step or the article: `https://help.prusa3d.com/edge/comments?lng=en&page=1&parent=<stepId or 1147602>&per_page=100&status=approve` (threaded through `replies[]`; `role` other than `visitor` means Prusa staff; `info.total_pages` handles paging).
- Article: fetch the article URL above as HTML. The body starts at "If you received your Prusa CORE One INDX" and ends before "Was this article helpful". Sections are `<h3>`, and its links point to the exact guide steps (`/guide/<slug>#<stepId>`).
- PDF text: `pdftotext -layout <pdf> out.txt` (available in Git Bash). The table of contents is in the first ~330 lines.

## What to check

Derive the expected merge order **yourself from the article's wording**. Don't trust the compiled page's roadmap. Then check:

1. **Completeness and order**
   - Every INDX step from all 6 chapters appears exactly once, in the original order, except where the article inserts other material. Cross-check the titles and order against the PDF table of contents too, and report any steps that differ between the PDF and the web version.
   - The Gen 2 steps included are exactly the ranges the article sends you to ("switch to … step X … until you finish step Y"), in their original order, and no others. One known exception, which you should confirm is flagged as compiler-added: Gen 2 "Changing the printer edition" (preflight chapter), inserted after INDX "Setting up the printer: Intro".
   - No step is duplicated anywhere.
2. **Switch points.** At every article handoff, check that the step immediately before is the "until you finish step …" step and the step immediately after is the "continue from …" step. Watch for near-identical titles (for example Gen 2 "Guiding the upper belt (right motor)" vs "Guiding the upper belt (gantry - right)").
3. **Article content.** All article sections and their instructions and images are present, and none are lost or reordered. The article introduction is present.
4. **Step content fidelity.** Spot-check at least 25 steps spread across all chapters. Check that the text lines, warnings, notes and images match the live JSON, and that the number of images per step matches.
5. **Compiler's notes and top cards.** Every claim is supported by the official text or the comments, and anything that comes only from comments must say so. Look for wrong step numbers, wrong anchors and contradictions with Prusa's instructions. Check each roadmap row's range and link.
6. **Comment filtering.** Sample about 15 steps that have many comments. Did any comment get dropped that has a practical tip, a correction to the instructions, or a warning? Is every Prusa staff comment kept? Are comments attached to the right step?
7. **Links.** Internal `#s-…`/`#art-…` links resolve. Links in step text that pointed to steps now inside the document should be internal anchors.
8. **Proofreading.** Check spelling, grammar and clarity of all compiler-written text: the header, the roadmap, the "Read first" card, the compiler's notes and phase titles.

## Report format

Give a short verdict first (ready to use / needs fixes), then findings ranked by severity:

- **Severity**: blocker (wrong or missing assembly step, wrong order, wrong instruction), major, minor, nit
- **Location**: the step badge and `id`, or the section of the page
- **What's wrong**, with evidence (quote the source and the compiled text)
- **Suggested fix**

Then list what you checked and found correct, so it's clear what was covered. Say explicitly if any check couldn't be completed (e.g. a fetch failed).
