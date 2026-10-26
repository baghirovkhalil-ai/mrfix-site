# Məhsul şəkillərini mrfix.az-dan static/img/products/ qovluğuna endirir.
# Domeni GitHub-a keçirməzdən ƏVVƏL öz kompüterinizdə bir dəfə işə salın:
#   python3 tools/download_images.py
# Sonra static/img qovluğunu GitHub-a yükləyin. build.py yerli şəkli avtomatik seçir.
import json, os, urllib.request

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
out = os.path.join(BASE, "static", "img", "products")
os.makedirs(out, exist_ok=True)
products = json.load(open(os.path.join(BASE, "content", "products.json"), encoding="utf-8"))
ok = 0
for p in products:
    dst = os.path.join(out, p["slug"] + ".png")
    if os.path.exists(dst):
        continue
    try:
        req = urllib.request.Request(p["image"], headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        open(dst, "wb").write(data)
        ok += 1
        print("✓", p["name"])
    except Exception as ex:
        print("✗", p["name"], ex)
print(f"{ok} şəkil endirildi -> {out}")
