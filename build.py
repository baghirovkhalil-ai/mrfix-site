#!/usr/bin/env python3
"""
Mr.Fix statik sayt generatoru.
  python3 build.py              -> _site/ qovluğuna yığır (GitHub Pages üçün)
  python3 build.py --explicit   -> linklər .../index.html formasında (faylı birbaşa açmaq üçün)
Məzmun: content/ qovluğu. Dizayn: static/ qovluğu.
"""
import json, os, re, shutil, sys, html, math, datetime, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "_site")
EXPLICIT = "--explicit" in sys.argv
C = lambda f: json.load(open(os.path.join(BASE, "content", f), encoding="utf-8"))

SITE = C("site.json"); PRODUCTS = C("products.json"); CATS = C("categories.json")
SYSTEMS = C("systems.json"); GROUTS = C("grouts.json"); REFS = C("references.json")
DEALERS = C("dealers.json"); NEWS = C("news.json")
CAT = {c["id"]: c for c in CATS}
BY_NAME = {p["name"]: p for p in PRODUCTS}
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
for c in CATS: c["count"] = sum(1 for p in PRODUCTS if p["cat"] == c["id"])
e = lambda s: html.escape(str(s), quote=True)
MONTHS = ["yanvar","fevral","mart","aprel","may","iyun","iyul","avqust","sentyabr","oktyabr","noyabr","dekabr"]
def dt(s):
    d = datetime.date.fromisoformat(str(s)); return f"{d.day} {MONTHS[d.month-1]} {d.year}"


# ---------- Minimal Markdown (yalnız standart kitabxana) ----------
def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t

def md_to_html(src):
    lines = src.strip("\n").split("\n"); out = []; i = 0; n = len(lines)
    while i < n:
        ln = lines[i]
        if not ln.strip(): i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lv = len(m.group(1)); out.append(f"<h{lv}>{_inline(m.group(2).strip())}</h{lv}>"); i += 1; continue
        if ln.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|?\s*:?-{2,}", lines[i+1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln); i += 2; rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i])); i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>")
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", ln):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ol>"); continue
        para = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|\s*[-*]\s+|\s*\d+\.\s+|\s*\|)", lines[i]):
            para.append(lines[i].strip()); i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")
    return "\n".join(out)

# ---------- Blog ----------
POSTS = []
for fn in sorted(os.listdir(os.path.join(BASE, "content", "blog"))):
    if not fn.endswith(".md"): continue
    raw = open(os.path.join(BASE, "content", "blog", fn), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":"); meta[k.strip()] = v.strip()
    body = m.group(2)
    POSTS.append(dict(slug=fn[:-3], title=meta.get("title",""), date=meta.get("date",""), category=meta.get("category","Bələdçi"),
        excerpt=meta.get("excerpt",""), products=[x.strip() for x in meta.get("products","").split(",") if x.strip()],
        html=md_to_html(body), minutes=max(2, round(len(body.split())/180))))
POSTS.sort(key=lambda p: p["date"], reverse=True)

# ---------- Icons ----------
def ic(path, sw="2"):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'
I = dict(
 search=ic('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>'),
 menu=ic('<path d="M4 7h16M4 12h16M4 17h16"/>'),
 close=ic('<path d="M6 6l12 12M18 6L6 18"/>'),
 arrow='<span class="arrow" aria-hidden="true">→</span>',
 chev=ic('<path d="M6 9l6 6 6-6"/>').replace("<svg ", '<svg class="chev" '),
 phone=ic('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>'),
 mail=ic('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'),
 pin=ic('<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
 chat=ic('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>'),
 send=ic('<path d="M4 12l16-8-6 16-2-7-8-1z"/>'),
 check=ic('<path d="M5 12.5l4.5 4.5L19 7"/>', "2.4"),
 doc=ic('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>'),
 down=ic('<path d="M12 4v12M6 11l6 6 6-6M5 20h14"/>'),
 wa=ic('<path d="M3 21l1.7-5A9 9 0 1 1 8 19.3z"/><path d="M9 9.5c.5 2.5 2.5 4.5 5 5l1.2-1.2 2 1-.5 1.7c-4 .3-8.5-4.2-8.2-8.2l1.7-.5 1 2z"/>', "1.6"),
 ig=ic('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>'),
 fb=ic('<path d="M15 3h-2.5A3.5 3.5 0 0 0 9 6.5V9H7v3.5h2V21h3.5v-8.5H15l.5-3.5h-3V7a1 1 0 0 1 1-1H15z"/>'),
 yt=ic('<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9l5 3-5 3z" fill="currentColor"/>'),
 shield=ic('<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>'),
 globe=ic('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'),
 flask=ic('<path d="M9 3h6M10 3v6L4.5 18.5A2 2 0 0 0 6.2 21.5h11.6a2 2 0 0 0 1.7-3L14 9V3"/><path d="M7 15h10"/>'),
 calc=ic('<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h4"/>'),
)

# ---------- URL helper ----------
def L(root, p=""):
    return root + p

def pack(p, root, kg=True):
    c = CAT[p["cat"]]["color"]
    img = p["image"]
    local = os.path.join(BASE, "static", "img", "products", p["slug"] + ".png")
    if os.path.exists(local): img = root + "img/products/" + p["slug"] + ".png"
    nm = p["name"].replace("®", "").split()
    line = nm[0]; rest = " ".join(nm[1:])
    std = p.get("standard", "") or p.get("group", "")
    imgtag = f'<img src="{e(img)}" alt="{e(p["name"])}" loading="lazy" decoding="async" onload="this.parentNode.classList.add(\'ok\')" onerror="this.parentNode.classList.add(\'noimg\')">' if img else ""
    return (f'<div class="pack{"" if img else " noimg"}" style="--c:{c}">{imgtag}'
            f'<div class="bag" aria-hidden="true"><div class="bag-top"></div><div class="bag-band"><b>{e(line)}</b><small>{e(rest)}</small></div>'
            f'<div class="bag-body"><img class="bag-logo" src="{root}assets/logo.svg" alt=""><span class="bag-std">{e(std)}</span>{"<span class=bag-kg>25 kq</span>" if kg and any("25 kq" in v for _, v in p.get("tech", [])) else ""}</div></div></div>')

def prod_card(p, root, cls="rv"):
    c = CAT[p["cat"]]
    keys = " ".join([p["name"], p["short"], p.get("standard",""), p["group"], c["name"]])
    badge = '<span class="badge tag tag-y">Texniki vərəqə</span>' if p.get("featured") else ""
    return (f'<article class="card prod-card {cls}" data-k="{e(keys)}" data-g="{e(p["cat"])} {e(slugify(p["group"]))}">{badge}'
            f'<div class="media">{pack(p, root)}</div><div class="body"><span class="group">{e(p["group"])}</span>'
            f'<h3>{e(p["name"])}</h3><p>{e(p["short"])}</p><div class="foot"><span class="link">Ətraflı {I["arrow"]}</span></div></div>'
            f'<a class="cover" href="{L(root, "mehsul/"+p["slug"]+"/")}" aria-label="{e(p["name"])}"></a></article>')

TR = str.maketrans({"ə":"e","Ə":"e","ı":"i","İ":"i","ö":"o","Ö":"o","ü":"u","Ü":"u","ş":"s","Ş":"s","ç":"c","Ç":"c","ğ":"g","Ğ":"g"})
def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.replace("®"," ").translate(TR).lower()).strip("-")

