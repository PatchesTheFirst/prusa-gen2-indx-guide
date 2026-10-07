"""Downloads a fresh snapshot from help.prusa3d.com and reports what changed.

Usage: python fetch.py                 download a new snapshot, then write the report
       python fetch.py --report-only   only write the report, comparing the existing data.prev/ with data/

- The new snapshot goes to data/. The previous one is kept in data.prev/ (replacing any older one).
- CHANGES.md lists what changed since the previous snapshot: steps added, removed, renamed or edited
  (with emphasis on steps that carry compiler's notes or sit at switch points), article changes,
  and every comment that isn't in comments_seen.txt yet.
"""
import datetime, difflib, html, json, os, re, shutil, sys, urllib.request, concurrent.futures as cf
from config import BASE, GUIDES, ARTICLE, SEQUENCE, Steps, Article
from notes import NOTES
from common import ROOT, DATA, Resolved, read_ids, walk_comments, article_sections

UA = {'User-Agent': 'Mozilla/5.0'}
NEW = os.path.join(ROOT, 'data.new')
PREV = os.path.join(ROOT, 'data.prev')


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    return data if binary else data.decode('utf-8')


def get_comments(parent):
    out, page = [], 1
    while True:
        j = json.loads(get(f'{BASE}/edge/comments?lng=en&page={page}&parent={parent}&per_page=100&status=approve'))
        out += j['data']
        if page >= j['info']['total_pages']:
            return out
        page += 1


def tag_tolerant(text):
    """Regex for text whose words may be separated by HTML tags, e.g. 'your <strong>Prusa'."""
    return r'(?:\s|<[^>]+>)*'.join(re.escape(w) for w in text.split())


def extract_article_body(page):
    m = re.search(r'<p[^>]*>(?:\s|<[^>]+>)*' + tag_tolerant(ARTICLE['start_marker']), page)
    if not m:
        sys.exit('Could not find the article start marker; update ARTICLE["start_marker"] in config.py')
    e = re.compile(tag_tolerant(ARTICLE['end_marker'])).search(page, m.start())
    if not e:
        sys.exit('Could not find the article end marker; update ARTICLE["end_marker"] in config.py')
    end = e.start()
    body = page[m.start():end]
    return body[:max(body.rfind('</p>') + 4, body.rfind('</ul>') + 5)]


# ---------------------------------------------------------------- download
def save_comments(sid):
    with open(os.path.join(NEW, 'comments', f'{sid}.json'), 'w', encoding='utf-8') as f:
        json.dump(get_comments(sid), f, ensure_ascii=False)


