"""Compress the originals in Images/ into web-ready WebP files under assets/img/.

Needs Pillow (pip install Pillow). Writes, per project:
  assets/img/<slug>/NN.webp         full view, longest side 1600px
  assets/img/<slug>/thumbs/NN.webp  grid/gallery thumbnail, longest side 720px
plus assets/img/avatar.webp and avatar-lg.webp (portrait for the nav and the intro), and assets/img/manifest.json, which build.py inlines into index.html.

Re-run after adding or removing originals. COVERS picks the card image per project
(file name inside the source folder); otherwise the first file is used. Files in a
"New" subfolder come right after the cover, ahead of the older work. Other subfolders
(e.g. one per brand, "1 Dong Nguyen", "2 SR Vietnam") follow in name order, so a
gallery groups by brand; a subfolder whose name starts with "_" is skipped.
"""
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).parent
SRC = ROOT / "Images"
OUT = ROOT / "assets" / "img"
FULL, THUMB = 1600, 720

FOLDERS = {
    "DAI-ICHI LIFE": "dai-ichi-life-vietnam",
    "SUNRISE EVENT": "sunrise-events-vietnam",
    "CEN GROUP": "cen-group-rising-star-media",
    "LAGUNA LANG CO": "laguna-lang-co",
    "NAM LONG": "nam-long-group",
    "VICTORIA": "thien-minh-hospitality-thien-minh-group",
    "FREELANCE": "freelancer",
}
COVERS = {
    "dai-ichi-life-vietnam": "00_Daiichi-portal-thumbnail.jpg",
    "sunrise-events-vietnam": "#1-Urban-Poster-Billboard-Mock-Up---Night-Edition.jpg",
    "cen-group-rising-star-media": "6MC_Key-Visual_FINAL.png",
    "laguna-lang-co": "LAGUNA_Brochure_Co gai & Chu tho_Page_01.jpg",
    "nam-long-group": "AH_Key-Visual_Final_Option-1.jpg",
    "thien-minh-hospitality-thien-minh-group": "Overview.jpg",
    "freelancer": "Keppel Land_billboard_mockup_v2_03.jpg",
}
# Slide decks shown as flip books instead of gallery images: id -> folder of slide images, or a
# PDF, under Images/. Each page becomes assets/decks/<id>/NN.webp (1600x900) and the deck
# assets/decks/<id>.pdf (a PDF source is copied as is; reading one needs PyMuPDF).
DECKS = {
    "sr-vietnam-brand-story": "FREELANCE/_decks/SR Vietnam Brand Story",
    "sac-nhanh-brand-concept": "FREELANCE/_decks/Sac Nhanh Brand Concept",
    "flow-english-brand-proposal": "FREELANCE/_decks/TES_Proposal_round 1_v3.pdf",
}
DECK_SIZE = (1600, 900)
SKIP = re.compile(r"^(\.|Screenshot )")
EXT = {".jpg", ".jpeg", ".png", ".webp"}


def natural(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def save(im, path, size):
    im = im.copy()
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(path, "WEBP", quality=80, method=6)


def avatar():
    """Head-and-shoulders crop of Images/Avatar.png: avatar.webp for the nav,
    avatar-lg.webp for the intro's round frame (transparent WebP)."""
    im = Image.open(SRC / "Avatar.png").convert("RGBA")
    w = im.width
    side = round(w * 0.78)
    left = 0
    face = im.crop((left, 0, left + side, side))
    face.resize((192, 192), Image.LANCZOS).save(OUT / "avatar.webp", "WEBP", quality=85, method=6)
    face.resize((640, 640), Image.LANCZOS).save(OUT / "avatar-lg.webp", "WEBP", quality=84, method=6)


def decks():
    """Pages for the flip book viewer plus a PDF of each deck (pages fitted to 16:9)."""
    out = {}
    for deck, folder in DECKS.items():
        src = SRC / folder
        d = ROOT / "assets" / "decks" / deck
        d.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() == ".pdf":
            import io
            import pymupdf
            doc = pymupdf.open(src)
            sources = [Image.open(io.BytesIO(pg.get_pixmap(dpi=round(72 * DECK_SIZE[0] / pg.rect.width)).tobytes("png"))) for pg in doc]
        else:
            files = sorted((f for f in src.iterdir() if f.suffix.lower() in EXT and not SKIP.match(f.name)),
                           key=lambda f: natural(f.name))
            sources = [ImageOps.exif_transpose(Image.open(f)) for f in files]
        pages = []
        for n, im in enumerate(sources, 1):
            im = ImageOps.fit(im.convert("RGB"), DECK_SIZE, Image.LANCZOS)
            im.save(d / f"{n:02d}.webp", "WEBP", quality=82, method=6)
            pages.append(im)
        pdf = ROOT / "assets" / "decks" / f"{deck}.pdf"
        if src.suffix.lower() == ".pdf":
            shutil.copyfile(src, pdf)
        else:
            pages[0].save(pdf, "PDF", save_all=True, append_images=pages[1:], resolution=150, quality=85)
        out[deck] = len(pages)
        print(f"deck {deck}: {len(pages)} pages")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    avatar()
    manifest = {}
    for folder, slug in FOLDERS.items():
        files = []
        groups = sorted((d for d in (SRC / folder).iterdir() if d.is_dir() and d.name != "New" and not d.name.startswith("_")),
                        key=lambda d: natural(d.name))
        for d in [SRC / folder / "New", SRC / folder] + groups:
            if d.is_dir():
                files += sorted(
                    (f for f in d.iterdir() if f.suffix.lower() in EXT and not SKIP.match(f.name)),
                    key=lambda f: natural(f.name),
                )
        cover = COVERS.get(slug)
        files.sort(key=lambda f: f.name != cover)  # stable: cover first, then New, then the rest
        (OUT / slug / "thumbs").mkdir(parents=True, exist_ok=True)
        items = []
        for n, f in enumerate(files, 1):
            im = ImageOps.exif_transpose(Image.open(f))
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
            name = f"{n:02d}.webp"
            save(im, OUT / slug / name, FULL)
            save(im, OUT / slug / "thumbs" / name, THUMB)
            w, h = im.size
            items.append([name, round(w / h, 3)])
        manifest[slug] = items
        print(f"{slug}: {len(items)} images")
    manifest["_decks"] = decks()
    (OUT / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")))


if __name__ == "__main__":
    main()
