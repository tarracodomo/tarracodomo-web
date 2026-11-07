import html
import json
import pathlib
import re

BASE = "https://tarracodomo.com"
IMG = BASE + "/image-3.png"
ALT = "Tarraco Domo: domótica, cámaras y monitorización en Tarragona"
SKIP_CSS = "<style>.skip{position:absolute;left:-9999px;top:0;background:#fff;color:#111;padding:.6rem 1rem;z-index:999}.skip:focus{left:1rem}</style>"


def url_for(path):
    if path.name == "index.html":
        return BASE + "/"
    return BASE + "/" + path.stem


def esc(value):
    return html.escape(value.strip(), quote=True)


def short_name(title):
    name = re.sub(r"\s*\|\s*Tarraco Domo\s*$", "", title or "").strip()
    if ":" in name:
        head = name.split(":", 1)[0].strip()
        if head:
            name = head
    return name


def crumbs(path, title, url):
    name = short_name(title) or path.stem
    items = [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE + "/"},
    ]
    if path.stem.startswith("doc-"):
        items.append({"@type": "ListItem", "position": 2, "name": "Documentación", "item": BASE + "/documentacion"})
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": name, "item": url})
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def shorten_existing(text, title):
    def repl(match):
        block = match.group(1)
        if "BreadcrumbList" not in block:
            return match.group(0)
        try:
            data = json.loads(block)
        except ValueError:
            return match.group(0)
        items = data.get("itemListElement") or []
        name = short_name(title)
        if items and name:
            items[-1]["name"] = name
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, text, flags=re.S)


def patch(path):
    text = path.read_text(encoding="utf-8")
    original = text
    match = re.search(r"<head>(.*?)</head>", text, re.S | re.I)
    if not match:
        return False
    head = match.group(1)
    raw_title = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    raw_title = html.unescape(raw_title.group(1)) if raw_title else "Tarraco Domo"
    title = esc(raw_title)
    desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', head, re.I | re.S)
    desc = esc(desc.group(1)) if desc else "Domótica, cámaras y monitorización en Tarragona."
    canon = re.search(r'<link\s+rel="canonical"\s+href="(.*?)"', head, re.I)
    url = canon.group(1) if canon else url_for(path)

    add = []
    if 'name="theme-color"' not in head:
        add.append('<meta name="theme-color" content="#ffffff">')
    if canon is None:
        add.append('<link rel="canonical" href="%s">' % url)
    if "og:site_name" not in head:
        add += [
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Tarraco Domo">',
            '<meta property="og:locale" content="es_ES">',
            '<meta property="og:url" content="%s">' % url,
            '<meta property="og:title" content="%s">' % title,
            '<meta property="og:description" content="%s">' % desc,
            '<meta property="og:image" content="%s">' % IMG,
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="675">',
            '<meta property="og:image:alt" content="%s">' % ALT,
        ]
    if "twitter:title" not in head:
        add += [
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:site" content="@tarracodomo">',
            '<meta name="twitter:title" content="%s">' % title,
            '<meta name="twitter:description" content="%s">' % desc,
            '<meta name="twitter:image" content="%s">' % IMG,
        ]
    if '"BreadcrumbList"' not in text:
        add.append(crumbs(path, raw_title, url))
    if 'class="skip"' not in text:
        add.append(SKIP_CSS)
    if add:
        text = re.sub(r"</head>", "\n".join(add) + "\n</head>", text, count=1, flags=re.I)

    text = shorten_existing(text, raw_title)
    text = re.sub(r"<br>\s*<div class=\"dev\"[^>]*>.*?</div>", "", text, flags=re.S)

    if 'class="skip"' not in text:
        text = re.sub(r"(<body>)", r'\1\n<a class="skip" href="#main">Saltar al contenido</a>', text, count=1, flags=re.I)
    if 'id="main"' not in text:
        text = re.sub(r"<main(\s)", r'<main id="main"\1', text, count=1, flags=re.I)
    if 'id="main"' not in text and "<main>" in text:
        text = text.replace("<main>", '<main id="main">', 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    changed = [p.name for p in sorted(pathlib.Path(".").glob("*.html")) if patch(p)]
    print("Páginas modificadas: %d" % len(changed))
    for name in changed:
        print(" -", name)


if __name__ == "__main__":
    main()
