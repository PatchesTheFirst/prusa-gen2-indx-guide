"""Builds ../index.html (and downloads its images into ../img/) from the data snapshot.

Usage: python build.py [--noimg] [--prune]
  --noimg  don't download missing images
  --prune  delete images in ../img that the page no longer uses
"""
import html, os, re, sys, urllib.request, concurrent.futures as cf
from config import BASE, GUIDES, ARTICLE, ARTICLE_SECTIONS, LINK_REMAP, ARTICLE_COMMENTS, Phase, Row
from notes import NOTES
from common import (Resolved, OUT, ROOT, DATA, jload, bundle, article_sections, article_comments, step_comments,
                    ranges_label, resolve_refs, read_ids, walk_comments)

IMG = os.path.join(OUT, 'img')
KEEP = read_ids(os.path.join(ROOT, 'comments_keep.txt')) | set(ARTICLE_COMMENTS)
R = Resolved()
if R.errors:
    sys.exit('Sequence errors:\n  ' + '\n  '.join(R.errors))
ref_errors = []


def refs(text):
    return resolve_refs(text, R, ref_errors)


def guide_url(slug):
    return f'{BASE}/guide/{slug}'


# ---------------------------------------------------------------- links
def fix_links(h):
    def rep(m):
        href = html.unescape(m.group(1))
        mm = re.search(r'/guide/[^#"]*#(\d+)', href)
        if mm and int(mm.group(1)) in LINK_REMAP:
            target = LINK_REMAP[int(mm.group(1))]
            return f'href="#{ARTICLE_SECTIONS[target] if isinstance(target, str) else f"s-{target}"}"'
        if mm and int(mm.group(1)) in R.in_doc:
            return f'href="#s-{mm.group(1)}"'
        if ARTICLE['slug_fragment'] in href:
            frag = href.split('#')[1] if '#' in href else ''
            return f'href="#{ARTICLE_SECTIONS.get(frag, "art-0")}"'
        if href.startswith('/'):
            href = BASE + href
        return f'href="{html.escape(href)}" target="_blank" rel="noopener"'
    return re.sub(r'href="([^"]*)"', rep, h)


# ---------------------------------------------------------------- images
downloads = {}


def local_img(url):
    name = url.split('/')[-1].split('?')[0]
    downloads[url] = os.path.join(IMG, name)
    return 'img/' + name


def gallery_imgs(step):
    out = []
    for g in (step['media'].get('gallery') or []):
        src = g.get('child') or g          # 'child' is the annotated ("painted") version the site shows
        disp = src.get('large') or src.get('original')
        full = src.get('original') or disp
        out.append((local_img(disp), full))
    return out


def clean_article_html(h):
    def img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        ss = re.search(r'srcSet="([^"]+)"', tag)
        disp = src
        if ss:
            for cand in ss.group(1).split(','):
                u, w = cand.strip().rsplit(' ', 1)
                if w == '800w':
                    disp = u
        return f'<a class="zoom" href="{src}" target="_blank" rel="noopener"><img loading="lazy" src="{local_img(disp)}" alt=""></a>'
    h = re.sub(r'<img[^>]*>', img, h)
    h = re.sub(r'</?span[^>]*>', '', h)
    h = re.sub(r'\s(style|data-[\w-]+|class)="[^"]*"', '', h)
    h = re.sub(r'<p>(\s|&nbsp;|\xa0)*</p>', '', h)
    h = h.replace('\xa0', ' ')
    return fix_links(h)


# ---------------------------------------------------------------- comments
def c_text(t):
    t = html.escape(html.unescape(t).strip())
    t = re.sub(r'(https?://[^\s<]+)', r'<a href="\1">\1</a>', t)
    return fix_links(t.replace('\n', '<br>'))


def is_useful(c):
    return c['id'] in KEEP or c['role'] != 'visitor'


def prune(cs):
    """Keeps useful comments plus the ancestors needed to show useful replies in context."""
    out = []
    for c in cs:
        kids = prune(c['replies'])
        if is_useful(c) or kids:
            out.append((c, kids))
    return out


def walk(tree):
    for c, kids in tree:
        yield c
        yield from walk(kids)


def render_comments(tree):
    h = ''
    for c, kids in tree:
        staff = c['role'] != 'visitor'
        dim = '' if is_useful(c) else ' ctx'
        h += (f'<div class="cmt{" staff" if staff else ""}{dim}"><div class="cmeta"><b>{html.escape(c["user"])}</b>'
              f'{"<span class=staffb>Prusa staff</span>" if staff else ""} · {c["date"][:10]}</div>'
              f'<div class="ctext">{c_text(c["content"])}</div>')
        if kids:
            h += f'<div class="replies">{render_comments(kids)}</div>'
        h += '</div>'
    return h


