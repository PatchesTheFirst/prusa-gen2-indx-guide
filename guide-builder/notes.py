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
    1099523: "Gen 2 path: leave this M3x10 screw only a few turns in, as the step says. You tighten it in the article section {a:mounting-the-left-cover-covering-the-electronics}, after the expansion joints are aligned. From comments: the sensor can get in the way when you align the front-right expansion joint ({s:1111025}).",
    # Gen 2 4.4 Removing old expansion joints
    1110931: "The Gen 2 guide says to keep one old expansion joint for the Gen 2 nozzle wiper. The Gen 2 nozzle-wiper steps are <b>not</b> part of the INDX path, since INDX fits its own nozzle cleaner in chapter 5. Keep the old joints anyway, like every other removed part.",
    # Gen 2 4.8 Inserting the heatbed spacer
    1110975: "This spacer sits loose for the next few sections. Commenters taped it in place, or used a screw or Allen key to keep it centered, until the heatbed goes back on in {s:1099880}.",
    # INDX 3.21 Heatbed cable covers: parts preparation
    1099715: "Gen 2 path: you already placed the new <b>10 mm</b> heatbed spacer from the Gen 2 kit in {s:1110975}. Don't use the old 8 mm spacer listed here.",
    # INDX 3.25 Securing the heatbed
    1099926: "Gen 2 path: only two turns, as the step says. The heatbed screws get their final tightening with the aligner in {s:1110993..1111043}, later in this document.",
    # Gen 2 3.9 Installing the new pulley (right motor)
    1113142: "From comments: many people found the new pulleys very hard to push onto the motor shaft, here and on the left motor ({s:1113272}).",
    # Gen 2 3.16 Right motor screws: parts preparation
    1113217: "INDX path: the M3nS nut and M3x10 listed here are for the Bowden-guide, which INDX doesn't use (see the article section above and {s:1113247}). On this path you never removed them: the Bowden-guide is still screwed to the motor mount and comes off in {s:1104211}.",
    # Gen 2 3.17 Tightening the right motor
    1113237: "INDX path: the Main-cable-clip part of this step doesn't apply, because the main cable was already removed in {s:1098321}.",
    # Gen 2 3.18 Securing the Bowden-guide
    1113247: "<b>Skip this step on the INDX path.</b> The article says the Bowden-guide isn't needed for the INDX conversion and can be removed once it's detached from the motor mount. On this path it's still attached; you remove it in {s:1104211}.",
    # Gen 2 3.6 Releasing the right motor
    1149258: "INDX path: skip the Main-cable-clip lines. The main cable and its clip were already removed in {s:1098321}.",
    # Gen 2 3.38 Guiding the upper belt (gantry - right)
    1113491: "This is the last Gen 2 belt step. Next comes a short article section, then the INDX guide continues.",
    # INDX 5.36 Mounting the front puck holder top - left
    1106663: 'Older copies of this guide (for example PDF exports from late September 2026) say the nut goes in the hole "closer to the bottom edge", here and on {s:1106795}. Prusa has since dropped that wording from both steps, which now just say to insert the nuts as shown. From comments: several people say the photos for this step and {s:1106795} are swapped or misleading, and that the nut belongs in the hole closer to the <b>top</b> edge ("the up arrow side"). On {s:1106795}, others got it to work by flipping the tool. Whichever way you hold it, look through the holes to check that the nuts line up with the screw holes before you push the tool up.',
    # Gen 2 4.12 Aligning the front side expansion joint
    1111005: "Combined path: the eight heatbed screws are already in place from {s:1099926} (tightened two turns only). Don't insert them again; go straight to aligning. (INDX calls these screws M3x4bT; this Gen 2 step calls them M3x4cT.)",
    # INDX 5.2 Removing the side cover - right
    1104211: "Combined path: <b>do remove the Bowden-guide</b> as this step says. It's still screwed to the right rear motor mount, because this path never detached it ({s:1113247} only skipped putting it back). The right metal side panel already came off in the article section {a:additional-information-and-removing-the-belts}, so skip the rivet and side-cover lines and keep the panel aside for later.",
    # INDX 6.11 Wizard: Belt tensioning
    1109875: "<b>Don't overtighten.</b> On the compiler's own build, the left belt-tensioner printed part broke at this step from overtightening the belts. Take Prusa's warning below seriously: read the linked belt-tension article first and adjust in small steps.",
    # INDX 6.7 Setting up the printer: Intro
    1109709: "<b>Gen 2 heads-up before you pick a model:</b> the next step (from the Gen 2 guide, not the companion article) says the printer edition must be set to Gen 2 because the new belts and pulleys have a different tooth pitch. On the compiler's printer, set up with firmware 6.9.2, the edition was already set to Gen 2 INDX. One commenter on this step was offered COREONEGEN2 here instead of COREONEINDX and couldn't go back afterwards. Check which models are offered before you confirm. If none of them fits an INDX + Gen 2 printer, ask Prusa support before continuing.",
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
    1104485: 'The "return to the Prusa INDX GEN 2 article" instruction is already handled: the article section and Gen 2 heatbed alignment follow next.',
    # Gen 2 4.19 Aligning the front right expansion joint
    1111025: "From comments: the loosely fitted offset sensor ({s:1099523}) can get in the way here. Some commenters moved it aside, aligned the joint and put it back. Others left it in place and used the aligner upside down, the side slot, or an Allen key to hold the joint while tightening.",
    # Gen 2 4.20 Fixing the heatbed
    1111043: "This is the last Gen 2 step for now. The article section that follows tightens the offset sensor, reconnects the X/Y motors and refits the left panel.",
    # Gen 2 5.6 Changing the printer edition
    1156275: "<b>Not in the companion article. Added by the compiler from the Gen 2 guide's preflight chapter.</b> The Gen 2 guide says this edition change is required because the Gen 2 belts and pulleys have a different tooth pitch. On the compiler's printer, set up with firmware 6.9.2, the edition was already set to Gen 2 INDX, so this step was only a check. Look under Settings → Hardware → Edition: if it already shows Gen 2, there's nothing to change. If not, set it before the wizard's belt and axis calibrations, choosing the Gen 2 option that matches INDX. The step below names CORE One+ Gen2; if that's the only Gen 2 option listed, check with Prusa support before confirming. If there's no Edition menu, commenters say your firmware is too old. Update it, or ask Prusa support before continuing.",
}