# ---------- Layout ----------
NAV = [("mehsullar/", "Məhsullar", "products"), ("hell-yollari/", "Həll yolları", "solutions"), ("hesablayici/", "Hesablayıcı", "calc"),
       ("referanslar/", "Layihələr", "refs"), ("bloq/", "Bloq", "blog"), ("haqqimizda/", "Haqqımızda", "about"), ("elaqe/", "Əlaqə", "contact")]

def header(root, active):
    ct = SITE["contact"]
    mega = "".join(f'<a href="{L(root,"mehsullar/"+c["slug"]+"/")}"><i class="mega-dot" style="background:{c["color"]}"></i><span><b>{e(c["name"])}</b><span>{c["count"]} məhsul</span></span></a>' for c in CATS[:9])
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        if key == "products":
            items.append(f'<li class="has-mega"><button class="nav-link" type="button" aria-expanded="false"{cur}>{label} {I["chev"]}</button><div class="mega"><div class="mega-in">{mega}'
                         f'<div class="mega-foot"><a class="link" href="{L(root,"mehsullar/")}">Bütün {len(PRODUCTS)} məhsul {I["arrow"]}</a><a class="link" href="{L(root,"senedler/")}">Texniki sənədlər {I["arrow"]}</a><a class="link" href="{L(root,"reng-secimi/")}">Dərz rəngləri {I["arrow"]}</a></div></div></div></li>')
        else:
            items.append(f'<li><a class="nav-link" href="{L(root,href)}"{cur}>{label}</a></li>')
    drawer = "".join(f'<a href="{L(root,h)}">{l} <small>→</small></a>' for h, l, k in NAV) + f'<a href="{L(root,"dilerler/")}">Dilerlər <small>→</small></a><a href="{L(root,"reng-secimi/")}">Dərz rəngləri <small>→</small></a><a href="{L(root,"senedler/")}">Texniki sənədlər <small>→</small></a>'
    return f'''<a class="skip" href="#main">Məzmuna keç</a>
<div class="topbar"><div class="wrap"><span class="hide-sm">{e(SITE["tagline"])} · ISO 9001</span><div class="row"><a href="tel:{ct["phones"][0].replace(" ","")}">{e(ct["phones"][0])}</a><a class="hide-sm" href="mailto:{ct["email"]}">{ct["email"]}</a><a href="{L(root,"dilerler/")}">Diler tap</a></div></div></div>
<header class="header"><div class="wrap">
<a class="logo" href="{L(root)}" aria-label="Mr.Fix ana səhifə"><img src="{root}assets/logo.svg" alt="mr.fix" width="114" height="34"></a>
<nav aria-label="Əsas menyu"><ul class="nav">{"".join(items)}</ul></nav>
<div class="header-actions">
<button class="icon-btn" type="button" data-search-open aria-label="Axtarış (Ctrl+K)">{I["search"]}</button>
<a class="btn btn-yellow btn-sm btn-cta" href="{L(root,"dilerler/")}">Diler tap</a>
<button class="icon-btn burger" type="button" data-drawer-open aria-label="Menyu">{I["menu"]}</button>
</div></div></header>
<div class="drawer" id="drawer" aria-hidden="true"><div class="drawer-bg" data-drawer-close></div><div class="drawer-panel" role="dialog" aria-label="Menyu">
<div class="drawer-head"><img src="{root}assets/logo.svg" alt="mr.fix" width="94" height="28" style="height:28px;width:auto"><button class="icon-btn drawer-close" type="button" data-drawer-close aria-label="Bağla">{I["close"]}</button></div>
<nav>{drawer}</nav><div class="drawer-cta"><a class="btn btn-yellow" href="{L(root,"dilerler/")}">Diler tap</a><a class="btn btn-ghost" href="tel:{ct["phones"][0].replace(" ","")}">{e(ct["phones"][0])}</a></div></div></div>'''

def footer(root):
    ct = SITE["contact"]; so = SITE["social"]
    cats = "".join(f'<li><a href="{L(root,"mehsullar/"+c["slug"]+"/")}">{e(c["name"])}</a></li>' for c in CATS[:6])
    return f'''<footer class="footer"><div class="wrap">
<div class="footer-grid">
<div class="brand"><img src="{root}assets/logo-white.svg" alt="mr.fix" width="140" height="35" style="height:34px;width:auto"><p>{e(SITE["company"])} — 2000-ci ildən Azərbaycanda tikinti kimyəviləri istehsalı. ISO 9001, Avropa EN standartlarına uyğun.</p>
<div class="social"><a href="{so["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram">{I["ig"]}</a><a href="{so["facebook"]}" target="_blank" rel="noopener" aria-label="Facebook">{I["fb"]}</a><a href="{so["youtube"]}" target="_blank" rel="noopener" aria-label="YouTube">{I["yt"]}</a></div></div>
<div><h4>Məhsullar</h4><ul>{cats}<li><a href="{L(root,"mehsullar/")}">Bütün məhsullar</a></li></ul></div>
<div><h4>Şirkət</h4><ul><li><a href="{L(root,"haqqimizda/")}">Haqqımızda</a></li><li><a href="{L(root,"referanslar/")}">Layihələr</a></li><li><a href="{L(root,"xeberler/")}">Xəbərlər</a></li><li><a href="{L(root,"bloq/")}">Bloq</a></li><li><a href="{L(root,"karyera/")}">Karyera</a></li><li><a href="{L(root,"dilerler/")}">Dilerlər</a></li></ul></div>
<div><h4>Əlaqə</h4><ul><li>{e(ct["address"])}</li><li><a href="tel:{ct["phones"][0].replace(" ","")}">{e(ct["phones"][0])}</a></li><li><a href="tel:{ct["phones"][1].replace(" ","")}">{e(ct["phones"][1])}</a></li><li><a href="mailto:{ct["email"]}">{ct["email"]}</a></li><li>{e(ct["hours"])}</li></ul></div>
</div>
<div class="footer-mark" aria-hidden="true"><img src="{root}assets/logo-white.svg" alt=""></div>
<div class="footer-bottom"><span>© {datetime.date.today().year} {e(SITE["name"])} · {e(SITE["company"])}. Bütün hüquqlar qorunur.</span><span><a href="{L(root,"senedler/")}">Texniki sənədlər</a> · <a href="{L(root,"hesablayici/")}">Hesablayıcı</a> · <a href="{L(root,"reng-secimi/")}">Dərz rəngləri</a></span></div>
</div></footer>
<div class="search-ov" id="search" aria-hidden="true"><div class="bgx" data-search-close></div><div class="search-box" role="dialog" aria-label="Axtarış">
<div class="top">{I["search"]}<label class="sr" for="searchInput">Axtarış</label><input id="searchInput" type="search" placeholder="Məhsul, standart, səth və ya məqalə…" autocomplete="off"><span class="kbd">Esc</span></div>
<div class="search-res" id="searchRes"></div></div></div>
<button class="fab" type="button" data-helper-open aria-controls="helper"><span class="pulse"></span><i>{I["chat"]}</i><span class="lbl">Məhsul köməkçisi</span></button>
<div class="helper" id="helper" role="dialog" aria-label="Məhsul köməkçisi" hidden>
<div class="helper-head"><span class="av"><img src="{root}assets/icon.svg" alt=""></span><div><b>Məhsul köməkçisi</b><small>Səth və ya problem yazın</small></div><button type="button" data-helper-close aria-label="Bağla">{I["close"]}</button></div>
<div class="helper-log" id="helperLog" aria-live="polite"></div>
<form id="helperForm"><label class="sr" for="helperInput">Sualınız</label><input id="helperInput" placeholder="Məs: hamamda su sızır" autocomplete="off"><button type="submit" aria-label="Göndər">{I["send"]}</button></form></div>'''