def download():
    """Fetches everything into data.new/, then moves data/ to data.prev/ and data.new/ to data/."""
    if os.path.exists(NEW):
        shutil.rmtree(NEW)
    os.makedirs(os.path.join(NEW, 'guides'))
    os.makedirs(os.path.join(NEW, 'comments'))

    print('Fetching guide chapters…')
    slugs = [s for g in GUIDES.values() for s in g['chapters'].values()]
    for slug in slugs:
        with open(os.path.join(NEW, 'guides', f'{slug}.json'), 'w', encoding='utf-8') as f:
            f.write(get(f'{BASE}/edge/guide-bundle?locale=en&slug={slug}'))

    print('Fetching the article…')
    with open(os.path.join(NEW, 'article_body.html'), 'w', encoding='utf-8') as f:
        f.write(extract_article_body(get(ARTICLE['url'])))
    with open(os.path.join(NEW, 'article_comments.json'), 'w', encoding='utf-8') as f:
        json.dump(get_comments(ARTICLE['id']), f, ensure_ascii=False)

    print('Fetching comments…')
    with_comments = []
    for slug in slugs:
        with open(os.path.join(NEW, 'guides', f'{slug}.json'), encoding='utf-8') as f:
            with_comments += [s['id'] for s in json.load(f)['data']['steps'] if s['comments']]
    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(save_comments, with_comments))
    today = datetime.date.today()
    with open(os.path.join(NEW, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump({'fetched': today.isoformat(), 'fetched_label': f'{today.day} {today:%b %Y}'}, f, indent=2)

    # swap snapshots
    if os.path.exists(PREV):
        shutil.rmtree(PREV)
    if os.path.exists(DATA):
        os.rename(DATA, PREV)
    os.rename(NEW, DATA)


if '--report-only' in sys.argv[1:]:
    if not os.path.exists(PREV):
        sys.exit('--report-only needs a previous snapshot in data.prev/')
else:
    download()

# ---------------------------------------------------------------- report
def text_of(step):
    return [re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', l['title']))).strip()
            for l in sorted(step['lines'], key=lambda x: x['order'])]


def imgs_of(step):
    return [(g.get('child') or g).get('original') for g in (step['media'].get('gallery') or [])]


def load_steps(data):
    out = {}
    for g, gd in GUIDES.items():
        for ch, slug in gd['chapters'].items():
            p = os.path.join(data, 'guides', f'{slug}.json')
            if os.path.exists(p):
                with open(p, encoding='utf-8') as f:
                    out[(g, ch)] = json.load(f)['data']['steps']
    return out


lines = [f'# Changes since the previous snapshot', '']
new_meta = json.load(open(os.path.join(DATA, 'meta.json'), encoding='utf-8'))
old_meta = json.load(open(os.path.join(PREV, 'meta.json'), encoding='utf-8')) if os.path.exists(os.path.join(PREV, 'meta.json')) else {}
lines.append(f'Previous snapshot: {old_meta.get("fetched", "none")} · new snapshot: {new_meta["fetched"]}\n')

R = Resolved()
if R.errors:
    lines += ['## ⚠ The sequence no longer resolves', ''] + [f'- {e}' for e in R.errors] + ['']

# switch-point steps: first/last of every Steps range and the steps around article sections
boundary = set()
for it in SEQUENCE:
    if isinstance(it, Steps):
        boundary |= {it.first, it.last}
flat = [x for x in R.items if isinstance(x, tuple)]
for k, x in enumerate(flat):
    if x[0] == 'article':
        for y in (flat[k - 1] if k else None, flat[k + 1] if k + 1 < len(flat) else None):
            if y and y[0] == 'step':
                boundary.add(y[5]['id'])

old_steps, new_steps = load_steps(PREV), load_steps(DATA)
struct, edits = [], []
for key in new_steps:
    g, ch = key
    o = {s['id']: s for s in old_steps.get(key, [])}
    n = {s['id']: s for s in new_steps[key]}
    oid, nid = [s['id'] for s in old_steps.get(key, [])], [s['id'] for s in new_steps[key]]
    name = f'{GUIDES[g]["label"]} ch. {ch}'
    for i, sid in enumerate(nid, 1):
        if sid not in o:
            struct.append(f'- **{name}: new step {ch}.{i}** "{n[sid]["title"]}" (id {sid}){" — inside a range used by the guide" if sid in R.in_doc else ""}')
    for sid in oid:
        if sid not in n:
            struct.append(f'- **{name}: step removed** "{o[sid]["title"]}" (id {sid}){" — ⚠ was in the guide" if sid in boundary or sid in NOTES else ""}')
    common_ids = [i for i in nid if i in o]
    if common_ids != [i for i in oid if i in n]:
        struct.append(f'- **{name}: steps were reordered**')
    for sid in common_ids:
        flags = []
        if sid in NOTES:
            flags.append('has a compiler\'s note')
        if sid in boundary:
            flags.append('switch point')
        tag = f' ({", ".join(flags)})' if flags else ''
        label = f'{name}, "{n[sid]["title"]}" (id {sid}){tag}'
        if o[sid]['title'] != n[sid]['title']:
            struct.append(f'- {label}: title changed from "{o[sid]["title"]}"')
        if sid not in R.in_doc:
            continue
        ot, nt = text_of(o[sid]), text_of(n[sid])
        if ot != nt:
            diff = [d for d in difflib.unified_diff(ot, nt, lineterm='', n=0) if not d.startswith(('---', '+++', '@@'))]
            edits.append(f'- {label}: text changed\n' + '\n'.join(f'    {d}' for d in diff))
        if imgs_of(o[sid]) != imgs_of(n[sid]):
            edits.append(f'- {label}: images changed ({len(imgs_of(o[sid]))} → {len(imgs_of(n[sid]))})')
lines += ['## Guide structure', ''] + (struct or ['No steps added, removed, renamed or reordered.']) + ['']
lines += ['## Edited steps in the document', ''] + (edits or ['None.']) + ['']

# article
art_lines = []
if os.path.exists(os.path.join(PREV, 'article_body.html')):
    _, osecs = article_sections(PREV)
    _, nsecs = article_sections(DATA)
    od, nd = {h: (t, b) for h, t, b in osecs}, {h: (t, b) for h, t, b in nsecs}
    for h, t, b in nsecs:
        if h not in od:
            art_lines.append(f'- **New section** "{t}" (id `{h}`) — place it in SEQUENCE and give it an anchor in ARTICLE_SECTIONS')
    for h, t, b in osecs:
        if h not in nd:
            art_lines.append(f'- **Section removed** "{t}" (id `{h}`)')
    def plain(b):
        b = re.sub(r'<(p|li|h3|br)[^>]*>', '\n', b)
        return [x for x in (re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', l))).strip() for l in b.split('\n')) if x]
    def links(b):
        return re.findall(r'href="([^"]+)"', b)
    for h, t, b in nsecs:
        if h in od:
            if plain(od[h][1]) != plain(b):
                diff = [d for d in difflib.unified_diff(plain(od[h][1]), plain(b), lineterm='', n=0) if not d.startswith(('---', '+++', '@@'))]
                art_lines.append(f'- Section "{t}": text changed\n' + '\n'.join(f'    {d}' for d in diff))
            if links(od[h][1]) != links(b):
                art_lines.append(f'- Section "{t}": links changed: {links(od[h][1])} → {links(b)}')
lines += ['## Companion article', ''] + (art_lines or ['No changes.']) + ['']

# comments
seen = read_ids(os.path.join(ROOT, 'comments_seen.txt'))
keep = read_ids(os.path.join(ROOT, 'comments_keep.txt'))
newc, all_ids = [], set()


def fmt(c, where):
    staff = ' **[Prusa staff]**' if c['role'] != 'visitor' else ''
    parent = f' (reply to {c["parent"]})' if c['parent'] else ''
    text = re.sub(r'\s+', ' ', html.unescape(c['content'])).strip()
    return f'- `{c["id"]}` {where} · {c["user"]}{staff}, {c["date"][:10]}{parent}: {text}'


for x in flat:
    if x[0] != 'step':
        continue
    p = os.path.join(DATA, 'comments', f'{x[5]["id"]}.json')
    cs = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []
    for c in walk_comments(cs):
        all_ids.add(c['id'])
        if c['id'] not in seen:
            newc.append(fmt(c, f'{R.label(x[5]["id"])} "{x[5]["title"]}"'))
acs = json.load(open(os.path.join(DATA, 'article_comments.json'), encoding='utf-8'))
for c in walk_comments(acs):
    all_ids.add(c['id'])
    if c['id'] not in seen:
        newc.append(fmt(c, 'Article'))
gone = sorted(keep - all_ids)
lines += [f'## New comments ({len(newc)})', '',
          'Not yet in comments_seen.txt. Decide for each whether to keep it (add to comments_keep.txt, or to '
          'ARTICLE_COMMENTS for the article), then add all reviewed ids to comments_seen.txt.', ''] + (newc or ['None.']) + ['']
if gone:
    lines += ['## Kept comments that disappeared', ''] + [f'- `{i}`' for i in gone] + ['']

with open(os.path.join(ROOT, 'CHANGES.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Done. {len(struct)} structural changes, {len(edits)} edited steps, {len(art_lines)} article changes, '
      f'{len(newc)} new comments. See CHANGES.md.')
