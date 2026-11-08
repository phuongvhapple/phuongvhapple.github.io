"""Roll-up standee mockup: artwork on a banner standing on its cassette base in a soft studio.

  .venv/bin/python tools/standee_mockup.py <artwork> <out.jpg> [pixels to crop from the top]

Used for the Infiniti, Von Wong and Plastic Sea standees in Images/FREELANCE. Save the
mockup into the brand folder and move the flat artwork to Images/<FOLDER>/_removed/.
"""
import sys

from PIL import Image, ImageDraw, ImageFilter


def lin(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(w, h, top, bot):
    g = Image.new("RGB", (1, h))
    for y in range(h):
        g.putpixel((0, y), lin(top, bot, y / max(h - 1, 1)))
    return g.resize((w, h))


def mockup(art_path, out, crop_top=0, wall=((236, 234, 230), (214, 210, 203)), floor=((205, 199, 190), (184, 177, 167))):
    W, H = 1300, 2000
    art = Image.open(art_path).convert("RGB")
    if crop_top:
        art = art.crop((0, crop_top, art.width, art.height))
    bh = 1500
    bw = round(bh * art.width / art.height)
    if bw > 760:
        bw = 760
        bh = round(bw * art.height / art.width)
    art = art.resize((bw, bh), Image.LANCZOS)
    fy = 1640  # where the wall meets the floor
    im = vgrad(W, fy, *wall).resize((W, H))
    im.paste(vgrad(W, H - fy, *floor), (0, fy))
    # soft light pool on the wall
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((W * 0.1, -300, W * 0.9, fy), fill=60)
    im.paste((255, 255, 255), (0, 0), glow.filter(ImageFilter.GaussianBlur(220)))
    x0 = (W - bw) // 2
    top = fy + 40 - bh
    baseh, basew = 44, bw + 70
    # shadow on the wall behind and on the floor
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 40, top + 50, x0 + bw + 60, fy + 10), 10, fill=70)
    im.paste((60, 55, 50), (0, 0), sh.filter(ImageFilter.GaussianBlur(45)))
    fl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(fl).ellipse((x0 - 90, fy + 40 + baseh - 26, x0 + bw + 110, fy + 40 + baseh + 40), fill=150)
    im.paste((40, 36, 32), (0, 0), fl.filter(ImageFilter.GaussianBlur(26)))
    # banner with a faint sheen down its left side and a darker right edge
    im.paste(art, (x0, top))
    sheen = Image.new("L", (bw, bh), 0)
    sd = ImageDraw.Draw(sheen)
    for x in range(bw):
        t = x / bw
        sd.line((x, 0, x, bh), fill=int(40 * max(0, 1 - t / 0.35)) + int(18 * max(0, (t - 0.85) / 0.15)))
    im.paste((255, 255, 255), (x0, top), sheen)
    edge = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(edge).rectangle((bw - 6, 0, bw, bh), fill=50)
    im.paste((0, 0, 0), (x0, top), edge)
    d = ImageDraw.Draw(im)
    # top rail
    d.rounded_rectangle((x0 - 6, top - 10, x0 + bw + 6, top + 6), 6, fill=(150, 152, 156))
    d.rectangle((x0 - 6, top - 10, x0 + bw + 6, top - 6), fill=(205, 207, 211))
    # cassette base: brushed aluminium with a light lip and two feet
    bx0, by0 = (W - basew) // 2, fy + 40
    mask = Image.new("L", (basew, baseh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, basew, baseh), 20, fill=255)
    im.paste(vgrad(basew, baseh, (226, 228, 232), (128, 131, 138)), (bx0, by0), mask)
    d.rounded_rectangle((bx0 + 14, by0 + 4, bx0 + basew - 14, by0 + 9), 3, fill=(245, 246, 248))
    for fx in (bx0 + 30, bx0 + basew - 90):
        d.rounded_rectangle((fx, by0 + baseh - 4, fx + 60, by0 + baseh + 8), 5, fill=(70, 72, 78))
    im.save(out, quality=92)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mockup(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