def fx():
    return '<div class="fx" aria-hidden="true"><div class="fx-glow a"></div><div class="fx-glow b"></div><div class="fx-grid"></div><canvas></canvas></div>'

def page_hero(root, crumbs, title, lede="", extra=""):
    cr = f'<a href="{L(root)}">Ana səhifə</a>' + "".join(f'<span aria-hidden="true">/</span>' + (f'<a href="{L(root,h)}">{e(t)}</a>' if h else f'<span>{e(t)}</span>') for h, t in crumbs)
    return f'<section class="page-hero">{fx()}<div class="wrap"><nav class="crumbs" aria-label="Səhifə yolu">{cr}</nav><h1 class="split">{e(title)}</h1>{f"<p class=lede>{lede}</p>" if lede else ""}{extra}</div></section>'

def cta(root):
    return f'''<section class="section-sm"><div class="wrap"><div class="cta-band rv"><div class="tiles" aria-hidden="true">{"<i></i>"*16}</div>
<div><span class="eyebrow">Texniki dəstək</span><h2 style="margin-top:14px">Layihəniz üçün düzgün sistemi birlikdə seçək.</h2><p>Mütəxəssisimiz səthə, yükə və şəraitə uyğun məhsulları və miqdarı təklif edəcək.</p></div>
<div class="actions"><a class="btn btn-yellow" href="https://wa.me/{SITE["contact"]["whatsapp"]}?text={e("Salam! Saytdan yazıram, texniki məsləhət lazımdır.")}" target="_blank" rel="noopener">{I["wa"]} WhatsApp ilə yaz</a><a class="btn btn-ghost" href="{L(root,"dilerler/")}">Ən yaxın diler</a></div></div></div></section>'''

_A = lambda f: os.path.exists(os.path.join(BASE, "static", "assets", f))
OG = f'<meta property="og:image" content="{SITE["url"]}/assets/og.png">' if _A("og.png") else ""
APPLE = lambda root: (f'<link rel="icon" href="{root}assets/favicon-32.png" sizes="32x32">' if _A("favicon-32.png") else "") + (f'<link rel="apple-touch-icon" href="{root}assets/icon-512.png">' if _A("icon-512.png") else "")
PAGES = []
def page(path, title, desc, body, active=None, tools=False, jsonld=None, progress=False, full_title=False):
    depth = path.count("/")
    root = "../" * depth if depth else "./"
    t = title if full_title else f"{title} | Mr.Fix"
    canon = SITE["url"].rstrip("/") + "/" + (path[:-10] if path.endswith("index.html") else path)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    doc = f'''<!doctype html>
<html lang="az">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(t)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(t)}"><meta property="og:description" content="{e(desc)}">{OG}<meta property="og:locale" content="az_AZ">
<meta name="theme-color" content="#EA5B5F">
<link rel="icon" href="{root}assets/icon.svg" type="image/svg+xml">{APPLE(root)}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap">
<link rel="stylesheet" href="{root}css/site.css">
{ld}
</head>
<body data-root="{root}" data-wa="{SITE["contact"]["whatsapp"]}">
{'<div class="progress" aria-hidden="true"></div>' if progress else ""}
{header(root, active)}
<main id="main">
{body(root)}
</main>
{footer(root)}
<script src="{root}js/site.js" defer></script>
{f'<script src="{root}js/tools.js" defer></script>' if tools else ""}
</body>
</html>
'''
    PAGES.append((path, doc))

