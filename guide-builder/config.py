"""Editorial configuration for the combined INDX + Gen 2 guide.

Everything a human decides lives here: which steps go where, how phases and
roadmap rows are grouped, link fixes and article-comment placement. Compiler's
notes are in notes.py, and curated step comments are in comments_keep.txt.

Step references use Prusa's step ids, which stay stable when steps are added
or renumbered. The displayed numbers (e.g. "INDX 3.17") are computed from the
live data at build time.
"""
from dataclasses import dataclass

BASE = 'https://help.prusa3d.com'

GUIDES = {
    'indx': {
        'label': 'INDX',
        'title': 'Prusa INDX Conversion kit for the Prusa CORE One/+',
        'chapters': {
            1: '1-introduction_1096223',
            2: '2-printer-preparation-disassembly_1096231',
            3: '3-z-axis-upgrade_1096239',
            4: '4-indx-toolhead-side-filament-sensors_1096247',
            5: '5-spoolholders-tool-dock-assembly_1096255',
            6: '6-preflight-check_1096263',
        },
    },
    'gen2': {
        'label': 'Gen 2',
        'title': 'Prusa CORE One+ to (Gen 2) upgrade',
        'chapters': {
            1: '1-introduction_1110653',
            2: '2-printer-disassembly_1110664',
            3: '3-belts-upgrade_1110672',
            4: '4-heatbed-upgrade_1110680',
            5: '5-preflight-check_1110689',
        },
    },
}

ARTICLE = {
    'id': 1147602,
    'url': f'{BASE}/article/assemblling-the-prusa-indx-core-one-with-the-gen-2-upgrade_1147602',
    'slug_fragment': 'assemblling-the-prusa-indx-core-one-with-the-gen-2-upgrade',
    'start_marker': 'If you received your Prusa CORE One INDX',
    'end_marker': 'Was this article helpful',
}

# Article <h3> id -> page anchor. Anchors double as progress-checkbox keys in
# readers' browsers, so never renumber existing ones; give new sections new ids.
ARTICLE_SECTIONS = {
    'securing-the-bed-spacer-right-additional-information': 'art-1',
    'removing-old-expansion-joints': 'art-2',
    'removing-the-bed-cable-cover-bottom': 'art-3',
    'additional-information-and-removing-the-belts': 'art-4',
    'gantry-aligner-tool': 'art-5',
    'mounting-the-side-panels-ptfe-and-right-cover': 'art-6',
    'fixing-the-heatbed': 'art-7',
    'mounting-the-left-cover-covering-the-electronics': 'art-8',
}


@dataclass
class Phase:            # starts a phase heading and table-of-contents group
    title: str


@dataclass
class Row:              # starts a roadmap row; its range label is computed from the items that follow
    description: str


@dataclass
class Steps:            # an inclusive range of steps of one chapter, by step id
    guide: str
    chapter: int
    first: int
    last: int


@dataclass
class Article:          # one article section, by its <h3> id
    section: str