def comments_block(raw, online_url):
    total = sum(1 for _ in walk_comments(raw))
    if not total:
        return ''
    tree = prune(raw)
    if not tree:
        return (f'<div class="nocmt">{total} comment{"s" if total != 1 else ""} online, none with practical info · '
                f'<a href="{online_url}" target="_blank" rel="noopener">read online</a></div>')
    shown = sum(1 for c in walk(tree) if is_useful(c))
    return (f'<details class="comments"><summary><span class="ccount">{shown} useful comment{"s" if shown != 1 else ""}</span>'
            f' <span class="cof">of {total}</span></summary>{render_comments(tree)}'
            f'<div class="call"><a href="{online_url}" target="_blank" rel="noopener">{"All " + str(total) + " comments" if total > 1 else "The comment"} online ↗</a></div></details>')


ART_COMMENTS = article_comments()


def article_comments_block(section):
    useful = [c for c in walk_comments(ART_COMMENTS) if ARTICLE_COMMENTS.get(c['id']) == section]
    if not useful:
        return ''
    return (f'<details class="comments"><summary><span class="ccount">Useful comments on the article</span></summary>'
            f'{render_comments([(c, []) for c in useful])}'
            f'<div class="call"><a href="{ARTICLE["url"]}#comments-section" target="_blank" rel="noopener">All article comments online ↗</a></div></details>')


# ---------------------------------------------------------------- steps
LINE_COLORS = {'yellow', 'light_blue', 'orange', 'blue', 'green', 'violet', 'red'}
ICONS = {'note': 'i', 'caution': '!', 'reminder': '✓'}


def render_lines(lines):
    h = '<ul class="lines">'
    for l in sorted(lines, key=lambda x: x['order']):
        m = l['meta'] if isinstance(l['meta'], dict) else {}
        cls = []
        if m.get('level') in ('1', 1):
            cls.append('lv1')
        icon = m.get('icon')
        if icon:
            cls.append('ic-' + icon)
        color = m.get('color')
        if color in LINE_COLORS:
            dot = f'<span class="dot c-{color}"></span>'
        elif icon:
            dot = f'<span class="ico">{ICONS.get(icon, "•")}</span>'
        else:
            dot = '<span class="dot c-none"></span>'
        h += f'<li class="{" ".join(cls)}">{dot}<span class="lt">{fix_links(l["title"])}</span></li>'
    return h + '</ul>'


def step_html(guide, ch, num, slug, s):
    sid = s['id']
    url = f'{guide_url(slug)}#{sid}'
    badge = f'<span class="badge {guide}">{GUIDES[guide]["label"].upper()} {ch}.{num}</span>'
    imgs = ''.join(f'<a class="zoom" href="{full}" target="_blank" rel="noopener" data-local="{loc}"><img loading="lazy" src="{loc}" alt=""></a>'
                   for loc, full in gallery_imgs(s))
    note = f'<div class="cnote"><span class="cnl">Compiler\'s note</span>{refs(NOTES[sid])}</div>' if sid in NOTES else ''
    title = html.unescape(re.sub('<[^>]+>', '', s['title']))
    return (f'<section class="step {guide}" id="s-{sid}"><header><label class="done"><input type="checkbox" data-id="{sid}"><span></span></label>'
            f'{badge}<h3>{html.escape(title)}</h3><a class="orig" href="{url}" target="_blank" rel="noopener" title="Open original step">↗</a></header>'
            f'{note}<div class="body"><div class="text">{render_lines(s["lines"])}</div><div class="gal">{imgs}</div></div>'
            f'{comments_block(step_comments(sid), url)}</section>'), title


def chapter_title(slug):
    return bundle(slug)['guide']['title']


# ---------------------------------------------------------------- assemble
def segments_of(items):
    """(guide, chapter, first_num, last_num) runs of consecutive steps in a list of resolved items."""
    segs = []
    for it in items:
        if isinstance(it, tuple) and it[0] == 'step':
            _, g, ch, n, _, _ = it
            if segs and segs[-1][0] == g and segs[-1][1] == ch and segs[-1][3] + 1 == n:
                segs[-1][3] = n
            else:
                segs.append([g, ch, n, n])
    return [tuple(s) for s in segs]


# group items into phases and roadmap rows
phases, rows = [], []
for it in R.items:
    if isinstance(it, Phase):
        phases.append([it.title, []])
    elif isinstance(it, Row):
        rows.append([it.description, []])
    else:
        phases[-1][1].append(it)
        rows[-1][1].append(it)