# =============== HOME ===============
def home(root):
    hero_p = [BY_NAME["FUGAMAX® COLORFUL"], BY_NAME["CERAMAX® FLEX"], BY_NAME["IZOMAX® C 40"]]
    latest = NEWS[0]
    rot = "".join(f"<span>{w}</span>" for w in ["Hamam", "Teras", "Hovuz", "Fasad", "Zirzəmi", "Döşəmə"])
    stats = SITE["stats"][:3] + [{"value": sum(len(v) for v in DEALERS.values()), "suffix": "+", "label": "diler və satış nöqtəsi"}]
    stats[2] = {"value": len(PRODUCTS), "suffix": "", "label": "məhsul çeşidi"}
    st = "".join(f'<div class="stat rv rv-d{i}"><b><span data-count="{s["value"]}">{s["value"]}</span><sup>{s["suffix"]}</sup></b><span>{e(s["label"])}</span></div>' for i, s in enumerate(stats))
    marq = "".join(f"<span>{e(r['name'])}</span>" for r in REFS[:16])
    main_cats = CATS[:6]
    cats = "".join(f'''<article class="card cat-card rv rv-d{i%3}" style="--c:{c["color"]}"><span class="num">0{i+1} · {c["count"]} məhsul</span><h3>{e(c["name"])}</h3><p>{e(c["desc"])}</p><span class="link">Kateqoriyaya bax {I["arrow"]}</span>
<div class="mini" aria-hidden="true">{pack(next(p for p in PRODUCTS if p["cat"]==c["id"] and p.get("featured")) if any(p["cat"]==c["id"] and p.get("featured") for p in PRODUCTS) else next(p for p in PRODUCTS if p["cat"]==c["id"]), root, False)}</div>
<a class="cover" href="{L(root,"mehsullar/"+c["slug"]+"/")}" aria-label="{e(c["name"])}"></a></article>''' for i, c in enumerate(main_cats))
    sols = "".join(sol_card(s, root, i) for i, s in enumerate(SYSTEMS[:6]))
    feat = [BY_NAME[n] for n in ["CERAMAX® FLEX", "CERAMAX® Maxi", "FUGAMAX® FLEX", "IZOMAX® C60 N", "IZOMAX® F-tec", "TAMCRETE® CRM 100", "THERMOMAX® EPS CARBON", "FLOMAX® SL 212"]]
    prods = "".join(prod_card(p, root) for p in feat)
    refs = "".join(ref_card(r, 0, root) for r in REFS[15:21])
    posts = "".join(post_card(p, root) for p in POSTS[:3])
    tiles = "".join('<i style="background:#F6F5F1"></i>' for _ in range(16))
    return f'''
<section class="hero">{fx()}<div class="wrap">
<div>
<a class="hero-badge" href="{L(root,"xeberler/"+latest["slug"]+"/")}"><b>YENİ</b>{e(latest["title"])} →</a>
<h1><span class="rotator" aria-label="Hamam, teras, hovuz, fasad, zirzəmi, döşəmə">{rot}</span><br>üçün düzgün formul.</h1>
<p class="lede">Kafel yapışdırıcısından su izolyasiyasına qədər {len(PRODUCTS)} tikinti kimyəvisi. 2000-ci ildən Azərbaycanda istehsal, Avropa EN standartlarına uyğun.</p>
<div class="hero-cta"><a class="btn btn-yellow" href="{L(root,"hell-yollari/")}">Sistemimi seç {I["arrow"]}</a><a class="btn btn-ghost" href="{L(root,"mehsullar/")}">Məhsullara bax</a></div>
<div class="hero-trust"><span>{I["shield"]} ISO 9001</span><span>{I["flask"]} Laboratoriya nəzarəti</span><span>{I["globe"]} 5 ölkədə satış</span></div>
</div>
<div class="stage" aria-hidden="true"><div class="stage-ring"></div><div class="stage-ring r2"></div>
<div class="stage-item">{pack(hero_p[1], root)}</div><div class="stage-item">{pack(hero_p[0], root)}</div><div class="stage-item">{pack(hero_p[2], root)}</div>
<div class="stage-chip c1"><i>S1</i><div><b>C2TE S1</b><span>Elastik yapışdırıcı</span></div></div>
<div class="stage-chip c2"><i>4</i><div><b>4 bar</b><span>Su təzyiqinə davamlı</span></div></div>
</div></div></section>

<section class="section-sm" style="border-bottom:1px solid var(--line)"><div class="wrap"><div class="row between" style="margin-bottom:18px"><span class="eyebrow">Etibar edilən layihələr</span><a class="link" href="{L(root,"referanslar/")}">Bütün layihələr {I["arrow"]}</a></div>
<div class="marquee"><div class="marquee-track">{marq}{marq}</div></div></div></section>

<section class="section"><div class="wrap">
<div class="head-row"><div class="head"><span class="eyebrow">Mr.Fix rəqəmlərlə</span><h2 class="h2 split">Çeyrək əsrlik istehsal təcrübəsi</h2></div><p class="lede" style="max-width:46ch">Bakıdakı tam avtomatlaşdırılmış zavodda istehsal olunan hər partiya keyfiyyətə nəzarət laboratoriyasında yoxlanılır.</p></div>
<div class="stats">{st}</div></div></section>

<section class="section bg-soft"><div class="wrap">
<div class="head-row"><div class="head"><span class="eyebrow">Məhsul kataloqu</span><h2 class="h2 split">Hər tikinti mərhələsi üçün</h2></div><a class="btn btn-white" href="{L(root,"mehsullar/")}">Bütün {len(CATS)} kateqoriya {I["arrow"]}</a></div>
<div class="grid g3">{cats}</div></div></section>

<section class="section"><div class="wrap">
<div class="head-row"><div class="head"><span class="eyebrow">Həll yolları</span><h2 class="h2 split">Səthi seçin, sistemi biz verək</h2><p class="lede">Hər həll alt qatdan üst qata qədər məhsul ardıcıllığı və addım-addım tətbiq qaydası ilə.</p></div><a class="btn btn-white" href="{L(root,"hell-yollari/")}">Bütün həllər {I["arrow"]}</a></div>
<div class="grid g3">{sols}</div></div></section>

<section class="section bg-soft"><div class="wrap">
<div class="head-row"><div class="head"><span class="eyebrow">Seçilmiş məhsullar</span><h2 class="h2 split">Ustaların ən çox seçdikləri</h2></div><a class="btn btn-white" href="{L(root,"mehsullar/")}">Kataloq {I["arrow"]}</a></div>
<div class="grid g4">{prods}</div></div></section>

<section class="section"><div class="wrap"><div class="grid g2">
<article class="card rv" style="padding:clamp(24px,3vw,40px);display:grid;gap:16px;background:var(--navy);color:var(--on-navy);border-color:var(--navy)"><span class="eyebrow">Hesablayıcı</span><h3 class="h3" style="font-size:clamp(24px,2.6vw,34px)">Nə qədər material lazımdır?</h3><p style="color:var(--on-navy-2)">Dərz, yapışdırıcı, su izolyasiyası və şap üçün sərfiyyatı saniyələr içində hesablayın, sifarişi birbaşa göndərin.</p>
<div class="row" style="gap:8px;margin-top:6px"><span class="tag tag-navy">kq/m²</span><span class="tag tag-navy">kisə sayı</span><span class="tag tag-navy">WhatsApp sifariş</span></div><span class="link" style="color:#fff;margin-top:auto">Hesablamağa başla {I["arrow"]}</span><a class="cover" href="{L(root,"hesablayici/")}" aria-label="Hesablayıcı"></a></article>
<article class="card rv rv-d1" style="padding:clamp(24px,3vw,40px);display:grid;gap:16px;grid-template-columns:minmax(0,1fr) 150px;align-items:center"><div style="display:grid;gap:14px"><span class="eyebrow">Dərz rəngləri</span><h3 class="h3" style="font-size:clamp(24px,2.6vw,34px)">32 rəngi canlı sınayın</h3><p class="muted">Kafel rəngini və düzülüşünü seçin, dərz rəngini dəyişin, nəticəni dərhal görün.</p><span class="link">Studiyanı aç {I["arrow"]}</span></div>
<div class="tile-mini" aria-hidden="true" style="display:grid;grid-template-columns:repeat(4,1fr);gap:5px;padding:5px;border-radius:12px;background:#B5562F;animation:float 6s ease-in-out infinite">{tiles}</div><a class="cover" href="{L(root,"reng-secimi/")}" aria-label="Dərz rəngləri"></a></article>
</div></div></section>

<section class="section bg-navy"><div class="wrap">
<div class="head-row"><div class="head"><span class="eyebrow">Layihələr</span><h2 class="h2 split">Hava limanından Şuşaya qədər</h2><p class="lede">Heydər Əliyev Mərkəzi, Alov Qüllələri, Qarabağ tunelləri — Mr.Fix məhsulları ölkənin ən məsuliyyətli tikintilərində.</p></div><a class="btn btn-ghost" href="{L(root,"referanslar/")}">{len(REFS)} layihəyə bax {I["arrow"]}</a></div>
<div class="grid g3">{refs}</div></div></section>

<section class="section"><div class="wrap">
<div class="head-row"><div class="head"><span class="eyebrow">Bloq</span><h2 class="h2 split">Ustalar və layihəçilər üçün bələdçilər</h2></div><a class="btn btn-white" href="{L(root,"bloq/")}">Bütün məqalələr {I["arrow"]}</a></div>
<div class="grid g3">{posts}</div></div></section>
{cta(root)}'''

