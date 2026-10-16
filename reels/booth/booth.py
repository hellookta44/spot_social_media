"""SPOT booth concept — drawn procedurally (architectural-render style).

draw_booth(lights)        -> RGBA 1080x1920 booth (lights 0..1 fades the spotlights/backlight on)
person(...)               -> soft grey silhouette (architectural-visualisation style)
bubble(text)              -> white speech bubble
Concept: 3 m x 3 m shell booth. Cream back wall with backlit SPOT wordmark + gold line,
oak-slat side walls, brass shelves with unlabelled frosted bottles and SPOT boxes,
white counter with gold edge, testers, a waitlist tablet, ink header fascia, track spots.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
S = 2  # supersample
HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(HERE, "..", "..", "brand")

CREAM = (243, 238, 230)
CREAM_D = (226, 218, 206)
INK = (34, 32, 30)
GOLD = (190, 154, 98)
OAK = (196, 160, 118)
OAK_D = (168, 132, 94)
WHITE = (252, 251, 248)
FLOOR = (214, 196, 172)

VP = (540, 860)  # vanishing point
BACK = (250, 650, 830, 1190)  # back wall x0, y0, x1, y1
HEADER = (0, 470, 1080, 590)
FRONT_Y = 1560


def _s(pts):
    return [(x * S, y * S) for x, y in pts]


def _logo(width, dark=True):
    src = Image.open(os.path.join(BRAND, "spot_logo_dark.png" if dark else "spot_logo_white.png")).convert("RGBA")
    return src.resize((width, round(src.height * width / src.width)), Image.LANCZOS)


def _paste(img, src, cx, cy):
    img.alpha_composite(src, (int(cx - src.width / 2), int(cy - src.height / 2)))


def _text(txt, size, color, font, tracking=0):
    from PIL import ImageFont
    f = ImageFont.truetype(font, size)
    w = int(sum(f.getlength(c) + tracking for c in txt)) + 4
    im = Image.new("RGBA", (w, int(size * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 0
    for c in txt:
        d.text((x, 0), c, font=f, fill=color)
        x += f.getlength(c) + tracking
    return im


FONT_DIR = "/usr/share/fonts/opentype/inter"
F_MED = os.path.join(FONT_DIR, "Inter-Medium.otf")
F_SEMI = os.path.join(FONT_DIR, "Inter-SemiBold.otf")
SERIF_I = os.path.join(HERE, "..", "..", "brand", "fonts", "CormorantGaramond-Italic[wght].ttf")


def _serif_italic(txt, size, color):
    from PIL import ImageFont
    f = ImageFont.truetype(SERIF_I, size)
    f.set_variation_by_axes([500])
    w = int(f.getlength(txt)) + 6
    im = Image.new("RGBA", (w, int(size * 1.4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), txt, font=f, fill=color)
    return im


def _bottle(d, x, y, h, frosted=(232, 228, 222), collar=GOLD):
    """Small unlabelled dropper bottle at (x, y=base)."""
    w = h * 0.42
    d.rounded_rectangle(_s([(x - w / 2, y - h * 0.62), (x + w / 2, y)]), radius=int(w * 0.35 * S), fill=frosted + (255,))
    d.rectangle(_s([(x - w * 0.28, y - h * 0.78), (x + w * 0.28, y - h * 0.62)]), fill=collar + (255,))
    d.rounded_rectangle(_s([(x - w * 0.16, y - h), (x + w * 0.16, y - h * 0.78)]), radius=int(w * 0.16 * S), fill=WHITE + (255,))
    d.line(_s([(x - w * 0.3, y - h * 0.5), (x - w * 0.3, y - h * 0.1)]), fill=(255, 255, 255, 200), width=2 * S)


def _box(d, x, y, w, h):
    d.rectangle(_s([(x - w / 2, y - h), (x + w / 2, y)]), fill=CREAM_D + (255,))
    d.rectangle(_s([(x - w / 2, y - h), (x + w / 2, y - h + 6)]), fill=GOLD + (255,))


def draw_booth(lights=1.0):
    img = Image.new("RGBA", (W * S, H * S), (28, 26, 25, 255))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = BACK

    # Hall backdrop gradient (dark, so the booth glows)
    g = np.linspace(0, 1, H * S)[:, None]
    hall = (np.array([40, 37, 35]) * (1 - g) + np.array([62, 58, 54]) * g).astype(np.uint8)
    img.paste(Image.fromarray(np.repeat(hall[:, None, :], W * S, axis=1).reshape(H * S, W * S, 3)).convert("RGBA"))
    d = ImageDraw.Draw(img)

    # Expo hall ceiling: truss lines and warm downlights above the header
    for k in range(9):
        yy = 60 + k * 46
        d.line(_s([(0, yy), (W, yy + 18)]), fill=(70, 66, 62, 255), width=2 * S)
    lamps = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamps)
    for k in range(6):
        xx = 90 + k * 180
        for r in range(3):
            yy = 120 + r * 120 + (k % 2) * 40
            gr = 7 + r * 3
            ld.ellipse(_s([(xx - gr, yy - gr * 0.5), (xx + gr, yy + gr * 0.5)]), fill=(255, 226, 170, 150))
    img.alpha_composite(lamps.filter(ImageFilter.GaussianBlur(3 * S)))
    # Aisle carpet in front of the booth
    d.polygon(_s([(0, FRONT_Y), (W, FRONT_Y), (W, H), (0, H)]), fill=(52, 48, 46, 255))
    d.line(_s([(0, FRONT_Y + 6), (W, FRONT_Y + 6)]), fill=GOLD + (160,), width=3 * S)

    # Floor (oak) with planks converging to the vanishing point
    d.polygon(_s([(x0, y1), (x1, y1), (W, FRONT_Y), (0, FRONT_Y)]), fill=FLOOR + (255,))
    for k in range(-6, 7):
        fx = 540 + k * 115
        bx = VP[0] + (fx - VP[0]) * (y1 - VP[1]) / (FRONT_Y - VP[1])
        d.line(_s([(bx, y1), (fx, FRONT_Y)]), fill=(196, 176, 150, 255), width=2 * S)
    for yy in (1260, 1360, 1470):
        d.line(_s([(0, yy), (W, yy)]), fill=(204, 186, 160, 120), width=1 * S)

    # Side walls: oak slats (left), shelves wall (right)
    d.polygon(_s([(0, 590), (x0, y0), (x0, y1), (0, FRONT_Y)]), fill=OAK + (255,))
    for k in range(1, 14):
        t = k / 14
        xa = x0 * t
        ya_top = 590 + (y0 - 590) * t
        ya_bot = FRONT_Y + (y1 - FRONT_Y) * t
        d.line(_s([(xa, ya_top), (xa, ya_bot)]), fill=OAK_D + (255,), width=3 * S)
    d.polygon(_s([(W, 590), (x1, y0), (x1, y1), (W, FRONT_Y)]), fill=CREAM_D + (255,))
    # brass shelves on the right wall (true perspective) with unlabelled bottles and boxes
    for j, f in enumerate((0.30, 0.50, 0.70)):
        yf, yb = 590 + f * (FRONT_Y - 590), y0 + f * (y1 - y0)
        ta, tb = 0.10, 0.95
        pa = (W + (x1 - W) * ta, yf + (yb - yf) * ta)
        pb = (W + (x1 - W) * tb, yf + (yb - yf) * tb)
        d.line(_s([pa, pb]), fill=GOLD + (255,), width=5 * S)
        for i in range(6):
            tt = ta + (tb - ta) * (i + 0.5) / 6
            bx, by = W + (x1 - W) * tt, yf + (yb - yf) * tt - 3
            scale = 1.0 - 0.55 * tt
            if (i + j) % 3 == 1:
                _box(d, bx, by, 46 * scale, 58 * scale)
            else:
                _bottle(d, bx, by, 86 * scale)

    # Back wall (cream) + backlit logo panel
    d.rectangle(_s([(x0, y0), (x1, y1)]), fill=CREAM + (255,))
    panel = (x0 + 70, y0 + 70, x1 - 70, y0 + 330)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle(_s([(panel[0] - 30, panel[1] - 30), (panel[2] + 30, panel[3] + 30)]), radius=40 * S,
                         fill=(255, 236, 200, int(140 * lights)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40 * S)))
    d.rounded_rectangle(_s([(panel[0], panel[1]), (panel[2], panel[3])]), radius=18 * S,
                        fill=tuple(int(c * (0.9 + 0.1 * lights)) for c in (252, 248, 240)) + (255,))
    logo = _logo(int(300 * S))
    _paste(img, logo, (x0 + x1) / 2 * S, (panel[1] + 110) * S)
    d.line(_s([((x0 + x1) / 2 - 60, panel[1] + 190), ((x0 + x1) / 2 + 60, panel[1] + 190)]), fill=GOLD + (255,), width=3 * S)
    tag = _serif_italic("Skincare, explained.", 44 * S, INK + (255,))
    _paste(img, tag, (x0 + x1) / 2 * S, (panel[1] + 235) * S)
    # gold base line + small plinth with plant on back wall
    d.line(_s([(x0, y1 - 120), (x1, y1 - 120)]), fill=GOLD + (200,), width=2 * S)

    # Header fascia (ink) with white logo + small caps
    d.rectangle(_s([(HEADER[0], HEADER[1]), (HEADER[2], HEADER[3])]), fill=INK + (255,))
    _paste(img, _logo(int(210 * S), dark=False), 540 * S, 515 * S)
    sub = _text("SKINCARE  ·  COMING SOON", 15 * S, GOLD + (255,), F_SEMI, tracking=5 * S)
    _paste(img, sub, 540 * S, 568 * S)
    d.line(_s([(0, HEADER[3]), (W, HEADER[3])]), fill=GOLD + (255,), width=3 * S)

    # Track spotlights + light cones onto the back wall
    cones = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(cones)
    for sx in (330, 540, 750):
        d.rounded_rectangle(_s([(sx - 14, HEADER[3] + 4), (sx + 14, HEADER[3] + 40)]), radius=6 * S, fill=(20, 20, 20, 255))
        cd.polygon(_s([(sx - 10, HEADER[3] + 40), (sx + 10, HEADER[3] + 40), (sx + 120, y1 - 60), (sx - 120, y1 - 60)]),
                   fill=(255, 240, 210, int(55 * lights)))
    img.alpha_composite(cones.filter(ImageFilter.GaussianBlur(26 * S)))

    # Plant (left, floor)
    px, py = 150, 1420
    d.rounded_rectangle(_s([(px - 45, py - 90), (px + 45, py)]), radius=12 * S, fill=WHITE + (255,))
    for a in range(-60, 61, 20):
        r = math.radians(a)
        d.ellipse(_s([(px + 120 * math.sin(r) - 26, py - 90 - 150 * math.cos(r) - 60),
                      (px + 120 * math.sin(r) + 26, py - 90 - 150 * math.cos(r) + 60)]), fill=(92, 120, 92, 255))

    base_hi = img
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Counter (white, gold top edge, logo on front, warm under-glow)
    cx0, cx1, ctop, cbot = 300, 780, 1150, 1400
    ug = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ug).ellipse(_s([(cx0 - 20, cbot - 30), (cx1 + 20, cbot + 50)]), fill=(255, 230, 190, int(90 * lights)))
    img.alpha_composite(ug.filter(ImageFilter.GaussianBlur(24 * S)))
    d.polygon(_s([(cx0 + 20, ctop - 26), (cx1 - 20, ctop - 26), (cx1, ctop), (cx0, ctop)]), fill=(236, 232, 226, 255))
    d.rectangle(_s([(cx0, ctop), (cx1, ctop + 10)]), fill=GOLD + (255,))
    d.rectangle(_s([(cx0, ctop + 10), (cx1, cbot)]), fill=WHITE + (255,))
    d.rectangle(_s([(cx0, cbot - 8), (cx1, cbot)]), fill=CREAM_D + (255,))
    _paste(img, _logo(int(150 * S)), 540 * S, 1285 * S)
    # testers on the counter
    for i, tx in enumerate((380, 425, 470)):
        _bottle(d, tx, ctop - 12, 62)
    # waitlist tablet on a stand
    d.polygon(_s([(640, ctop - 14), (690, ctop - 14), (700, ctop - 100), (630, ctop - 100)]), fill=(30, 30, 30, 255))
    d.rectangle(_s([(636, ctop - 96), (694, ctop - 20)]), fill=(250, 246, 238, 255))
    for qy in range(3):
        for qx in range(3):
            if (qx + qy) % 2 == 0:
                d.rectangle(_s([(648 + qx * 12, ctop - 80 + qy * 12), (656 + qx * 12, ctop - 72 + qy * 12)]), fill=INK + (255,))
    # mirror
    d.ellipse(_s([(520, ctop - 120), (580, ctop - 24)]), outline=GOLD + (255,), width=4 * S, fill=(214, 220, 226, 255))

    base = base_hi.resize((W, H), Image.LANCZOS)
    counter = img.resize((W, H), Image.LANCZOS)
    return base, counter


def compose(lights, base_lit, counter, behind=(), front=()):
    """Booth + people: `behind` sits between wall and counter (staff), `front` in front."""
    fr = base_lit.copy()
    for im, (x, y) in behind:
        fr.alpha_composite(im, (int(x), int(y)))
    fr.alpha_composite(counter)
    for im, (x, y) in front:
        fr.alpha_composite(im, (int(x), int(y)))
    if lights < 1:
        fr.alpha_composite(Image.new("RGBA", (W, H), (10, 9, 8, int(205 * (1 - lights)))))
    return fr


# --------------------------------------------------------------------------- people

def person(height=520, color=(128, 120, 114), alpha=225, reach=0.0, facing=1, accent=None, step=0.0):
    """Soft arch-viz silhouette built from round-capped strokes. reach 0..1 lifts the
    forward arm; step (-1..1) swings the legs for walking; accent tints the torso (staff apron)."""
    s = 3
    hh = height * s
    wid = int(hh * 0.62)
    im = Image.new("RGBA", (wid, hh + 6 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = color + (255,)
    c = wid / 2

    def stroke(p0, p1, w):
        d.line([p0, p1], fill=col, width=int(w))
        for p in (p0, p1):
            d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)

    head_w, head_h = hh * 0.105, hh * 0.13
    d.ellipse([c - head_w / 2, 0, c + head_w / 2, head_h], fill=col)
    neck_y, hip_y = hh * 0.15, hh * 0.53
    sh_w = hh * 0.21
    d.polygon([(c - sh_w / 2, neck_y + hh * 0.03), (c + sh_w / 2, neck_y + hh * 0.03),
               (c + hh * 0.08, hip_y), (c - hh * 0.08, hip_y)], fill=col)
    d.ellipse([c - sh_w / 2 - hh * 0.02, neck_y + hh * 0.005, c + sh_w / 2 + hh * 0.02, neck_y + hh * 0.08], fill=col)
    d.rectangle([c - hh * 0.025, head_h * 0.85, c + hh * 0.025, neck_y + hh * 0.03], fill=col)
    if accent:
        d.polygon([(c - hh * 0.07, neck_y + hh * 0.07), (c + hh * 0.07, neck_y + hh * 0.07),
                   (c + hh * 0.075, hip_y - hh * 0.01), (c - hh * 0.075, hip_y - hh * 0.01)], fill=accent + (255,))
    leg_w = hh * 0.068
    sw = step * hh * 0.06
    stroke((c - hh * 0.045, hip_y), (c - hh * 0.05 + sw, hh * 0.985), leg_w)
    stroke((c + hh * 0.045, hip_y), (c + hh * 0.05 - sw, hh * 0.985), leg_w)
    arm_w = hh * 0.048
    shx = sh_w / 2 + hh * 0.005
    back = (c - shx * facing, neck_y + hh * 0.05)
    stroke(back, (back[0] - facing * hh * 0.02 - sw * 0.5, hip_y + hh * 0.02), arm_w)
    fwd = (c + shx * facing, neck_y + hh * 0.05)
    ang = math.radians(10 + 80 * reach)
    hand = (fwd[0] + facing * math.sin(ang) * hh * 0.3, fwd[1] + math.cos(ang) * hh * 0.3)
    stroke(fwd, hand, arm_w)
    im = im.filter(ImageFilter.GaussianBlur(1.2 * s))
    a_ch = im.split()[3].point(lambda v: int(v * alpha / 255))
    im.putalpha(a_ch)
    return im.resize((im.width // s, im.height // s), Image.LANCZOS)


def bubble(lines, size=40, dark=False):
    """Rounded speech bubble with a small tail at bottom-left."""
    from PIL import ImageFont
    serif = os.path.join(HERE, "..", "..", "brand", "fonts", "CormorantGaramond[wght].ttf")
    f = ImageFont.truetype(serif, size)
    f.set_variation_by_axes([600])
    tw = max(f.getlength(l) for l in lines)
    lh = int(size * 1.15)
    pw, ph = int(tw + 64), int(lh * len(lines) + 40)
    im = Image.new("RGBA", (pw + 10, ph + 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill = (INK if dark else WHITE) + (250,)
    d.rounded_rectangle([0, 0, pw, ph], radius=28, fill=fill)
    d.polygon([(34, ph - 2), (70, ph - 2), (30, ph + 30)], fill=fill)
    for i, l in enumerate(lines):
        d.text(((pw - f.getlength(l)) / 2, 18 + i * lh), l, font=f, fill=(WHITE if dark else INK) + (255,))
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 90), (20, 28), im.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    sh.alpha_composite(im, (20, 20))
    return sh
