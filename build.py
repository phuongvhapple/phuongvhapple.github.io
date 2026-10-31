"""Build index.html from portfolio.src.html.

Wraps the source in a full HTML document, writes the @font-face rules for the
self-hosted fonts in assets/fonts/, and inlines assets/img/manifest.json (made by
optimize_images.py) so the page also works when opened straight from disk.

  python3 build.py                        -> index.html (the real site), llms.txt, robots.txt, sitemap.xml
  python3 build.py --artifact <file.html> -> shareable claude.ai artifact page

The site draws its Work cards and Experience rail with JavaScript. AI readers and most
crawlers do not run scripts, so the build also writes that content into the HTML (the
script redraws it identically), adds a schema.org Person block, and writes llms.txt: the
whole CV and portfolio as plain Markdown. Needs Node to read PROJECTS and JOBS.
"""
import datetime
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

# Barlow (body) is self-hosted; Reddit Sans (headlines) and Barlow Condensed Bold
# (sub-titles) come from Google Fonts, linked in HEAD.
FONTS = [
    ("Barlow", "400", "bw400.woff"),
    ("Barlow", "700", "bw700.woff"),
]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Vũ Hoàng Phương (Phuong Vu Hoang): Design Manager and creative lead in Ho Chi Minh City with 10+ years in brand identity, key visuals, events, UI design and AI-assisted workflows. CV and portfolio.">
<meta name="theme-color" content="#03031a">
<link rel="canonical" href="{SITE}">
<link rel="alternate" type="text/markdown" title="CV and portfolio as plain text" href="{SITE}llms.txt">
<meta property="og:type" content="profile">
<meta property="og:url" content="{SITE}">
<meta property="og:title" content="Vũ Hoàng Phương · Design Manager & Creative">
<meta property="og:description" content="Design manager and creative lead. Selected work for Dai-ichi Life Vietnam, Sunrise Events Vietnam, CEN Group, Laguna Lăng Cô, Nam Long and Thien Minh Group.">
<meta property="og:image" content="{SITE}assets/img/sunrise-events-vietnam/01.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{GOOGLE_FONTS}">
"""


SITE = "https://phuongvhapple.github.io/"
GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700&family=Reddit+Sans:wght@400;500;600&display=swap"


def artifact(out):
    """Shareable claude.ai artifact: no document wrapper (the host adds it), all fonts
    from Google Fonts, one image size (assets/img/<slug>/NN.webp), bare #slug links."""
    src = (ROOT / "portfolio.src.html").read_text()
    manifest = (ROOT / "assets" / "img" / "manifest.json").read_text().strip()
    fonts = GOOGLE_FONTS.replace("family=Barlow+Condensed", "family=Barlow:wght@400;700&family=Barlow+Condensed")
    head = (
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{fonts}">\n'
    )
    title_end = src.index("</title>") + len("</title>\n")
    src = src[:title_end] + head + src[title_end:]
    src = (src.replace("/*__FONTS__*/", "")
              .replace("/*__MANIFEST__*/{}", manifest)
              .replace("/*__EMBEDDED__*/false", "true"))
    out.write_text(src)
    print(f"{out}: {len(src) // 1024} KB")


def data(src):
    """PROJECTS and JOBS exactly as the page script defines them, evaluated by Node."""
    parts = []
    for start in ("var PROJECTS = [", "var JOBS = ["):
        i = src.index(start)
        parts.append(src[i:src.index("\n  ];", i) + 5])
    js = "\n".join(parts) + "\nprocess.stdout.write(JSON.stringify({projects: PROJECTS, jobs: JOBS}));"
    return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)


def text(fragment):
    """Visible text of an HTML fragment."""
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def section(src, start, end):
    i = src.index(start)
    return src[i:src.index(end, i)]


def esc(s):
    return html.escape(s, quote=False)