# The merge order, derived from the companion article's "until you finish step ..."
# and "continue from step ..." instructions. Titles are in comments for readability.
SEQUENCE = [
    Phase('A. Introduction & disassembly'),
    Row('Introduction, disassembly, front bed spacers'),
    Steps('indx', 1, 1096271, 1096924),     # How to navigate … Prepare your desk
    Steps('indx', 2, 1096990, 1098670),     # Tools … Final step
    Steps('indx', 3, 1098695, 1099288),     # Tools … Securing the bed spacer - right

    Phase('B. Left side opened, rear bed spacer & offset sensor'),
    Row('Unplug X/Y motors; remove left top cover and left metal panel'),
    Article('securing-the-bed-spacer-right-additional-information'),
    Row('Rear bed spacer and offset sensor (offset-sensor screw only a few turns in)'),
    Steps('indx', 3, 1098949, 1099623),     # Removing the rear bed spacer … Securing the offset sensor cable

    Phase('C. Gen 2 expansion joints'),
    Row('Replace the expansion joints; place the 10 mm heatbed spacer'),
    Article('removing-old-expansion-joints'),
    Steps('gen2', 4, 1110931, 1110975),     # Removing old expansion joints … Inserting the heatbed spacer

    Phase('D. Heatbed back in, cables, bed stop'),
    Row('Heatbed back in (screws 2 turns only), cables, bed stop; release belts'),
    Article('removing-the-bed-cable-cover-bottom'),
    Steps('indx', 3, 1099677, 1100550),     # Removing the Bed-cable-cover-bottom … Done
    Steps('indx', 4, 1100576, 1100696),     # Tools … Releasing the belts

    Phase('E. Gen 2 belts & pulleys'),
    Row('Remove right top cover and right panel; lubricate tensioner screws'),
    Article('additional-information-and-removing-the-belts'),
    Row('New pulleys and finer-pitch belts (skip the Bowden-guide step, {s:1113247})'),
    Steps('gen2', 3, 1149188, 1113491),     # Removing the belts … Guiding the upper belt (gantry - right)

    Phase('F. INDX toolhead & filament sensors'),
    Row('Gantry alignment, INDX toolhead, head cable, filament sensors (skip the tensioner-lube step, {s:1116271})'),
    Article('gantry-aligner-tool'),
    Steps('indx', 4, 1100758, 1103025),     # Gantry aligner tool: parts preparation … Covering the FS - right

    Phase('G. Side covers, PTFE tubes, wiper, dock fan cable'),
    Row('Refit both top see-through covers (leave out the left top-middle rivet, and the right one too on 8-tool)'),
    Article('mounting-the-side-panels-ptfe-and-right-cover'),
    Row('PTFE tubes, side handle, nozzle cleaner, dock fan cable'),
    Steps('indx', 4, 1103061, 1104025),     # PTFE tubes - left side: parts preparation … Done
    Steps('indx', 5, 1104051, 1104485),     # Tools … Securing the zip ties II.

    Phase('H. Gen 2 expansion joint alignment'),
    Row('Align the expansion joints and tighten the heatbed'),
    Article('fixing-the-heatbed'),
    Steps('gen2', 4, 1110993, 1111043),     # Expansion joint aligner … Fixing the heatbed

    Phase('I. Closing up, spool holders & tool dock'),
    Row('Tighten the offset sensor; reconnect X/Y motors; left panel (3 rivets)'),
    Article('mounting-the-left-cover-covering-the-electronics'),
    Row('Electronics covers, spool holders, tool dock, top cover, nozzles'),
    Steps('indx', 5, 1105054, 1109439),     # Electronics covers: parts preparation … That's it

    Phase('J. Preflight check'),
    Row('Firmware, set up the printer, Gen 2 edition change (right after {s:1109709}), wizard'),
    Steps('indx', 6, 1109473, 1109709),     # Installing the spoolholder … Setting up the printer: Intro
    # Not in the article: the Gen 2 edition change, placed right after the model choice.
    Steps('gen2', 5, 1156275, 1156275),     # Changing the printer edition
    Steps('indx', 6, 1109747, 1110607),     # Setting up the printer: Network setup … Join Printables!
]

# Links in Prusa's step text that point to the wrong guide (the INDX Founders
# Edition), by the step id they point at -> where they should go instead.
# Values are a step id (int) or an article section id (str).
LINK_REMAP = {
    1067881: 'mounting-the-side-panels-ptfe-and-right-cover',   # 4-tool skip to "PTFE tubes - left side" (article first)
    1068878: 1103969,                                           # 4-tool skip to "Connecting the filament sensor cable"
    1074825: 1109176,                                           # 4-tool skip to "Checking the tubes"
}

# Useful comments on the companion article -> the article section they belong to.
ARTICLE_COMMENTS = {
    101116: 'securing-the-bed-spacer-right-additional-information',   # David R. Campbell: camera cable
    100215: 'securing-the-bed-spacer-right-additional-information',   # Tkadla: remove both panels early
    99447: 'additional-information-and-removing-the-belts',          # Bpendragon: drill for extended bucket
    99902: 'fixing-the-heatbed',                                      # PetrichorPete: sensor blocks front-right joint
    101211: 'mounting-the-left-cover-covering-the-electronics',       # Luis: rivet tip
}