body, toc = [], []
n_steps = n_art = 0
for pi, (ptitle, items) in enumerate(phases):
    has_art = any(it[0] == 'article' for it in items)
    psub = ('Article · ' if has_art else '') + ranges_label(segments_of(items), R, prefix_guides=True)
    body.append(f'<h2 class="phase" id="ph-{pi}"><span>{html.escape(ptitle)}</span><small>{psub}</small></h2>')
    entries = []
    prev = None
    for k, it in enumerate(items):
        if it[0] == 'article':
            _, sec, t, h = it
            aid = ARTICLE_SECTIONS[sec]
            body.append(f'<section class="step article" id="{aid}"><header><label class="done"><input type="checkbox" data-id="{aid}"><span></span></label>'
                        f'<span class="badge article">ARTICLE</span><h3>{html.escape(t)}</h3>'
                        f'<a class="orig" href="{ARTICLE["url"]}" target="_blank" rel="noopener" title="Open original article">↗</a></header>'
                        f'<div class="arttext">{clean_article_html(h)}</div>{article_comments_block(sec)}</section>')
            entries.append((aid, t, 'article', 'Article'))
            n_art += 1
            prev = None
            continue
        _, g, ch, n, slug, s = it
        if prev != (g, ch, n - 1):     # start of a run of steps: show a segment marker
            _, _, a, b = segments_of(items[k:])[0]
            span = f'steps {a}–{b}' if a != b else f'step {a}'
            body.append(f'<div class="segmark {g}">{GUIDES[g]["label"]} guide · {html.escape(chapter_title(slug))} · {span}</div>')
        h, title = step_html(g, ch, n, slug, s)
        body.append(h)
        entries.append((f's-{s["id"]}', title, g, f'{"INDX" if g == "indx" else "G2"} {ch}.{n}'))
        n_steps += 1
        prev = (g, ch, n)
    toc.append((ptitle, pi, entries))

intro_html, _ = article_sections()
art_intro_html = clean_article_html(intro_html)

# counts
tot_c = kept_c = 0
for it in R.items:
    if isinstance(it, tuple) and it[0] == 'step':
        raw = step_comments(it[5]['id'])
        tot_c += sum(1 for _ in walk_comments(raw))
        kept_c += sum(1 for c in walk(prune(raw)) if is_useful(c))
tot_c += sum(1 for _ in walk_comments(ART_COMMENTS))
kept_c += sum(1 for c in walk_comments(ART_COMMENTS) if c['id'] in ARTICLE_COMMENTS)

# roadmap
roadmap = ''
for desc, items in rows:
    arts = [it for it in items if it[0] == 'article']
    guides = []
    for it in items:
        if it[0] == 'step' and it[1] not in guides:
            guides.append(it[1])
    first = items[0]
    anchor = ARTICLE_SECTIONS[first[1]] if first[0] == 'article' else f's-{first[5]["id"]}'
    if not guides:       # article-only row
        badge, cls = 'Article', 'article'
        label = '“' + arts[0][2] + '”'
    elif len(guides) == 1:
        badge, cls = GUIDES[guides[0]]['label'], guides[0]
        label = ranges_label(segments_of(items), R, prefix_guides=False)
    else:
        badge, cls = ' + '.join(GUIDES[g]['label'] for g in guides), 'mixed'
        label = ranges_label(segments_of(items), R, prefix_guides=True)
    roadmap += (f'<tr><td><span class="badge {cls}">{badge}</span></td>'
                f'<td><a href="#{anchor}">{html.escape(label)}</a></td><td>{refs(desc)}</td></tr>')

toc_html = ''
for ptitle, pi, items in toc:
    lis = ''.join(f'<li><a href="#{a}" data-t="{a}"><span class="tb {src}">{lab}</span>{html.escape(t)}</a></li>' for a, t, src, lab in items)
    toc_html += (f'<details class="tocp" data-p="{pi}"><summary><a href="#ph-{pi}">{html.escape(ptitle)}</a>'
                 f'<span class="pc" data-p="{pi}"></span></summary><ol>{lis}</ol></details>')

with open(os.path.join(ROOT, 'template.html'), encoding='utf-8') as f:
    tpl = refs(f.read())
page = (tpl.replace('{{TOC}}', toc_html).replace('{{BODY}}', '\n'.join(body)).replace('{{ROADMAP}}', roadmap)
        .replace('{{ART_INTRO}}', art_intro_html).replace('{{NSTEPS}}', str(n_steps + n_art))
        .replace('{{NCOMM}}', str(kept_c)).replace('{{TCOMM}}', str(tot_c)).replace('{{ARTICLE_URL}}', ARTICLE['url'])
        .replace('{{INDX_URL}}', guide_url(GUIDES['indx']['chapters'][1]))
        .replace('{{GEN2_URL}}', guide_url(GUIDES['gen2']['chapters'][1]))
        .replace('{{FETCHED}}', jload(os.path.join(DATA, 'meta.json'))['fetched_label']))
if ref_errors:
    sys.exit('Reference errors:\n  ' + '\n  '.join(sorted(set(ref_errors))))
os.makedirs(IMG, exist_ok=True)
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(page)
print(f'steps {n_steps}, article sections {n_art}, comments shown {kept_c} of {tot_c}, images {len(downloads)}')

# ---------------------------------------------------------------- images
if '--noimg' not in sys.argv:
    def dl(item):
        url, path = item
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return 0
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=120).read()
        with open(path, 'wb') as f:
            f.write(data)
        return len(data)
    with cf.ThreadPoolExecutor(8) as ex:
        sizes = list(ex.map(dl, downloads.items()))
    print(f'downloaded {sum(1 for s in sizes if s)} new images ({sum(sizes) // 1024} KB)')
if '--prune' in sys.argv:
    used = {os.path.basename(p) for p in downloads.values()}
    stale = [f for f in os.listdir(IMG) if f not in used]
    for f in stale:
        os.remove(os.path.join(IMG, f))
    print(f'pruned {len(stale)} unused images')
