#!/usr/bin/env python3
"""Designed Instagram covers for the Building SPOT reels (1080x1920 JPG).

Usage:  python3 reels/covers.py           -> writes reels/dayNN/out/spot_dayNN_cover.jpg

One series style so the profile grid reads as a set: best frame of the reel,
cinematic grade + dark bottom, a "DAY NN" outline badge, one big serif hook,
an italic line, a gold rule and the white SPOT wordmark. All content sits in
the centre 1080x1350 area that the profile grid shows.
"""
import importlib.util
import os

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("day06_render", os.path.join(HERE, "day06", "render.py"))
d6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d6)
d3, kit = d6.d3, d6.kit

W, H = kit.W, kit.H
WHITE, INK, CREAM, GOLD = kit.WHITE, kit.INK, kit.CREAM, d6.GOLD
SAFE_TOP, SAFE_BOT = 285, 1635  # 4:5 grid crop
LOGO_WHITE = Image.open(os.path.join(HERE, "..", "brand", "spot_logo_white.png")).convert("RGBA")
LOGO_DARK = Image.open(os.path.join(HERE, "..", "brand", "spot_logo_dark.png")).convert("RGBA")


def grab(day, clip, t, defocus=0, blur=None):
    img = next(d3.footage_frames(clip, t, 0.1, 1.0, blur, footage_dir=os.path.join(HERE, day, "footage")))
    if defocus:
        img = img.filter(ImageFilter.GaussianBlur(defocus))
    return img


def cinematic(img, zoom=1.0, focus=(0.5, 0.5)):
    img = kit.ken_burns(img, 1.0, zoom, zoom, fx=focus[0], fy=focus[1])
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(0.95).convert("RGBA")
    yy = np.linspace(0, 1, H)[:, None]
    shade = np.clip((yy - 0.32) / 0.5, 0, 1) ** 1.2 * 0.85 + np.clip((0.2 - yy) / 0.2, 0, 1) * 0.45
    xx = np.linspace(-1, 1, W)[None, :]
    shade = np.clip(shade + 0.18 * xx ** 2, 0, 0.9)
    overlay = Image.new("RGBA", (W, H), (12, 9, 8, 0))
    overlay.putalpha(Image.fromarray((shade * 255).astype(np.uint8)))
    img.alpha_composite(overlay)
    return img


