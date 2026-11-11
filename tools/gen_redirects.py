# Köhnə mrfix.az ünvanlarını (tools/old_urls.txt) yeni sayta yönləndirən qaydaları vercel.json-a yazır.
# Domen yeni sayta keçəndə Google-dakı və paylaşılmış köhnə linklər 404 verməsin deyə.
import json, os, re
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NEW = {p["slug"] for p in json.load(open(os.path.join(BASE, "content/products.json"), encoding="utf-8"))}
CAT = {"beton-qoruyucu-materiallari": "beton-kurleri", "coatix": "coatix", "kafel-ve-keramika-derz-dolgulari": "derz-dolgulari",
       "kafel-ve-keramika-yapisdiricilari": "keramika-yapisdiricilari", "q-lib-yaglari": "qelib-yaglari",
       "qatqilar-ve-astarlar": "harc-qatqilari-ve-astarlar", "qatqilar": "qatqilar", "silikon-ve-mastikler": "silikon-ve-mastikler",
       "su-izolyasiya-materiallari": "su-izolyasiyasi", "suvaq-ve-horgu-mehsullari": "suvaq-ve-horgu",
       "temir-ve-guclendirme-materiallari": "temir-ve-guclendirme", "termo-izolyasiya-materiallari": "istilik-izolyasiyasi",
       "zemin-materiallari": "zemin-materiallari"}
SOL = {"bathroom": "hamam", "hovuz": "hovuz", "metbex": "metbex", "teras-ve-eyvan": "teras", "xarici-mekanlar": "fasad", "zemin": "zemin", "zirzemi-ve-bunovre": "zirzemi"}
ALIAS = {"ceramax-standart-white": "ceramax-standard-white", "izomax-c-60-n": "izomax-c60-n", "izomax-c-70-uv": "izomax-c70-uv",
         "izomax-c-75-flex": "izomax-c75-flex", "izomax-sup-sup-f-tec": "izomax-f-tec", "izomax-sup-sup-stb-sw": "izomax-stb-sw",
         "izomax-band-f-120": "izomax-band-f", "izomax-band-f-daxili-kose": "izomax-band-f-corner-in", "izomax-band-f-xarici-kose": "izomax-band-f-corner-out",
         "izomax-band-w-120-70": "izomax-band-w", "tpe-dilatasiya-banti": "izomax-band-d-tpe", "thermomax-karbonlu-eps": "thermomax-eps-carbon",
         "thermomax-yapisdirici": "thermomax-bond-40", "thermomax-suvaq": "thermomax-plast-65", "betonmix-air": "betonmix-air-80",
         "flomax-sh-501": "flomax-sh-cure", "betonmix-shotcrete-2310-af": "betonmix-shotcrete-310-af"}
FIXED = {"/about/": "/haqqimizda/", "/cedvel/": "/hesablayici/", "/dealers/": "/dilerler/", "/derz-reng-secimi/": "/reng-secimi/",
         "/material-calculator/": "/hesablayici/", "/news/": "/xeberler/", "/products/": "/mehsullar/", "/vakansiya/": "/karyera/",
         "/kataloqlar/": "/senedler/", "/news/novb-ti-ixrac-m-kdasligimiz-gurcustan/": "/xeberler/gurcustan-ixrac/",
         "/news/m-hsullarimizi-artiq-qirgizistana-da-ixrac-etm-y-basladiq/": "/xeberler/qirgizistan-ixrac/"}
def target(u):
    if u in FIXED: return FIXED[u]
    seg = [s for s in u.split("/") if s]
    if seg[0] == "products":
        last = seg[-1]
        for cand in (ALIAS.get(last), last, re.sub(r"-\d$", "", last), ALIAS.get(re.sub(r"-\d$", "", last))):
            if cand and cand in NEW and len(seg) > 2: return f"/mehsul/{cand}/"
        if re.match(r"izomax-stb-[a-z]+$", last) and last.replace("stb-", "stb-pvc-") in NEW: return f"/mehsul/{last.replace('stb-', 'stb-pvc-')}/"
        return f"/mehsullar/{CAT[seg[1]]}/"
    if seg[0] == "hell-yollari" and len(seg) > 1: return f"/hell-yollari/{SOL[seg[1]]}/"
    if seg[0] == "news": return "/xeberler/"
    if seg[0] == "kataloqlar": return "/senedler/"
    if seg[0] == "referanslar" and len(seg) > 1: return "/referanslar/"
    return None
rules, report = [], {"mehsul": 0, "kateqoriya": 0, "diger": 0}
for u in open(os.path.join(BASE, "tools/old_urls.txt")).read().split():
    u = u if u.endswith("/") else u + "/"
    t = target(u)
    if not t or t == u: continue
    assert os.path.exists(os.path.join(BASE, "_site", t.strip("/"), "index.html")), (u, t)
    rules.append({"source": u, "destination": t, "permanent": True})
    report["mehsul" if t.startswith("/mehsul/") else "kateqoriya" if t.startswith("/mehsullar/") else "diger"] += 1
rules.append({"source": "/:lang(en|ru|tr|uz)/:path*", "destination": "/", "permanent": False})
vp = os.path.join(BASE, "vercel.json"); v = json.load(open(vp)); v["redirects"] = rules
json.dump(v, open(vp, "w"), ensure_ascii=False, indent=2); open(vp, "a").write("\n")
print(len(rules), "qayda", report)