def sol_card(s, root, i=0):
    bars = "".join("<i></i>" for _ in s["layers"])
    return f'''<article class="sol-card rv rv-d{i%3}"><div class="img"><img src="{e(s["image"])}" alt="" loading="lazy" onerror="this.remove()"></div>
<div class="in"><span class="tag tag-y" style="width:max-content">{len(s["layers"])} qatlı sistem</span><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p><div class="layers-mini" aria-hidden="true">{bars}</div></div>
<a class="cover" href="{L(root,"hell-yollari/"+s["id"]+"/")}" aria-label="{e(s["name"])}"></a></article>'''

def ref_slug(r):
    return r.get("slug") or slugify(r["name"])

def ref_card(r, i=0, root="./"):
    link = f'<a class="cover" href="{L(root, "referanslar/" + ref_slug(r) + "/")}" aria-label="{e(r["name"])}"></a>' if r.get("products") is not None else ""
    n = len([x for x in r.get("products", []) if x.get("slug")])
    pc = f'<span class="ref-n">{n} məhsul</span>' if n else ""
    return f'''<article class="ref-card rv" data-k="{e(r["name"]+" "+r["place"]+" "+r["type"]+" "+" ".join(x["name"] for x in r.get("products", [])))}" data-g="{e(slugify(r["type"]))}"><img src="{e(r["image"])}" alt="{e(r["name"])}" loading="lazy" onerror="this.parentNode.classList.add('noimg')">
<div class="in"><span class="meta">{e(r["type"])} · {e(r["place"])}{" · "+r["year"] if r["year"] else ""}</span><h3>{e(r["name"])}</h3>{pc}</div>{link}</article>'''

def ref_page(r):
    root = "../../"
    ps = r.get("products", [])
    linked = [BY_SLUG[x["slug"]] for x in ps if x.get("slug") in BY_SLUG]
    other = [x["name"] for x in ps if x.get("slug") not in BY_SLUG]
    meta = " · ".join(x for x in (r["type"], r["place"], r.get("year")) if x)
    hero = f'''<section class="page-hero ref-hero"><div class="fx" aria-hidden="true"><img src="{e(r["image"])}" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.32" onerror="this.remove()"><div class="fx-grid"></div></div>
<div class="wrap"><nav class="crumbs" aria-label="Səhifə yolu"><a href="{root}">Ana səhifə</a><span aria-hidden="true">/</span><a href="{L(root,"referanslar/")}">Layihələr</a><span aria-hidden="true">/</span><span>{e(r["name"])}</span></nav>
<span class="tag tag-y">{e(meta)}</span><h1 class="split" style="margin-top:18px">{e(r["name"])}</h1>{f'<p class="lede">{e(r["desc"])}</p>' if r.get("desc") else ""}</div></section>'''
    body = ""
    if linked:
        wa = "Salam! Saytdan yazıram. \"" + r["name"] + "\" layihəsində istifadə olunan məhsullar haqqında məlumat almaq istəyirəm:\n" + "\n".join(f"{i+1}. {p['name']}" for i, p in enumerate(linked))
        body += f'''<section class="section"><div class="wrap"><div class="head-row"><div class="head"><span class="eyebrow">İstifadə olunan məhsullar</span><h2 class="h2" style="font-size:clamp(26px,3vw,36px)">Bu layihədə {len(linked)} Mr.Fix məhsulu</h2></div><a class="btn btn-yellow" href="https://wa.me/{SITE["contact"]["whatsapp"]}?text={e(wa)}" target="_blank" rel="noopener">{I["wa"]} Bu məhsulları soruş</a></div>
<div class="grid g4">{"".join(prod_card(p, root) for p in linked)}</div>{f'<p class="note" style="margin-top:24px">Layihədə həmçinin: {e(", ".join(other))}.</p>' if other else ""}</div></section>'''
    elif other:
        body += f'''<section class="section"><div class="wrap"><span class="eyebrow">İstifadə olunan məhsullar</span><p class="lede" style="margin-top:14px">{e(", ".join(other))}</p></div></section>'''
    rest = [x for x in REFS if x is not r and x.get("products")][:3]
    if rest:
        body += f'''<section class="section-sm bg-soft"><div class="wrap"><div class="head-row"><div class="head"><span class="eyebrow">Digər layihələr</span></div><a class="btn btn-white" href="{L(root,"referanslar/")}">Bütün layihələr {I["arrow"]}</a></div><div class="grid g3">{"".join(ref_card(x, 0, root) for x in rest)}</div></div></section>'''
    return hero + body + cta(root)

def references(root):
    types = []
    for r in REFS:
        if r["type"] not in types: types.append(r["type"])
    chips = '<div class="chips" style="margin-bottom:24px"><button class="chip" type="button" data-g-btn="all" aria-pressed="true">Hamısı</button>' + "".join(f'<button class="chip" type="button" data-g-btn="{slugify(t)}" aria-pressed="false">{e(t)}</button>' for t in types) + "</div>"
    return page_hero(root, [(None, "Layihələr")], "Referans layihələr", f"Heydər Əliyev Mərkəzindən Qarabağın yeni tunellərinə qədər {len(REFS)} layihədə Mr.Fix məhsulları istifadə olunub.") + f'''
<section class="section"><div class="wrap" data-filter="#rlist">{chips}<span class="count" data-count-out style="display:block;margin-bottom:16px"></span><div class="grid g3" id="rlist">{"".join(ref_card(r, 0, root) for r in REFS)}</div></div></section>{cta(root)}'''

