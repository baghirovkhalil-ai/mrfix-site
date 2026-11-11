# Bir dəfəlik: köhnə mrfix.az layihə səhifələrindən təsvir və istifadə olunan məhsulları content/references.json-a əlavə edir.
import json, os, re, difflib, urllib.request
from bs4 import BeautifulSoup
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OLD = "agilli-kend alov-qulleleri basqal-resort-spa boulevard-hotel cebrayil-zengilan-agbend-tunelleri fuzuli-susa-avtomobil-yolu havalimani-korpusu heyder-eliyev-merkezi-1 heyder-eliyev-merkezi iqtisadiyyat-nazirliyi kelbecer-lacin-tuneli lacin-hotel muganli-i-smayilli-q-b-l-yolu murovdag-tuneli qala-alti-hotel-spa qarabag-hotel qelebe-meydani-tuneli qubadli-lacin-tuneli sea-breeze-resort serq-bazari shabran-recreation-complex vaqif-turbesi xaribulbul-otel xeyal-adalari yelken-towers".split()
NAME = {"boulevard-hotel": "Baku Marriott Hotel", "xeyal-adalari": "Dreamland", "yelken-towers": "The Ritz-Carlton",
        "shabran-recreation-complex": "Shabran Wellbeing Resort", "heyder-eliyev-merkezi-1": "H. Əliyev adına Müasir Təhsil Kompleksi",
        "havalimani-korpusu": "Heydər Əliyev Beynəlxalq Hava Limanı körpüsü", "qelebe-meydani-tuneli": "Qələbə meydanı tunel tipli yol qovşağı"}
ALIAS = {"THERMOMAX YAPIŞDIRICI": "thermomax-bond-40", "THERMOMAX SUVAQ": "thermomax-plast-65", "IZOMAX C40": "izomax-c-40",
         "IZOMAX C 40": "izomax-c-40", "IZOMAX C70": "izomax-c70-uv", "IZOMAX C 70 UV": "izomax-c70-uv", "IZOMAX C 75 FLEX": "izomax-c75-flex",
         "KONTAKT ASTAR": "kontakt-astar", "BETONMIX SP SHOTCRETE 224 AL": "betonmix-shotcrete-224-al", "BETONMIX HP 1000 K": "betonmix-sp-1000-k",
         "BETONMIX HP 1000 S": "betonmix-sp-1000-s", "THERMOMAX ST 160": "thermomax-rm-160", "FLOMAX SL 220 PRIMER": "flomax-sl-primer",
         "TAMCRETE CRM 100TX": "tamcrete-crm-100-tx"}
T = lambda s: re.sub(r"\s+", " ", s or "").strip()
N = lambda s: re.sub(r"[^A-Z0-9ƏÖÜĞIŞÇ]", "", s.replace("®", "").upper())
prods = json.load(open(os.path.join(BASE, "content/products.json"), encoding="utf-8"))
BYN = {N(p["name"]): p["slug"] for p in prods}
AL = {N(k): v for k, v in ALIAS.items()}
fp = os.path.join(BASE, "content/references.json"); refs = json.load(open(fp, encoding="utf-8"))
names = [r["name"] for r in refs]
def find_ref(old, oldname):
    want = NAME.get(old, oldname)
    m = difflib.get_close_matches(want.replace("-", "–"), names, n=1, cutoff=0.45) or difflib.get_close_matches(want, names, n=1, cutoff=0.45)
    return refs[names.index(m[0])] if m else None
miss = []
for old in OLD:
    d = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(f"https://mrfix.az/referanslar/{old}/", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace"), "html.parser")
    st = d.select_one(".solution_text"); txt = st.get_text("\n") if st else ""
    parts = re.split(r"İstifadə olunan məhsullar:?", txt)
    desc = T(parts[0]); pnames = [T(x) for x in (parts[1] if len(parts) > 1 else "").split("\n") if T(x)]
    links = [T(a.get_text()) for a in (st.select('a[href*="/products/"]') if st else [])]
    if not pnames: pnames = links
    if pnames and desc and all(n in desc for n in pnames[:2]): desc = ""
    bc = [T(x.get_text()) for x in d.select(".breadcrumbs a, .breadcrumbs span")]; oldname = bc[-1] if bc else old
    r = find_ref(old, oldname)
    if not r: print("✗ layihə tapılmadı:", old, oldname); continue
    out, seen = [], set()
    for n in pnames:
        k = N(n); s = AL.get(k) or BYN.get(k)
        item = {"name": n.replace("®", "® ").replace("®  ", "® "), "slug": s} if s else {"name": n}
        if (s or n) in seen: continue
        seen.add(s or n); out.append(item)
        if not s: miss.append((old, n))
    r["old"] = old; r["desc"] = desc; r["products"] = out
    print("✓", old, "→", r["name"], "| məhsul", len(out), "| uyğun", sum(1 for x in out if x.get("slug")))
json.dump(refs, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("yeni saytda olmayan məhsullar:", miss)
