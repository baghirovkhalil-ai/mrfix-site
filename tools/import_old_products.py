# Bir dəfəlik: köhnə mrfix.az-da olub yeni saytda olmayan məhsulları content/products.json-a əlavə edir.
# GitHub Actions ("Köhnə saytdan məhsulları gətir") işlədir. Artıq olan slug-ları təkrar əlavə etmir.
import json, os, re, urllib.request
from bs4 import BeautifulSoup
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = "https://mrfix.az"
# (köhnə ünvan, yeni slug, kateqoriya, qrup, standart)
ITEMS = [
 ("/products/coatix/astarlar/coatix-ep-1130-primer/", "coatix-ep-1130-primer", "coatix", "Astar", ""),
 ("/products/coatix/astarlar/coatix-ep-1150-primer/", "coatix-ep-1150-primer", "coatix", "Astar", ""),
 ("/products/coatix/astarlar/coatix-ep-1220-primer/", "coatix-ep-1220-primer", "coatix", "Astar", ""),
 ("/products/coatix/astarlar/coatix-ep-1260-primer/", "coatix-ep-1260-primer", "coatix", "Astar", ""),
 ("/products/coatix/epoksid-sasli-ortukl-r/coatix-ep-3248-self-leveling/", "coatix-ep-3248-self-leveling", "coatix", "Epoksid örtüklər", ""),
 ("/products/coatix/epoksid-sasli-ortukl-r/coatix-ep-3565-self-leveling/", "coatix-ep-3565-self-leveling", "coatix", "Epoksid örtüklər", ""),
 ("/products/coatix/epoksid-sasli-ortukl-r/coatix-ep-4085-top-coat/", "coatix-ep-4085-top-coat", "coatix", "Epoksid örtüklər", ""),
 ("/products/coatix/epoksid-sasli-ortukl-r/coatix-ep-4090-thixotropic-top-coat/", "coatix-ep-4090-thixotropic-top-coat", "coatix", "Epoksid örtüklər", ""),
 ("/products/coatix/epoksid-sasli-ortukl-r/coatix-ep-4565-top-coat/", "coatix-ep-4565-top-coat", "coatix", "Epoksid örtüklər", ""),
 ("/products/coatix/hibrid-poliuretan-sement-ortukl-r/coatix-pc-7210-polyurethane-cement/", "coatix-pc-7210-polyurethane-cement", "coatix", "Poliuretan-sement örtüklər", "EN 13813 · SR-B2,0-AR0,5-IR4"),
 ("/products/kafel-ve-keramika-yapisdiricilari/epoksi-esasli/ceramax-ep-300/", "ceramax-ep-300", "yapisdirici", "Epoksid əsaslı", "EN 12004-1 · R2T / EN 13888 · RG"),
 ("/products/su-izolyasiya-materiallari/akril-sasli-su-i-zolyasiya-materiallari/izomax-aqualastic/", "izomax-aqualastic", "izolyasiya", "Akril əsaslı", ""),
 ("/products/su-izolyasiya-materiallari/sement-esasli/izomax-c-20/", "izomax-c10-rapid", "izolyasiya", "Sement əsaslı", ""),
 ("/products/suvaq-ve-horgu-mehsullari/astarlar/pratix-kontakt/", "pratix-kontakt", "suvaq", "Astar", ""),
 ("/products/suvaq-ve-horgu-mehsullari/horgu-materiallari/pratix-aero-bond/", "pratix-aero-bond", "suvaq", "Hörgü materialları", ""),
 ("/products/suvaq-ve-horgu-mehsullari/suvaq-setkalari/pratix-rm-75/", "pratix-rm-75", "suvaq", "Suvaq setkaları", ""),
 ("/products/suvaq-ve-horgu-mehsullari/suvaqlar-1/pratix-aero-plast/", "pratix-aero-plast", "suvaq", "Suvaqlar", ""),
 ("/products/suvaq-ve-horgu-mehsullari/suvaqlar-1/pratix-hp-30/", "pratix-hp-30", "suvaq", "Suvaqlar", ""),
 ("/products/suvaq-ve-horgu-mehsullari/suvaqlar-1/pratix-mp-40/", "pratix-mp-40", "suvaq", "Suvaqlar", ""),
 ("/products/termo-izolyasiya-materiallari/dubell-r/thermomax-dbl-60/", "thermomax-dbl-60p", "istilik", "Dübellər", ""),
 ("/products/termo-izolyasiya-materiallari/dubell-r/thermomax-dbl-80/", "thermomax-dbl-80m", "istilik", "Dübellər", ""),
 ("/products/termo-izolyasiya-materiallari/montaj-aksessuarlari/thermomax-cp/", "thermomax-cp", "istilik", "Montaj aksesuarları", ""),
]
T = lambda s: re.sub(r"\s+", " ", s or "").strip()
def get(u):
    return urllib.request.urlopen(urllib.request.Request(SRC + u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace")
def short_of(desc, name):
    s = desc.split(";", 1)[1] if ";" in desc[:len(name) + 5] else re.sub("^" + re.escape(name), "", desc)
    s = T(re.split(r"(?<=[a-zəöüğışç])\.\s", s)[0]).rstrip(".")
    s = re.sub(r"\s*(materialıdır|astarıdır|astardır|dir|dır|dur|dür)$", "", s)
    return (s[:1].upper() + s[1:])[:110]
def parse(u, slug, cat, group, std):
    d = BeautifulSoup(get(u), "html.parser")
    name = T((d.select_one(".product_content h1") or d.select_one("h1")).get_text())
    name = re.sub(r"®(?=\S)", "® ", name)
    pt = d.select_one(".product_text")
    lines = [T(x) for x in pt.get_text("\n").split("\n")] if pt else []
    lines = [x for x in lines if x]
    desc, areas, feats, notes, classes, mode = [], [], [], [], [], "desc"
    for ln in lines:
        low = ln.lower()
        if low.startswith("istifadə sahələri") or low.startswith("tətbiq sahələri"): mode = "areas"; continue
        if low.startswith("üstünlük"): mode = "feats"; continue
        if ln.startswith("•") or ln.startswith("-"):
            item = T(ln.lstrip("•- "))
            (areas if mode == "areas" else feats if mode == "feats" else areas).append(item); continue
        m = re.match(r"^([A-Z][A-Z0-9]{0,3}):\s*(.+)$", ln)
        if m and mode == "desc": classes.append([m.group(1), m.group(2)]); continue
        (desc if mode == "desc" else notes).append(ln)
    tech = []
    for tr in d.select(".Table tr, .product_sections table tr"):
        cells = [T(c.get_text(" ")) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        if len(cells) == 2 and [cells[0], cells[1]] not in tech: tech.append(cells)
    for r in tech:
        if re.match(r"^[+−-]?\d+\s*°C$", r[0]): r[0] = "Qabda istifadə müddəti " + r[0]
    docs = [a.get("href") for a in d.select(".document_grid a[href]")]
    pdf = lambda pat: next((SRC + h if h.startswith("/") else h for h in docs if re.search(pat, h, re.I)), "")
    img = d.select_one(".product_image img")
    img = img.get("src") if img and img.get("src") else ""
    p = {"slug": slug, "name": name, "cat": cat, "group": group, "short": short_of(" ".join(desc), name),
         "image": (SRC + img if img.startswith("/") else img), "featured": bool(pdf(r"tds_az|_az\.pdf"))}
    if std: p["standard"] = std
    if classes: p["classes"] = classes
    p["desc"] = " ".join(desc)
    if areas: p["areas"] = areas
    if feats: p["features"] = feats
    if tech: p["tech"] = tech
    cons = next((v for k, v in tech if k.lower().startswith("sərfiyyat")), "")
    if cons: p["consumption"] = cons
    tds = pdf(r"tds_az") or pdf(r"_az[^/]*\.pdf")
    sds = pdf(r"msds|sds_az|tmv")
    if tds: p["tds"] = tds
    if sds and sds != tds: p["sds"] = sds
    if notes: p["note"] = " ".join(notes)
    return p
fp = os.path.join(BASE, "content", "products.json")
prods = json.load(open(fp, encoding="utf-8")); have = {p["slug"] for p in prods}
added = []
for it in ITEMS:
    if it[1] in have: continue
    try:
        p = parse(*it); prods.append(p); added.append(p)
        print("✓", p["name"], "|", p["short"], "| tech", len(p.get("tech", [])), "| tds", bool(p.get("tds")), "| img", bool(p["image"]))
    except Exception as ex:
        print("✗", it[0], ex)
# kateqoriya sırası ilə saxla
order = [c["id"] for c in json.load(open(os.path.join(BASE, "content", "categories.json"), encoding="utf-8"))]
prods.sort(key=lambda p: order.index(p["cat"]) if p["cat"] in order else 99)
json.dump(prods, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"əlavə olundu: {len(added)} · cəmi: {len(prods)}")
