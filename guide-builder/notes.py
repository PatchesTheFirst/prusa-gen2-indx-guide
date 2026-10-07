"""Compiler's notes, shown in yellow boxes above a step. Keyed by Prusa step id.

These are additions written while merging the guides; they are not Prusa's text.
Anything taken only from user comments must say so.

Reference syntax (resolved at build time, so numbers stay right if Prusa renumbers):
  {s:1111025}            -> linked label of that step, e.g. "Gen 2 4.19"
  {s:1110993..1111043}   -> linked range label, e.g. "Gen 2 4.11–4.20"
  {a:fixing-the-heatbed} -> linked title of that article section
The same syntax works in template.html.
"""

NOTES = {
    # INDX 1.3 Before you begin
    1096375: "You don't need the companion article or the Gen 2 guide open: this document already follows the article's switching instructions. The original pages are linked from every step if you want to check them.",
    # INDX 1.11 Optional CORE One+ Gen 2 upgrade
    1149726: "Already handled: the companion article and the needed Gen 2 steps are merged into this document in the right order.",
    # INDX 3.17 Securing the offset sensor assembly
    1099523: "Gen 2 path: leave this M3x10 screw only a few turns in, as the step says. You tighten it in the article section {a:mounting-the-left-cover-covering-the-electronics}, after the expansion joints are aligned. You'll also have to move the sensor aside to align the front-right expansion joint ({s:1111025}).",
    # Gen 2 4.4 Removing old expansion joints
    1110931: "The Gen 2 guide says to keep one old expansion joint for the Gen 2 nozzle wiper. The Gen 2 nozzle-wiper steps are <b>not</b> part of the INDX path, since INDX fits its own nozzle cleaner in chapter 5. Keep the old joints anyway, like every other removed part.",
    # Gen 2 4.8 Inserting the heatbed spacer
    1110975: "This spacer sits loose for the next few sections. Commenters taped it in place, or used a screw or Allen key to keep it centered, until the heatbed goes back on in {s:1099880}.",
    # INDX 3.21 Heatbed cable covers: parts preparation
    1099715: "Gen 2 path (from comments; the official docs don't say this): you already placed the new <b>10 mm</b> heatbed spacer in {s:1110975}. Don't use the old 8 mm spacer listed here.",
    # INDX 3.25 Securing the heatbed
    1099926: "Gen 2 path: only two turns, as the step says. The heatbed screws get their final tightening with the aligner in {s:1110993..1111043}, later in this document.",
    # Gen 2 3.9 Installing the new pulley (right motor)
    1113142: "From comments: many people found the new pulleys very hard to push onto the motor shaft, here and on the left motor ({s:1113272}). Before you force one, loosen or remove both set screws, and file off any burr the old set screw left on the shaft. Some still needed pliers or a clamp. At least one commenter got a pulley stuck halfway and had to order a new motor, so go carefully if it won't slide on.",
    # Gen 2 3.16 Right motor screws: parts preparation
    1113217: "INDX path: the M3nS nut and M3x10 listed here are for the Bowden-guide, which INDX doesn't use (see the article section above and {s:1113247}).",
    # Gen 2 3.17 Tightening the right motor
    1113237: "INDX path (from comments): the Main-cable-clip part of this step doesn't apply, because the main cable was already removed in INDX chapter 2.",
    # Gen 2 3.18 Securing the Bowden-guide
    1113247: "<b>Skip this step on the INDX path.</b> The article says the Bowden-guide isn't needed for the INDX conversion and can be removed once it's detached from the motor mount.",
    # Gen 2 3.38 Guiding the upper belt (gantry - right)
    1113491: "This is the last Gen 2 belt step. Next comes a short article section, then the INDX guide continues.",
    # INDX 5.36 Mounting the front puck holder top - left
    1106663: 'Don\'t rely on the "bottom edge" wording in your PDF export of the INDX guide (generated 30 Sep 2026). For this step it says <i>"Double-check that the nut is inserted in the same hole closer to the bottom edge, with the arrow pointing LEFT next to it."</i> The web version of {s:1106795} said the same about the bottom edge (arrow pointing DOWN) until Prusa changed it to "Double-check that the nuts are inserted as shown" in early October 2026. The photos didn\'t change. From comments: several people say the photos for this step and {s:1106795} are swapped or misleading, and that the nut belongs in the hole closer to the <b>top</b> edge ("the up arrow side"). On {s:1106795}, others got it to work by flipping the tool. Whichever way you hold it, look through the holes to check that the nuts line up with the screw holes before you push the tool up.',
    # Gen 2 4.12 Aligning the front side expansion joint
    1111005: "Combined path: the eight heatbed screws are already in place from {s:1099926} (tightened two turns only). Don't insert them again; go straight to aligning. (INDX calls these screws M3x4bT; this Gen 2 step calls them M3x4cT.)",
    # INDX 5.2 Removing the side cover - right
    1104211: "Combined path: the right metal side panel already came off in the article section {a:additional-information-and-removing-the-belts}, and the Bowden-guide was left off ({s:1113247} was skipped). So there's nothing to remove here; keep the panel aside for later.",
    # INDX 6.7 Setting up the printer: Intro
    1109709: "<b>Gen 2 heads-up before you pick a model:</b> the next step (from the Gen 2 guide, not the companion article) says the printer edition must be set to Gen 2 because the new belts and pulleys have a different tooth pitch. One commenter on this step saw a COREONEGEN2 option on this screen and couldn't go back afterwards. Check which models are offered before you confirm. If you're unsure which one fits an INDX + Gen 2 printer, ask Prusa support before continuing.",
    # INDX 4.4 Gantry aligner tool: parts preparation
    1100758: "Heads-up from the comments: several people whose printers were working well before the upgrade found their alignment got <i>worse</i> after this procedure ({s:1100758..1100946}). Others redid it later when docking failed. Read the comments on these steps before loosening anything.",
    # INDX 4.10 Securing the belts
    1101015: "Gen 2 path: commenters found this one of the hardest steps with the new, finer-pitch belts. Many of them fully unscrewed the front belt tensioners first, attached both belt ends to the head-mounting plate, and then refitted the tensioners. Also check that plenty of teeth stick out (see comments). Don't overdo it, though: one commenter on {s:1101093} had homing and calibration failures with the belt ends flush, until they moved each end about 1 mm back.",
    # INDX 4.12 Lubricating the belt tensioner screw
    1116271: "<b>Skip this step.</b> You already lubricated both M3x30 tensioner screws in the article section {a:additional-information-and-removing-the-belts}.",
    # INDX 4.50 Covering the FS - left
    1102933: '4-tool version: when this step says to skip to "PTFE tubes - left side: parts preparation", do the article section {a:mounting-the-side-panels-ptfe-and-right-cover} first. It comes right before that step in this document.',
    # INDX 4.52 Covering the FS - right
    1103025: 'The "return to the Prusa INDX GEN 2 article" instruction is already handled: the article section follows next.',
    # INDX 5.17 Securing the zip ties II.
    1104485: 'The "return to the article" instruction is already handled: the article section and Gen 2 heatbed alignment follow next.',
    # Gen 2 4.19 Aligning the front right expansion joint
    1111025: "This is where the loosely fitted offset sensor ({s:1099523}) gets in the way. Move it aside, align the joint, then put it back.",
    # Gen 2 4.20 Fixing the heatbed
    1111043: "This is the last Gen 2 step for now. The article section that follows tightens the offset sensor, reconnects the X/Y motors and refits the left panel.",
    # Gen 2 5.6 Changing the printer edition
    1156275: "<b>Not in the companion article. Added by the compiler from the Gen 2 guide's preflight chapter.</b> The Gen 2 guide says this edition change is required because the Gen 2 belts and pulleys have a different tooth pitch. How it interacts with INDX firmware isn't documented. See the note on {s:1109709} above. If the edition wasn't already set to Gen 2 during setup, set it as described below before the wizard's belt and axis calibrations. If the Edition menu isn't available, ask Prusa support before continuing.",
}
