"""Build index.html from portfolio.src.html.

Wraps the source in a full HTML document, writes the @font-face rules for the
self-hosted fonts in assets/fonts/, and inlines assets/img/manifest.json (made by
optimize_images.py) so the page also works when opened straight from disk.

  python3 build.py                        -> index.html (the real site)
  python3 build.py --artifact <file.html> -> shareable claude.ai artifact page
"""
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
<meta name="description" content="Vũ Hoàng Phương: design manager and creative lead in Ho Chi Minh City. Portfolio and CV.">
<meta name="theme-color" content="#03031a">
<meta property="og:title" content="Vũ Hoàng Phương · Creative">
<meta property="og:description" content="Design manager and creative lead. Selected work for Dai-ichi Life, Sunrise Events, CEN Group, Laguna Lăng Cô, Nam Long and Victoria.">
<meta property="og:image" content="assets/img/sunrise-events-vietnam/01.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{GOOGLE_FONTS}">
"""


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


def main():
    src = (ROOT / "portfolio.src.html").read_text()
    faces = "\n".join(
        f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;font-display:swap;'
        f'src:url(assets/fonts/{f}) format("woff")}}'
        for fam, w, f in FONTS
    )
    manifest = (ROOT / "assets" / "img" / "manifest.json").read_text().strip()
    src = src.replace("/*__FONTS__*/", faces).replace("/*__MANIFEST__*/{}", manifest)
    style_end = src.index("</style>") + len("</style>")
    html = HEAD.replace("{GOOGLE_FONTS}", GOOGLE_FONTS) + src[:style_end] + "\n</head>\n<body>\n" + src[style_end:].lstrip() + "</body>\n</html>\n"
    (ROOT / "index.html").write_text(html)
    print(f"index.html: {len(html) // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--artifact":
        artifact(Path(sys.argv[2]))
    else:
        main()
