# mrfix.az serverindəki bütün şəkil və PDF-ləri (content/ içində keçən) static/m/ qovluğuna köçürür.
# build.py bu yerli nüsxəni avtomatik istifadə edir — köhnə sayt bağlansa da heç nə itmir.
# GitHub Actions ("Köhnə saytdan faylları köçür") bunu avtomatik işlədir; əl ilə: python3 tools/mirror_assets.py
import os, re, glob, urllib.request, urllib.parse
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PRE = "https://mrfix.az/site/assets/files/"
urls = set()
for f in glob.glob(os.path.join(BASE, "content", "**", "*.*"), recursive=True):
    urls |= set(re.findall(re.escape(PRE) + r'[^"\s)\]]+', open(f, encoding="utf-8").read()))
ok = skip = bad = 0
for u in sorted(urls):
    dst = os.path.join(BASE, "static", "m", urllib.parse.unquote(u[len(PRE):]))
    if os.path.exists(dst) and os.path.getsize(dst) > 0: skip += 1; continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
        open(dst, "wb").write(data); ok += 1
    except Exception as ex:
        bad += 1; print("✗", u, ex)
print(f"cəmi {len(urls)} · yeni {ok} · artıq var {skip} · xəta {bad}")
