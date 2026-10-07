"""Shared helpers: data snapshot access, sequence resolution, step labels, references."""
import json, os, re, html
from config import GUIDES, ARTICLE, ARTICLE_SECTIONS, SEQUENCE, Steps, Article

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.dirname(ROOT)      # the repo root: index.html and img/ are published from there


def jload(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def bundle(slug, data=DATA):
    return jload(os.path.join(data, 'guides', f'{slug}.json'))['data']


def chapter_steps(guide, chapter, data=DATA):
    return bundle(GUIDES[guide]['chapters'][chapter], data)['steps']


def step_comments(step_id, data=DATA):
    p = os.path.join(data, 'comments', f'{step_id}.json')
    return jload(p) if os.path.exists(p) else []


def article_body(data=DATA):
    with open(os.path.join(data, 'article_body.html'), encoding='utf-8') as f:
        return f.read()


def article_comments(data=DATA):
    return jload(os.path.join(data, 'article_comments.json'))


def article_sections(data=DATA):
    """Returns (intro_html, [(h3_id, title, body_html), ...]) in article order."""
    parts = re.split(r'(<h3[^>]*>.*?</h3>)', article_body(data), flags=re.S)
    secs = []
    for i in range(1, len(parts), 2):
        m = re.search(r'id="([^"]+)"', parts[i])
        title = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', parts[i]))).strip()
        secs.append((m.group(1) if m else '', title, parts[i + 1]))
    return parts[0], secs


class Resolved:
    """The SEQUENCE resolved against a data snapshot."""

    def __init__(self, data=DATA):
        self.data = data
        self.items = []       # config items with Steps expanded: ('step', guide, ch, num, slug, step) / ('article', h3id, title, html) / Phase / Row
        self.pos = {}         # step id -> (guide, chapter, number) for every step of every configured chapter
        self.errors = []
        for g, gd in GUIDES.items():
            for ch, slug in gd['chapters'].items():
                p = os.path.join(data, 'guides', f'{slug}.json')
                if not os.path.exists(p):
                    continue
                for n, s in enumerate(bundle(slug, data)['steps'], 1):
                    self.pos[s['id']] = (g, ch, n)
        _, secs = article_sections(data)
        self.art = {h: (t, b) for h, t, b in secs}
        self.art_order = [h for h, _, _ in secs]
        for it in SEQUENCE:
            if isinstance(it, Steps):
                st = chapter_steps(it.guide, it.chapter, data)
                ids = [s['id'] for s in st]
                if it.first not in ids or it.last not in ids:
                    self.errors.append(f'{it}: first/last step id not found in {it.guide} chapter {it.chapter}')
                    continue
                a, b = ids.index(it.first), ids.index(it.last)
                if a > b:
                    self.errors.append(f'{it}: first step comes after last step')
                    continue
                slug = GUIDES[it.guide]['chapters'][it.chapter]
                for n in range(a, b + 1):
                    self.items.append(('step', it.guide, it.chapter, n + 1, slug, st[n]))
            elif isinstance(it, Article):
                if it.section not in self.art:
                    self.errors.append(f'Article section "{it.section}" not found in the article')
                    continue
                t, b = self.art[it.section]
                self.items.append(('article', it.section, t, b))
            else:
                self.items.append(it)
        self.in_doc = {x[5]['id'] for x in self.items if isinstance(x, tuple) and x[0] == 'step'}

    def label(self, step_id):
        g, ch, n = self.pos[step_id]
        return f'{GUIDES[g]["label"]} {ch}.{n}'

    def range_label(self, a, b):
        ga, cha, na = self.pos[a]
        gb, chb, nb = self.pos[b]
        if (ga, cha) == (gb, chb):
            return f'{GUIDES[ga]["label"]} {cha}.{na}–{cha}.{nb}' if na != nb else self.label(a)
        return f'{self.label(a)} – {self.label(b)}'


def ranges_label(segs, resolved, prefix_guides):
    """Compact label for a list of (guide, chapter, first_num, last_num) segments, merging
    adjacent ranges and collapsing full chapters, e.g. "Ch. 1–2, 3.1–3.10"."""
    # group by guide (in order of first appearance), then merge contiguous ranges of the
    # same chapter even if another guide's steps were inserted between them
    order = list(dict.fromkeys(g for g, *_ in segs))
    merged = []
    for g in order:
        for _, ch, a, b in sorted(s for s in segs if s[0] == g):
            if merged and merged[-1][0] == g and merged[-1][1] == ch and merged[-1][3] + 1 == a:
                merged[-1][3] = b
            else:
                merged.append([g, ch, a, b])
    nsteps = {}
    for g, gd in GUIDES.items():
        for ch, slug in gd['chapters'].items():
            nsteps[(g, ch)] = sum(1 for v in resolved.pos.values() if v[0] == g and v[1] == ch)
    out = []      # [guide, text-parts]
    for g, ch, a, b in merged:
        full = a == 1 and b == nsteps[(g, ch)]
        part = ('full', ch) if full else ('part', f'{ch}.{a}' + (f'–{ch}.{b}' if b != a else ''))
        if out and out[-1][0] == g:
            out[-1][1].append(part)
        else:
            out.append([g, [part]])
    texts = []
    for g, parts in out:
        chunks, i = [], 0
        while i < len(parts):
            if parts[i][0] == 'full':
                j = i
                while j + 1 < len(parts) and parts[j + 1][0] == 'full' and parts[j + 1][1] == parts[j][1] + 1:
                    j += 1
                chunks.append(f'Ch. {parts[i][1]}' + (f'–{parts[j][1]}' if j > i else ''))
                i = j + 1
            else:
                chunks.append(parts[i][1])
                i += 1
        t = ', '.join(chunks)
        texts.append(f'{GUIDES[g]["label"]} {t}' if prefix_guides else t)
    return ', '.join(texts)


def resolve_refs(text, resolved, errors=None):
    """Replace {s:ID}, {s:ID..ID} and {a:section} with internal links."""
    def rep(m):
        kind, val = m.group(1), m.group(2)
        try:
            if kind == 's':
                if '..' in val:
                    a, b = (int(x) for x in val.split('..'))
                    return f'<a href="#s-{a}">{resolved.range_label(a, b)}</a>'
                sid = int(val)
                return f'<a href="#s-{sid}">{resolved.label(sid)}</a>'
            t, _ = resolved.art[val]
            return f'<a href="#{ARTICLE_SECTIONS[val]}">{html.escape(t)}</a>'
        except (KeyError, ValueError):
            if errors is not None:
                errors.append(f'Unresolvable reference {m.group(0)}')
            return m.group(0)
    return re.sub(r'\{(s|a):([^}]+)\}', rep, text)


def read_ids(path):
    """Reads a list of comment ids: the first token of each non-empty, non-# line."""
    ids = set()
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ids.add(int(line.split()[0]))
    return ids


def walk_comments(cs):
    for c in cs:
        yield c
        yield from walk_comments(c['replies'])