def prerender(src, d, manifest):
    """Work cards and the Experience rail in the same markup the script draws, plus the
    project write-ups in <noscript> (shown only where scripts do not run)."""
    cards = "".join(
        f'<a href="#{p["slug"]}" class="card" style="text-decoration:none"><div class="art" style="--a:{p["a"]};--b:{p["b"]}">'
        f'<b>{esc(p["code"])}</b><span>{len(manifest.get(p["slug"], []))} images</span></div><div class="meta">'
        f'<div class="tag sub">{esc(p["role"] + (" · " + p["when"] if p["when"] else ""))}</div><h3>{esc(p["title"])}</h3></div></a>'
        for p in d["projects"])
    notes = []
    for p in d["projects"]:
        bits = [f'<h3>{esc(p["title"])}</h3><p>{esc(p["role"] + (" · " + p["when"] if p["when"] else ""))}</p><p>{esc(p["text"])}</p>']
        if p.get("extra"): bits.append(f'<p>{esc(p["extra"])}</p>')
        if p.get("videos"): bits.append("<p>Videos: " + esc("; ".join(v[0] for v in p["videos"])) + "</p>")
        if p.get("decks"): bits.append("<p>Decks and brochures: " + esc("; ".join(f"{k[1]}, {k[2]}" for k in p["decks"])) + "</p>")
        notes.append("<article>" + "".join(bits) + "</article>")
    jobs = "".join(
        f'<article class="job"><time>{esc(j[0])}</time><div><h3>{esc(j[1])}</h3><div class="at">{esc(j[2])}</div><p>{esc(j[3])}</p>'
        f'<div class="jd" id="jd-{n}"><div><h4>Responsibilities</h4><ul>' + "".join(f"<li>{esc(t)}</li>" for t in j[4]) +
        f'</ul></div></div><button class="more" type="button" aria-expanded="false" aria-controls="jd-{n}"><span>Read more</span> · {len(j[4])} points</button></div></article>'
        for n, j in enumerate(d["jobs"]))
    src = src.replace('<div class="grid" id="grid"></div>',
                      f'<div class="grid" id="grid">{cards}</div>\n    <noscript><div class="work-notes">{"".join(notes)}</div></noscript>')
    return src.replace('<div class="rail" id="rail"></div>', f'<div class="rail" id="rail">{jobs}</div>')


def person(src, d):
    """schema.org Person for search engines and AI readers."""
    skills = re.findall(r"<li>([^<]+)</li>", section(src, '<ul class="skills"', "</ul>"))
    edu = re.findall(r"<strong>([^<]+)</strong><span>([^<·]+)", section(src, '<ul class="edu"', "</ul>"))
    current = d["jobs"][0]
    ld = {
        "@context": "https://schema.org", "@type": "Person",
        "name": "Vũ Hoàng Phương", "alternateName": ["Phuong Vu Hoang", "Vu Hoang Phuong"],
        "url": SITE, "image": SITE + "assets/img/avatar-lg.webp",
        "jobTitle": "Design Manager", "description": text(section(src, '<div class="summary">', "</div>")),
        "email": "mailto:phuongvh.apple@gmail.com", "telephone": "+84 986 362 186",
        "address": {"@type": "PostalAddress", "addressLocality": "Ho Chi Minh City", "addressCountry": "VN"},
        "worksFor": {"@type": "Organization", "name": current[2]},
        "hasOccupation": {"@type": "Occupation", "name": current[1]},
        "knowsAbout": [html.unescape(s) for s in skills] + ["Figma", "Claude", "ChatGPT", "Gemini"],
        "alumniOf": [{"@type": "EducationalOrganization", "name": school.split(",")[0].strip()} for _, school in edu],
    }
    return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n"


