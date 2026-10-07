"""Deterministic checks of the configuration, the data snapshot and the built page.

Usage: python verify.py        (run after build.py; exits 1 if any check FAILs)
"""
import html, os, re, sys
from config import GUIDES, ARTICLE, ARTICLE_SECTIONS, LINK_REMAP, ARTICLE_COMMENTS
from notes import NOTES
from common import (Resolved, ROOT, OUT, chapter_steps, step_comments, article_comments, read_ids,
                    walk_comments, resolve_refs)

results = []


def check(ok, name, detail=''):
    results.append(('PASS' if ok else 'FAIL', name, detail))


def warn(cond, name, detail=''):
    results.append(('PASS' if cond else 'WARN', name, detail))


def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', html.unescape(re.sub('<[^>]+>', '', t)).lower()).strip()


R = Resolved()
check(not R.errors, 'Sequence resolves against the data', '; '.join(R.errors))

steps = [it for it in R.items if isinstance(it, tuple) and it[0] == 'step']
ids = [it[5]['id'] for it in steps]
dups = sorted({i for i in ids if ids.count(i) > 1})
check(not dups, 'No step appears twice', f'duplicates: {dups}')

# every INDX step exactly once, in original order
indx_all = [s['id'] for ch in GUIDES['indx']['chapters'] for s in chapter_steps('indx', ch)]
indx_doc = [i for i in ids if i in set(indx_all)]
missing = [R.label(i) for i in indx_all if i not in set(indx_doc)]
check(not missing, 'Every INDX step is included', f'missing: {missing}')
check(indx_doc == [i for i in indx_all if i in set(indx_doc)], 'INDX steps keep their original order')

# Gen 2 steps used (informational) and their order within each chapter
g2 = [it for it in steps if it[1] == 'gen2']
order_ok = all(not (a[2] == b[2] and a[3] >= b[3]) for a, b in zip(g2, g2[1:]) if a[2] == b[2])
check(order_ok, 'Gen 2 steps keep their original order within each chapter')
results.append(('INFO', 'Gen 2 steps used', f'{len(g2)} steps'))

# article sections
arts = [it for it in R.items if isinstance(it, tuple) and it[0] == 'article']
placed = [a[1] for a in arts]
unplaced = [h for h in R.art_order if h not in placed]
check(not unplaced, 'Every article section is placed', f'unplaced: {unplaced}')
check(len(placed) == len(set(placed)), 'No article section is placed twice')
unknown_anchor = [h for h in R.art_order if h not in ARTICLE_SECTIONS]
check(not unknown_anchor, 'Every article section has a stable anchor in ARTICLE_SECTIONS', f'missing: {unknown_anchor}')

# article switch points: "until you finish step X" and "continue from" links
flat = [it for it in R.items if isinstance(it, tuple)]
before_article = {}   # section -> title of the step right before it
after_article = {}    # section -> id of the step right after it
for k, it in enumerate(flat):
    if it[0] == 'article':
        prev = next((x for x in reversed(flat[:k]) if x[0] == 'step'), None)
        nxt = next((x for x in flat[k + 1:] if x[0] == 'step'), None)
        before_article[it[1]] = norm(prev[5]['title']) if prev else ''
        after_article[it[1]] = nxt[5]['id'] if nxt else None
finish_names = []
for sec, (title, body) in R.art.items():
    for m in re.finditer(r'until you finish step\s*(?:<[^>]+>|\s)*([^<.,:]+)', body, re.I):
        finish_names.append((sec, norm(m.group(1))))
pre_titles = set(before_article.values())
bad_finish = [f'{s}: "{n}"' for s, n in finish_names if n not in pre_titles]
check(not bad_finish, 'Each "until you finish step X" in the article is the step right before an article section', '; '.join(bad_finish))
unnamed = [s for s, t in before_article.items() if t and t not in {n for _, n in finish_names}]
warn(not unnamed, 'Each article section follows a step the article names as a finish point', f'not named: {unnamed}')
bad_cont = []
for sec, (title, body) in R.art.items():
    for m in re.finditer(r'href="[^"]*/guide/[^"#]*#(\d+)"', body):
        sid = int(m.group(1))
        if sid in R.in_doc and sid != after_article.get(sec) and sid != ids[0]:   # ids[0]: "follow the guide from the start"
            bad_cont.append(f'{sec} links {R.label(sid)} but is followed by '
                            f'{R.label(after_article[sec]) if after_article.get(sec) else "nothing"}')
check(not bad_cont, 'Each article "continue from" link points to the step right after that section', '; '.join(bad_cont))

