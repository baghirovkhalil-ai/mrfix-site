# Mr.Fix — korporativ sayt

Statik, çoxsəhifəli sayt (181 səhifə). Server və verilənlər bazası tələb etmir. GitHub Pages-də pulsuz işləyir.

**Tam təlimat: `TELIMAT.html` faylını brauzerdə açın.**

## Struktur

```
content/      ← bütün məzmun (məhsullar, həllər, dilerlər, xəbərlər, bloq)
static/       ← dizayn: css, js, loqo
build.py      ← content + static → _site (hazır sayt)
_site/        ← yığılmış sayt (birbaşa yükləmək olar)
tools/        ← köməkçi skriptlər (şəkil endirmə)
.github/      ← GitHub Actions: hər dəyişiklikdə avtomatik yığılma
```

## Tez başlanğıc

```bash
pip install markdown
python3 build.py
cd _site && python3 -m http.server 8000   # http://localhost:8000
```

## GitHub Pages

1. Bütün faylları repozitoriyaya yükləyin (`.github` qovluğu daxil).
2. Settings → Pages → Source: **GitHub Actions**.
3. `content/` faylında hər dəyişiklik saytı 1–2 dəqiqəyə yeniləyir.