def llms(src, d, manifest):
    """The whole CV and portfolio as Markdown (llmstxt.org)."""
    summary = re.findall(r"<p[^>]*>(.*?)</p>", section(src, '<div class="summary">', "</div>"), re.S)
    about = section(src, '<section id="about">', "</section>")
    traits = re.findall(r"<p>(.*?)</p>", section(about, "Characteristics", "<ul"), re.S)
    skills = re.findall(r"<li>([^<]+)</li>", section(src, '<ul class="skills"', "</ul>"))
    edu = re.findall(r"<strong>([^<]+)</strong><span>([^<]+)</span>", section(src, '<ul class="edu"', "</ul>"))
    facts = text(section(src, '<aside class="facts"', "</aside>"))
    out = ["# Vũ Hoàng Phương (Phuong Vu Hoang)", "",
           "> Design Manager and creative lead in Ho Chi Minh City, Vietnam. 10+ years from graphic design to creative "
           "direction across brand identity, key visuals, events, photo and video, UI design and AI-assisted workflows. "
           f"Portfolio: {SITE}", "",
           "Contact: phuongvh.apple@gmail.com · +84 986 362 186 · Ho Chi Minh City", "",
           "## Professional summary", ""] + [text(p) + "\n" for p in summary] + [
           f"At a glance: {facts}", "", "## Experience", ""]
    for j in d["jobs"]:
        out += [f"### {j[1]}, {j[2]} ({j[0]})", "", j[3], ""] + [f"- {t}" for t in j[4]] + [""]
    out += ["## Selected work", "", f"Each project opens at {SITE}#<slug> with its gallery, videos and flip-through decks.", ""]
    for p in d["projects"]:
        out += [f"### {p['title']} ({p['role']}{', ' + p['when'] if p['when'] else ''})", "", f"Link: {SITE}#{p['slug']}", "", p["text"], ""]
        if p.get("extra"): out += [p["extra"], ""]
        if p.get("videos"): out += ["Videos: " + "; ".join(v[0] for v in p["videos"]) + ".", ""]
        if p.get("decks"): out += ["Decks and brochures: " + "; ".join(f"{k[1]}, {k[2]}" for k in p["decks"]) + ".", ""]
        out += [f"Gallery: {len(manifest.get(p['slug'], []))} images.", ""]
    out += ["## About", ""] + [text(t) + "\n" for t in traits] + [
            "Skills: " + ", ".join(html.unescape(s) for s in skills) + ".", "", "## Education", ""]
    out += [f"- {html.unescape(a)}, {html.unescape(b).replace(' · ', ', ')}" for a, b in edu] + [""]
    return "\n".join(out)


def main():
    src = (ROOT / "portfolio.src.html").read_text()
    d = data(src)
    manifest_data = json.loads((ROOT / "assets" / "img" / "manifest.json").read_text())
    (ROOT / "llms.txt").write_text(llms(src, d, manifest_data))
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    today = datetime.date.today().isoformat()
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE}</loc><lastmod>{today}</lastmod></url>\n"
        f"  <url><loc>{SITE}llms.txt</loc><lastmod>{today}</lastmod></url>\n</urlset>\n")
    ld = person(src, d)
    src = prerender(src, d, manifest_data)
    faces = "\n".join(
        f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;font-display:swap;'
        f'src:url(assets/fonts/{f}) format("woff")}}'
        for fam, w, f in FONTS
    )
    manifest = (ROOT / "assets" / "img" / "manifest.json").read_text().strip()
    src = src.replace("/*__FONTS__*/", faces).replace("/*__MANIFEST__*/{}", manifest)
    style_end = src.index("</style>") + len("</style>")
    page = (HEAD.replace("{GOOGLE_FONTS}", GOOGLE_FONTS).replace("{SITE}", SITE) + ld + src[:style_end]
            + "\n</head>\n<body>\n" + src[style_end:].lstrip() + "</body>\n</html>\n")
    (ROOT / "index.html").write_text(page)
    print(f"index.html: {len(page) // 1024} KB, llms.txt, robots.txt, sitemap.xml")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--artifact":
        artifact(Path(sys.argv[2]))
    else:
        main()