# notes and references
not_in_doc = [k for k in NOTES if k not in R.in_doc]
check(not not_in_doc, 'Every compiler\'s note is on a step in the document', f'{not_in_doc}')
ref_err = []
for v in NOTES.values():
    resolve_refs(v, R, ref_err)
check(not ref_err, 'All {s:..}/{a:..} references in notes resolve', '; '.join(sorted(set(ref_err))))
bad_remap = [k for k, v in LINK_REMAP.items() if (v not in ARTICLE_SECTIONS if isinstance(v, str) else v not in R.in_doc)]
check(not bad_remap, 'LINK_REMAP targets exist', f'{bad_remap}')

# links in Prusa's step text that point to a same-named chapter of another guide edition
known = {slug for g in GUIDES.values() for slug in g['chapters'].values()}
known_names = {slug.rsplit('_', 1)[0] for slug in known}
wrong_edition = []
for it in steps:
    for l in it[5]['lines']:
        for m in re.finditer(r'href="[^"]*/guide/([^"#/?]+)#(\d+)', l['title']):
            slug, target = m.group(1), int(m.group(2))
            if slug not in known and slug.rsplit('_', 1)[0] in known_names and target not in LINK_REMAP:
                wrong_edition.append(f'{R.label(it[5]["id"])} -> {slug}#{target}')
check(not wrong_edition, 'No step links into another edition of the guide (add them to LINK_REMAP)', '; '.join(wrong_edition))

# comments
keep = read_ids(os.path.join(ROOT, 'comments_keep.txt'))
seen = read_ids(os.path.join(ROOT, 'comments_seen.txt'))
doc_comment_ids, unseen = set(), []
for it in steps:
    for c in walk_comments(step_comments(it[5]['id'])):
        doc_comment_ids.add(c['id'])
        if c['id'] not in seen:
            unseen.append(f'{R.label(it[5]["id"])}#{c["id"]}')
acs = article_comments()
for c in walk_comments(acs):
    doc_comment_ids.add(c['id'])
    if c['id'] not in seen:
        unseen.append(f'article#{c["id"]}')
stale = sorted(keep - doc_comment_ids)
warn(not stale, 'Every kept comment id still exists on a step in the document', f'{len(stale)} not found: {stale[:20]}')
bad_ac = [k for k, v in ARTICLE_COMMENTS.items() if k not in {c['id'] for c in walk_comments(acs)} or v not in ARTICLE_SECTIONS]
warn(not bad_ac, 'ARTICLE_COMMENTS ids and sections exist', f'{bad_ac}')
warn(not unseen, 'No unreviewed comments', f'{len(unseen)} new: {", ".join(unseen[:40])}{" …" if len(unseen) > 40 else ""}')
missing_c = [R.label(it[5]['id']) for it in steps if it[5]['comments'] and not step_comments(it[5]['id'])]
warn(not missing_c, 'Comment threads are downloaded for every step that has comments', f'{missing_c[:20]}')

# built page
page_path = os.path.join(OUT, 'index.html')
if not os.path.exists(page_path):
    check(False, 'Built page exists', page_path)
else:
    page = open(page_path, encoding='utf-8').read()
    anchors = set(re.findall(r'id="([^"]+)"', page))
    broken = sorted({h for h in re.findall(r'href="#([^"]+)"', page) if h not in anchors})
    check(not broken, 'Internal links resolve', f'{broken}')
    imgs = set(re.findall(r'src="(img/[^"]+)"', page))
    missing_img = [i for i in imgs if not os.path.exists(os.path.join(OUT, i))]
    check(not missing_img, 'All images exist locally', f'{len(missing_img)} missing, e.g. {missing_img[:5]}')
    sections = re.findall(r'<section class="step[^"]*" id="([^"]+)"', page)
    expected = ['art-0'] + [f's-{x[5]["id"]}' if x[0] == 'step' else ARTICLE_SECTIONS[x[1]] for x in flat]
    check(sections == expected, 'Built page matches the configured sequence (page is up to date)')
    leftover = re.findall(r'\{(?:s|a):[^}]+\}|\{\{[A-Z_]+\}\}', page)
    check(not leftover, 'No unresolved placeholders in the page', f'{leftover[:5]}')

w = max(len(r[1]) for r in results)
for status, name, detail in results:
    print(f'{status:4}  {name}' + (f'\n        {detail}' if detail and status != 'PASS' else ''))
fails = sum(r[0] == 'FAIL' for r in results)
warns = sum(r[0] == 'WARN' for r in results)
print(f'\n{fails} failed, {warns} warnings')
sys.exit(1 if fails else 0)
