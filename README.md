# Prusa CORE One INDX + Gen 2: combined assembly guide

**→ Open the guide: https://patchesthefirst.github.io/prusa-gen2-indx-guide/**

Upgrading a Prusa CORE One/+ with both the INDX conversion kit and the CORE One+ Gen 2 upgrade means switching between three official sources:

- the [INDX conversion guide](https://help.prusa3d.com/guide/1-introduction_1096223);
- the [CORE One+ Gen 2 upgrade guide](https://help.prusa3d.com/guide/1-introduction_1110653);
- the [companion article](https://help.prusa3d.com/article/assemblling-the-prusa-indx-core-one-with-the-gen-2-upgrade_1147602) that tells you when to switch.

This page merges them into one guide in assembly order.

> **Unofficial.** This is a community-made compilation. It isn't affiliated with or endorsed by Prusa Research. The step text, article text and photos are Prusa's, copied from help.prusa3d.com. If Prusa would like it taken down, please open an issue.

## What's in it

- **Every step, in order:** all INDX steps, the Gen 2 steps the companion article sends you to, and the article's own sections. Prusa's text and photos are copied as-is, and every step links to its original page.
- **Filtered community comments:** under each step, the useful comments (tips, problems with fixes, corrections). Prusa staff replies are always shown.
- **Compiler's notes:** yellow boxes where the official docs are unclear for the combined path, for example which steps to skip and what stays loose until later. They aren't Prusa's text, and anything that comes only from comments says so.
- **Built for working at the printer:** progress checkboxes (saved in your browser), a step filter, dark mode and print styles. It also works on phones.

## How it's kept up to date

Python scripts in [`guide-builder/`](guide-builder/) download the guides, the article and the comments from Prusa's help site, and build the page. Another script checks that every step is present, in the right order, and that every switch point matches the article.

Every Monday, a GitHub Action fetches a fresh copy and opens a pull request if anything changed. The maintainer reviews Prusa's edits against the compiler's notes and triages new comments before merging. Nothing goes live without that review. The date at the top of the guide shows when it was last fetched.

The page and its tooling were built with the help of AI (Claude). The merge order, notes and comment selection were reviewed by hand, and an independent AI review cross-checked the merge order against Prusa's article.

## Found a problem?

Please [open an issue](https://github.com/PatchesTheFirst/prusa-gen2-indx-guide/issues). It helps to include:

- the step badge, for example **INDX 5.36** or **GEN 2 3.9**, or a link to the step (each step has its own `#s-…` anchor);
- what's wrong, or the tip you think should be included;
- for a comment that should be shown, a link to it on help.prusa3d.com.

Pull requests are welcome too. Don't edit `index.html` directly: it's generated. Changes go into the builder's inputs, as described in [`guide-builder/README.md`](guide-builder/README.md), which also explains the editorial rules (Prusa's text is never edited, and notes must be backed by Prusa's text or by comments).

## Repository layout

| Path | Contents |
|---|---|
| `index.html`, `img/` | The published guide (served by GitHub Pages) |
| `guide-builder/` | Scripts, configuration, compiler's notes, comment lists and the data snapshot |
| `.github/workflows/weekly-update.yml` | The weekly update check |
| `.claude/skills/` | Maintenance instructions for Claude Code (update, review, auto-update PR review) |