# =============== ABOUT ===============
def about(root):
    vals = "".join(f'<div class="card rv rv-d{i}" style="padding:26px;display:grid;gap:10px"><span class="mono" style="color:var(--blue);font-size:13px">0{i+1}</span><h3 class="h3">{e(v["title"])}</h3><p class="muted">{e(v["text"])}</p></div>' for i, v in enumerate(SITE["values"]))
    tl = [("2000","Kartaş MMC yaradıldı","Mr.Fix brendi ilə tikinti kimyəviləri istehsalına başlandı."),("2012","Heydər Əliyev Mərkəzi","Ölkənin simvol binalarından birində Mr.Fix məhsulları istifadə olundu."),("2013","Alov Qüllələri","Bakının yeni siluetinin tikintisində iştirak."),("2021","Qarabağın bərpası","Şuşa, Zəngilan və Murovdağ layihələri."),("2023","Tunel layihələri","Kəlbəcər–Laçın, Qubadlı–Laçın, Cəbrayıl–Zəngilan–Ağbənd tunelləri."),("2026","Yeni ixrac bazarları","Qırğızıstan və Gürcüstana ixrac; direktor Necmeddin Taşbağ Tərəqqi medalı ilə təltif olundu.")]
    tlh = "".join(f'<li class="rv"><span class="y">{y}</span><span class="d"></span><div><b>{e(t)}</b><p>{e(d)}</p></div></li>' for y, t, d in tl)
    ex = "".join(f'<span class="chip" style="pointer-events:none">{e(x)}</span>' for x in SITE["export"])
    return page_hero(root, [(None, "Haqqımızda")], "25 ildən çox tikinti kimyəviləri təcrübəsi", "Kartaş MMC 2000-ci ildən Mr.Fix brendi ilə Azərbaycanda istehsal edir.") + f'''
<section class="section"><div class="wrap"><div class="grid g2" style="gap:clamp(28px,5vw,72px);align-items:start">
<div class="stack"><span class="eyebrow">Biz kimik</span><h2 class="h2 split">Hər bina insanların rahatlığı və təhlükəsizliyi deməkdir</h2></div>
<div class="stack prose">{"".join(f"<p>{e(x)}</p>" for x in SITE["about"])}</div></div></div></section>
<section class="section bg-soft"><div class="wrap"><div class="head"><span class="eyebrow">Prinsiplərimiz</span><h2 class="h2">Missiya və dəyərlər</h2></div><div class="grid g4">{vals}</div></div></section>
<section class="section"><div class="wrap"><div class="grid g2" style="gap:clamp(28px,5vw,72px);align-items:start">
<div class="stack"><span class="eyebrow">Tarixçə</span><h2 class="h2">Mühüm mərhələlər</h2><p class="lede">Bakıdakı zavoddan beş ölkənin tikinti bazarına.</p><div class="chips" style="margin-top:8px">{ex}</div></div>
<ol class="timeline">{tlh}</ol></div></div></section>{cta(root)}'''

# =============== DEALERS ===============
def dealers(root):
    countries = list(DEALERS.keys())
    chips = '<div class="chips" style="margin-bottom:20px">' + "".join(f'<button class="chip" type="button" data-g-btn="{"all" if i==0 and False else slugify(c)}" aria-pressed="{str(i==0).lower()}">{e(c)} <span class="n">{len(DEALERS[c])}</span></button>' for i, c in enumerate(countries)) + "</div>"
    items = "".join(f'<div class="dealer" data-k="{e(n+" "+a+" "+c)}" data-g="{slugify(c)}"><b>{e(n)}</b><span>{I["pin"].replace("<svg ","<svg style=width:14px;height:14px;vertical-align:-2px;margin-right:4px ")}{e(a)}</span><a href="https://www.google.com/maps/search/?api=1&amp;query={e((n+" "+a).replace(" ","+"))}" target="_blank" rel="noopener">Xəritədə bax →</a></div>' for c in countries for n, a in DEALERS[c])
    total = sum(len(v) for v in DEALERS.values())
    return page_hero(root, [(None, "Dilerlər")], "Diler şəbəkəsi", f"{len(countries)} ölkədə {total} diler və satış nöqtəsi. Ad, küçə və ya qəsəbə üzrə axtarın.") + f'''
<section class="section-sm"><div class="wrap" data-filter="#dlist"><div class="toolbar"><div class="search-field">{I["search"]}<label class="sr" for="dsearch">Diler axtar</label><input id="dsearch" type="search" placeholder="Məs: Mərdəkan, Sədərək, Gəncə…"></div><span class="count" data-count-out></span></div>{chips}
<div class="grid g3" id="dlist" style="gap:12px">{items}</div><p class="empty" data-empty hidden>Bu axtarışa uyğun diler tapılmadı. Baş ofisə zəng edin: {e(SITE["contact"]["phones"][0])}</p></div></section>
<script>document.addEventListener("DOMContentLoaded",function(){{var b=document.querySelector('[data-g-btn="azerbaycan"]');b&&b.click();}});</script>
<section class="section-sm"><div class="wrap"><div class="card" style="padding:clamp(22px,3vw,36px);display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));align-items:center"><div class="stack"><span class="eyebrow">Diler olmaq istəyirsiniz?</span><h2 class="h3" style="font-size:clamp(22px,2.4vw,30px)">Mr.Fix şəbəkəsinə qoşulun</h2><p class="muted">Tikinti materialları mağazanız və ya distribyutor şirkətiniz varsa, bizimlə əlaqə saxlayın.</p></div><div class="row" style="justify-content:flex-end"><a class="btn btn-yellow" href="https://wa.me/{SITE["contact"]["whatsapp"]}?text={e("Salam! Mr.Fix dileri olmaq istəyirəm.")}" target="_blank" rel="noopener">{I["wa"]} Müraciət et</a><a class="btn btn-ghost" href="mailto:{SITE["contact"]["email"]}">{SITE["contact"]["email"]}</a></div></div></div></section>'''

# =============== DOCUMENTS ===============
def documents(root):
    def dl(url, label):
        return f'<a href="{e(url)}" target="_blank" rel="noopener">{label} ↓</a>' if url else "—"
    rows = "".join(f'<tr data-k="{e(p["name"]+" "+CAT[p["cat"]]["name"]+" "+p.get("standard",""))}" data-g="{p["cat"]}"><th scope="row"><a href="{L(root,"mehsul/"+p["slug"]+"/")}">{e(p["name"])}</a></th><td style="font-weight:500;color:var(--muted)">{e(CAT[p["cat"]]["name"])}</td><td><span class="code">{e(p.get("standard",""))}</span></td><td>{dl(p.get("tds"), "TDS")}</td><td>{dl(p.get("sds"), "SDS")}</td></tr>' for p in PRODUCTS if p.get("featured"))
    return page_hero(root, [(None, "Texniki sənədlər")], "Sənəd mərkəzi", "Texniki məlumat (TDS) və təhlükəsizlik (SDS) vərəqələri bir yerdə. Siyahıda olmayan sənəd üçün bizə yazın.") + f'''
<section class="section-sm"><div class="wrap" data-filter="#dtable"><div class="toolbar"><div class="search-field">{I["search"]}<label class="sr" for="docsearch">Sənəd axtar</label><input id="docsearch" type="search" placeholder="Məhsul adı və ya standart…"></div><span class="count" data-count-out></span></div>
<div class="table-box"><table class="spec" style="min-width:720px"><thead><tr style="background:var(--bg)"><th>Məhsul</th><th>Kateqoriya</th><th>Standart</th><th>TDS</th><th>SDS</th></tr></thead><tbody id="dtable">{rows}</tbody></table></div>
<p class="empty" data-empty hidden>Sənəd tapılmadı.</p>
<p style="margin-top:20px"><a class="btn btn-white" href="https://mrfix.az/kataloqlar/" target="_blank" rel="noopener">{I["doc"]} Məhsul kataloqları (PDF)</a></p></div></section>{cta(root)}'''