def badge(day, color=WHITE):
    txt = kit.text_layer([f"DAY {day}"], kit.F_SEMIBOLD, 40, color, tracking=9)
    pw, ph = txt.width + 64, txt.height + 26
    img = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    fill = (0, 0, 0, 0) if color == INK else (10, 8, 8, 110)  # soft dark fill on photo covers
    ImageDraw.Draw(img).rounded_rectangle([1, 1, pw - 2, ph - 2], radius=ph // 2, fill=fill,
                                          outline=color + (235,), width=3)
    img.alpha_composite(txt, ((pw - txt.width) // 2, 14))
    return img


def logo(width, dark=False):
    src = LOGO_DARK if dark else LOGO_WHITE
    return src.resize((width, round(src.height * width / src.width)), Image.LANCZOS)


def tight(img):
    """Crop a text layer to its visible pixels so layout math is exact."""
    return img.crop(img.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())


def place_box(fr, layer, cx, top=None, bottom=None):
    y = top if top is not None else bottom - layer.height
    fr.alpha_composite(layer, (int(cx - layer.width / 2), int(y)))


def compose(bg, day, big, line, big_size=300, dark=False):
    """Bottom-up layout inside the grid-safe area: logo, line, gold rule, big hook."""
    fr = bg.copy()
    col = INK if dark else WHITE
    shadow = (lambda im: im) if dark else (lambda im: kit.with_shadow(im, 18, 0.6))
    lg = logo(230, dark)
    place_box(fr, lg, W / 2, bottom=SAFE_BOT - 40)
    line_img = tight(d3.serif_layer([line], 78, col, weight=500, italic=True))
    line_bottom = SAFE_BOT - 40 - lg.height - 70
    place_box(fr, shadow(line_img), W / 2, bottom=line_bottom + 36)  # shadow pads 36px
    rule_y = line_bottom - line_img.height - 38
    kit.place(fr, Image.new("RGBA", (120, 3), GOLD + (255,)), W / 2, rule_y, rise=0)
    big_img = tight(d3.serif_layer(big, big_size, col, weight=600, line_gap=0.95))
    place_box(fr, shadow(big_img), W / 2, bottom=rule_y - 40 + 54)  # shadow pads 54px
    kit.place(fr, shadow(badge(day, col)), W / 2, SAFE_TOP + 110, rise=0)
    return fr.convert("RGB")


def cover_day01():
    bg = cinematic(grab("day01", "rejected_samples.mp4", 1.4, defocus=7), zoom=1.08)
    return compose(bg, "01", ["35"], "samples received.", big_size=360)


def cover_day02():
    bg = cinematic(d6.SHORT_IMG, zoom=1.05, focus=(0.5, 0.35))
    return compose(bg, "02", ["Only 6"], "made the shortlist.", big_size=250)


def cover_day03():
    bg = cinematic(grab("day03", "pipette_macro.mp4", 27.0), zoom=1.05, focus=(0.5, 0.2))
    return compose(bg, "03", ["The final", "cut."], "round two begins.", big_size=190)


def cover_day04():
    bg = cinematic(grab("day04", "road_trip.mp4", 6.0), zoom=1.04)
    return compose(bg, "04", ["15"], "factories visited.", big_size=360)


def cover_day05():
    bg = cinematic(grab("day05", "serum_application_pexels.mp4", 6.5), zoom=1.06, focus=(0.4, 0.4))
    return compose(bg, "05", ["Behind the", "formula."], "factories · testing · chemists.", big_size=180)


def cover_day07():
    bg = cinematic(d3_still("day07", "walking_hall.jpg"), zoom=1.18, focus=(0.5, 1.0))
    return compose(bg, "07", ["Beauty", "Asia."], "a day at the expo.", big_size=200)


def cover_day08():
    """The pour shot (text painted out, graded) with the Day 8 hook."""
    spec = importlib.util.spec_from_file_location("day08_render", os.path.join(HERE, "day08", "render.py"))
    d8 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d8)
    small, _ = d8.portrait("pour")
    bg = cinematic(d8.plate(small).resize((W, H), Image.LANCZOS), zoom=1.04, focus=(0.5, 0.3))
    return compose(bg, "08", ["What goes into", "one bottle?"], "the journey of a formula.", big_size=128)


def d3_still(day, name):
    img = Image.open(os.path.join(HERE, day, "footage", name)).convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x0, y0, x0 + W, y0 + H))


def cover_day06():
    """Cream data cover: the 35-dot grid, six gold, '29 no's.' in ink."""
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    kit.place(fr, badge("06", INK), W / 2, SAFE_TOP + 110, rise=0)
    big = tight(d3.serif_layer(["29 no's."], 190, INK, weight=600))
    place_box(fr, big, W / 2, top=SAFE_TOP + 200)
    cols, rows, gap = d6.COLS, d6.ROWS, 112
    x0 = (W - (cols - 1) * gap) / 2
    y0 = SAFE_TOP + 200 + big.height + 80
    faded = d6.dot_sprite(28, (196, 186, 175))
    gold = d6.dot_sprite(34, GOLD, glow=True)
    for idx in range(cols * rows):
        if idx not in d6.CHOSEN:
            d6.paste_center(fr, faded, x0 + (idx % cols) * gap, y0 + (idx // cols) * gap)
    for idx in d6.CHOSEN:
        d6.paste_center(fr, gold, x0 + (idx % cols) * gap, y0 + (idx // cols) * gap)
    line = tight(d3.serif_layer(["and only 6 yes."], 74, GOLD, weight=500, italic=True))
    place_box(fr, line, W / 2, top=y0 + (rows - 1) * gap + 110)
    place_box(fr, logo(170, dark=True), W / 2, bottom=SAFE_BOT - 30)
    return fr.convert("RGB")


COVERS = {"01": cover_day01, "02": cover_day02, "03": cover_day03, "04": cover_day04, "05": cover_day05, "06": cover_day06, "07": cover_day07, "08": cover_day08}


def main():
    for day, fn in COVERS.items():
        out = os.path.join(HERE, f"day{day}", "out", f"spot_day{day}_cover.jpg")
        fn().save(out, quality=94)
        print("wrote", out)


if __name__ == "__main__":
    main()