# =============== CAREER ===============
def career(root):
    car = SITE["career"]
    vals = "".join(f'<div class="card" style="padding:24px;display:grid;gap:8px"><h3 class="h3" style="font-size:20px">{t}</h3><p class="muted">{d}</p></div>' for t, d in [("Qarşılıqlı hörmət","Komandada etimad və açıq ünsiyyət əsasdır."),("İnkişaf","Təlimlər və laboratoriya təcrübəsi ilə peşəkar böyümə."),("Müxtəliflik","Fərqli bacarıq və baxışlara dəyər veririk."),("Motivasiya","Nəticəni görən və dəyərləndirən mühit.")])
    op = "".join(f'<div class="card" style="padding:22px"><h3 class="h3">{e(o["title"])}</h3><p class="muted">{e(o.get("text",""))}</p></div>' for o in car["openings"]) or '<div class="empty">Hazırda açıq vakansiya yoxdur. CV-nizi göndərin — uyğun vəzifə açılanda sizinlə əlaqə saxlayacağıq.</div>'
    return page_hero(root, [(None, "Karyera")], "Komandamızın bir hissəsi olun", e(car["intro"])) + f'''
<section class="section"><div class="wrap"><div class="grid g4">{vals}</div></div></section>
<section class="section-sm bg-soft"><div class="wrap"><div class="head"><span class="eyebrow">Açıq vakansiyalar</span></div>{op}
<div class="row" style="margin-top:24px"><a class="btn btn-yellow" href="mailto:{car["email"]}?subject={e("CV — Mr.Fix")}">{I["mail"]} CV göndər: {car["email"]}</a></div></div></section>'''

# =============== CONTACT ===============
def contact(root):
    ct = SITE["contact"]
    cards = [(I["pin"], "Baş ofis", ct["address"], ct["map"], "Xəritədə aç"), (I["phone"], "Telefon", " · ".join(ct["phones"]), "tel:" + ct["phones"][0].replace(" ", ""), "Zəng et"), (I["mail"], "E-poçt", ct["email"], "mailto:" + ct["email"], "Yaz"), (I["wa"], "WhatsApp", "Texniki məsləhət və sifariş", "https://wa.me/" + ct["whatsapp"], "Yazışmaya başla")]
    ch = "".join(f'<div class="card rv" style="padding:24px;display:grid;gap:10px"><span style="width:44px;height:44px;border-radius:12px;background:var(--bg);display:grid;place-items:center;color:var(--blue)">{i.replace("<svg ","<svg style=width:20px;height:20px ")}</span><span class="mono muted" style="font-size:12px;text-transform:uppercase;letter-spacing:.08em">{t}</span><b style="font-size:16px">{e(v)}</b><a class="link" href="{h}" target="_blank" rel="noopener">{a} {I["arrow"]}</a></div>' for i, t, v, h, a in cards)
    topics = ["Məhsul məlumatı", "Qiymət sorğusu", "Texniki məsləhət", "Diler olmaq", "Digər"]
    return page_hero(root, [(None, "Əlaqə")], "Bizimlə əlaqə", f"{e(ct['hours'])}. Texniki sual, qiymət və ya diler məlumatı üçün yazın.") + f'''
<section class="section-sm"><div class="wrap"><div class="grid g4">{ch}</div></div></section>
<section class="section-sm"><div class="wrap"><div class="grid g2" style="gap:clamp(24px,4vw,48px);align-items:start">
<form class="calc-form" id="contactForm" data-mail="{ct["email"]}"><div class="head" style="margin:0"><span class="eyebrow">Sorğu forması</span><h2 class="h3" style="font-size:28px">Mesaj göndərin</h2></div>
<div class="field"><label for="cf-name">Ad, soyad</label><input class="input" id="cf-name" name="name" required autocomplete="name"></div>
<div class="field"><label for="cf-phone">Telefon</label><input class="input" id="cf-phone" name="phone" type="tel" required autocomplete="tel" placeholder="+994"></div>
<div class="field"><label for="cf-topic">Mövzu</label><select class="select" id="cf-topic" name="topic">{"".join(f"<option>{t}</option>" for t in topics)}</select></div>
<div class="field"><label for="cf-msg">Mesaj</label><textarea class="textarea" id="cf-msg" name="msg" required placeholder="Layihə, sahə, məhsul…"></textarea></div>
<div class="row"><button class="btn btn-yellow" type="submit" value="wa">{I["wa"]} WhatsApp ilə göndər</button><button class="btn btn-ghost" type="submit" value="mail">{I["mail"]} E-poçt ilə</button></div>
<p id="formOk" class="note" hidden>Mesajınız WhatsApp və ya e-poçt proqramında hazırlandı. Göndər düyməsini basmağı unutmayın.</p></form>
<div class="card" style="min-height:440px;overflow:hidden;border-radius:var(--r-xl)"><iframe title="Mr.Fix baş ofis xəritəsi" src="https://www.google.com/maps?q={e(ct["address"].replace(" ","+"))}&amp;output=embed" style="border:0;width:100%;height:100%;min-height:440px" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
</div></div></section>'''

# =============== 404 ===============
def nf(root):
    return f'<section class="page-hero" style="min-height:70vh;display:grid;align-items:center">{fx()}<div class="wrap"><span class="eyebrow">Xəta 404</span><h1 style="margin-top:18px">Bu səhifə tapılmadı</h1><p class="lede" style="margin-top:16px">Ünvan dəyişmiş ola bilər. Axtarışdan istifadə edin və ya ana səhifəyə qayıdın.</p><div class="row" style="margin-top:28px"><a class="btn btn-yellow" href="{root}">Ana səhifə</a><button class="btn btn-ghost" type="button" data-search-open>Axtar</button></div></div></section>'

# =============== BUILD ===============
ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "Mr.Fix", "legalName": SITE["company"], "url": SITE["url"], "logo": SITE["url"] + "/assets/logo.svg",
       "address": {"@type": "PostalAddress", "streetAddress": "Xətai prospekti 43", "addressLocality": "Bakı", "addressCountry": "AZ"},
       "telephone": SITE["contact"]["phones"][0], "email": SITE["contact"]["email"], "sameAs": list(SITE["social"].values()), "foundingDate": "2000"}
page("index.html", "Mr.Fix — Tikinti kimyəviləri | Kafel yapışdırıcısı, dərz, su izolyasiyası", "Mr.Fix: 2000-ci ildən Azərbaycanda istehsal olunan kafel yapışdırıcıları, dərz dolğuları, su və istilik izolyasiyası, təmir və zəmin materialları.", home, "home", jsonld=ORG, full_title=True)
page("mehsullar/index.html", "Məhsullar", f"Mr.Fix məhsul kataloqu: {len(PRODUCTS)} tikinti kimyəvisi, {len(CATS)} kateqoriya.", catalog(), "products")
for c in CATS:
    page(f"mehsullar/{c['slug']}/index.html", c["name"], c["desc"], catalog(c), "products")
for p in PRODUCTS:
    b, ld = product(p)
    page(f"mehsul/{p['slug']}/index.html", p["name"], (p.get("desc") or p["short"])[:155], b, "products", jsonld=ld)
page("hell-yollari/index.html", "Həll yolları", "Hamam, teras, hovuz, fasad, zirzəmi və döşəmə üçün Mr.Fix məhsul sistemləri.", solutions, "solutions")
for s in SYSTEMS:
    page(f"hell-yollari/{s['id']}/index.html", s["name"] + " — sistem həlli", s["intro"][:155], solution(s), "solutions", tools=False)
page("hesablayici/index.html", "Material hesablayıcısı", "Dərz dolğusu, kafel yapışdırıcısı, su izolyasiyası və şap sərfiyyatını hesablayın.", calculator, "calc", tools=True)
page("reng-secimi/index.html", "Dərz rəngləri", "FUGAMAX® dərz dolğularının 32 rəngini kafel üzərində canlı sınayın.", studio, "products", tools=True)
page("bloq/index.html", "Bloq", "Tikinti kimyəviləri üzrə praktik bələdçilər: yapışdırıcı seçimi, su izolyasiyası, fasad.", blog_index, "blog")
for b in POSTS:
    body, ld = blog_post(b)
    page(f"bloq/{b['slug']}/index.html", b["title"], b["excerpt"][:155], body, "blog", jsonld=ld, progress=True)
page("xeberler/index.html", "Xəbərlər", "Mr.Fix şirkət xəbərləri.", news_index, None)
for n in NEWS:
    page(f"xeberler/{n['slug']}/index.html", n["title"], n["body"][0][:155], news_post(n), None)
page("referanslar/index.html", "Layihələr", "Mr.Fix məhsullarının istifadə olunduğu referans layihələr.", references, "refs")
for r in REFS:
    if r.get("products") is not None:
        page(f"referanslar/{ref_slug(r)}/index.html", r["name"], (r.get("desc") or (r["name"] + " — Mr.Fix məhsullarının istifadə olunduğu layihə."))[:155], ref_page(r), "refs")
page("haqqimizda/index.html", "Haqqımızda", "Kartaş MMC — 2000-ci ildən Mr.Fix brendi ilə tikinti kimyəviləri istehsalı.", about, "about")
page("dilerler/index.html", "Dilerlər", "Mr.Fix diler şəbəkəsi: Azərbaycan, Gürcüstan, Özbəkistan, Türkiyə.", dealers, None)
page("senedler/index.html", "Texniki sənədlər", "Mr.Fix məhsullarının TDS və SDS vərəqələri.", documents, "products")
page("karyera/index.html", "Karyera", "Mr.Fix komandasına qoşulun.", career, None)
page("elaqe/index.html", "Əlaqə", "Mr.Fix baş ofis: Xətai prospekti 43, Bakı. Telefon, e-poçt, WhatsApp.", contact, "contact")
page("404.html", "Səhifə tapılmadı", "Səhifə tapılmadı.", nf, None)

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
for sub in ("css", "js", "assets", "img", "m"):
    src = os.path.join(BASE, "static", sub)
    if os.path.exists(src): shutil.copytree(src, os.path.join(OUT, sub))

def explicit(doc):
    return re.sub(r'href="((?!https?:|mailto:|tel:|#|data:)[^"]*?/)"', lambda m: f'href="{m.group(1)}index.html"', doc).replace('href="./"', 'href="./index.html"')

# mrfix.az fayllarının yerli nüsxəsi (static/m/) varsa, ona yönləndir — köhnə sayt bağlansa da şəkil və PDF-lər işləyir
MPRE = "https://mrfix.az/site/assets/files/"
def local_assets(doc):
    bp = SITE.get("base_path", "/")
    def rep(m):
        rel = m.group(1)
        return bp + "m/" + rel if os.path.exists(os.path.join(BASE, "static", "m", urllib.parse.unquote(rel))) else m.group(0)
    return re.sub(re.escape(MPRE) + r'([^"\s)\]<>]+)', rep, doc)

for path, doc in PAGES:
    if path == "404.html":
        bp = SITE.get("base_path", "/")
        doc = doc.replace('data-root="./"', f'data-root="{bp}"').replace('href="./', f'href="{bp}').replace('src="./', f'src="{bp}')
    if EXPLICIT: doc = explicit(doc)
    doc = local_assets(doc)
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)

# search index
items = [dict(k="Məhsul", t=p["name"], d=p.get("standard") or p["short"], x=p["short"] + " " + CAT[p["cat"]]["name"] + " " + " ".join(p.get("areas", [])), u=f"mehsul/{p['slug']}/") for p in PRODUCTS]
items += [dict(k="Kateqoriya", t=c["name"], d=f'{c["count"]} məhsul', x=c["desc"], u=f"mehsullar/{c['slug']}/") for c in CATS]
items += [dict(k="Həll", t=s["name"], d=s["short"], x=" ".join(s["keywords"]), u=f"hell-yollari/{s['id']}/") for s in SYSTEMS]
items += [dict(k="Bloq", t=b["title"], d=b["excerpt"], x=b["category"], u=f"bloq/{b['slug']}/") for b in POSTS]
items += [dict(k="Səhifə", t=t, d=d, x=x, u=u) for t, d, x, u in [("Material hesablayıcısı", "Dərz, yapışdırıcı, izolyasiya, şap", "hesabla sərfiyyat kq neçə kisə", "hesablayici/"), ("Dərz rəngləri", "32 rəng", "rəng dərz fuga", "reng-secimi/"), ("Dilerlər", "Satış nöqtələri", "diler mağaza harada almaq", "dilerler/"), ("Texniki sənədlər", "TDS və SDS", "pdf vərəqə sənəd", "senedler/"), ("Əlaqə", SITE["contact"]["phones"][0], "telefon ünvan", "elaqe/")]]
systems = [dict(n=s["name"], k=[x.lower() for x in s["keywords"]], u=f"hell-yollari/{s['id']}/", l=[[l["role"], l["product"], f"mehsul/{BY_NAME[l['product']]['slug']}/"] for l in s["layers"] if l["product"] in BY_NAME]) for s in SYSTEMS]
if EXPLICIT:
    for it in items: it["u"] += "index.html"
    for s in systems:
        s["u"] += "index.html"
        for l in s["l"]: l[2] += "index.html"
json.dump(dict(items=items, systems=systems), open(os.path.join(OUT, "search.json"), "w", encoding="utf-8"), ensure_ascii=False)

# sitemap, robots, nojekyll, CNAME
urls = [SITE["url"].rstrip("/") + "/" + (p[:-10] if p.endswith("index.html") else p) for p, _ in PAGES if p != "404.html"]
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{html.escape(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['url'].rstrip('/')}/sitemap.xml\n")
open(os.path.join(OUT, ".nojekyll"), "w").write("")
if SITE.get("cname"): open(os.path.join(OUT, "CNAME"), "w").write(SITE["cname"] + "\n")
print(f"OK: {len(PAGES)} səhifə yığıldı -> {OUT}")
