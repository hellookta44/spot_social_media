#!/usr/bin/env python3
"""Render the SPOT "Day 2" Instagram Reel: how a sample gets a yes (1080x1920, 30 fps).

Usage:  python3 reels/day02/render.py
Output: reels/day02/out/spot_day02_reel.mp4 (+ _no_music, music .wav, cover .jpg)

Reuses the Day 1 look (fonts, tag, stamps, end card) from reels/day01/render.py.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "day01"))
import render as kit  # noqa: E402  (Day 1 helpers; its footage dir has the dropper clip)

FOOTAGE = os.path.join(HERE, "footage")
OUT = os.path.join(HERE, "out")
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = kit.XFADE, kit.LAST_XFADE
INK, CREAM, WHITE, STAMP_RED = kit.INK, kit.CREAM, kit.WHITE, kit.STAMP_RED
appear, place, headline, sub = kit.appear, kit.place, kit.headline, kit.sub

TAG = kit.make_tag("02")


# --------------------------------------------------------------------------- stills

def prep_still(name, blur_boxes=()):
    """Load a photo, blur private/brand-revealing areas, cover-crop to 1080x1920, grade."""
    img = Image.open(os.path.join(FOOTAGE, name)).convert("RGB")
    for box in blur_boxes:
        region = img.crop(box).filter(ImageFilter.GaussianBlur(14))
        img.paste(region, box[:2])
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((x0, y0, x0 + W, y0 + H))
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(0.92)
    return img


# Laptop screen (order page) blurred on the pouch photo; "GEL Cleanser" label blurred on the lineup.
POUCH = prep_still("sample_pouch.jpg", blur_boxes=[(0, 260, 275, 625)])
SHORTLIST = prep_still("shortlist.jpg", blur_boxes=[(306, 708, 404, 762)])


# --------------------------------------------------------------------------- scene 1: the pouch

S1_H = headline(["Sample #17582."], 92)
S1_S = sub(["Every sample arrives like this.", "No brand. No name. Just a code."], 44)
S1_BOT = kit.gradient(0.7, 1100, bottom=True)


def s1_overlay(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(S1_BOT)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, S1_H, W / 2, 1180, appear(t, 0.15))
    place(fr, S1_S, W / 2, 1340, appear(t, 1.0))


# --------------------------------------------------------------------------- scene 2: checklist

def make_dark_tag():
    day = kit.text_layer(["DAY 02"], kit.F_SEMIBOLD, 64, INK, tracking=10)
    line = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)
    w = max(day.width, line.width)
    img = Image.new("RGBA", (w, day.height + line.height + 6), (0, 0, 0, 0))
    img.alpha_composite(day, ((w - day.width) // 2, 0))
    img.alpha_composite(line, ((w - line.width) // 2, day.height + 6))
    return img


TAG_INK = make_dark_tag()
C_TITLE = kit.text_layer(["Before any formulation gets a yes,", "it has to pass all five:"],
                         kit.F_DISPLAY_LIGHT, 58, INK, line_gap=1.2)
CHECKS = ["Texture", "Absorption", "Feel on skin", "Ingredients", "Fragrance"]
C_ITEMS = [kit.text_layer([c], kit.F_DISPLAY_LIGHT, 64, INK, align="left") for c in CHECKS]
FAIL_INDEX = 4
C_FOOT = kit.text_layer(["One fail and it's out."], kit.F_MEDIUM, 46, INK)
C_STAMP = kit.stamp("REJECTED", 58, angle=-9)
ITEM_T0, ITEM_STEP = 0.55, 0.42
LIST_X, LIST_Y, ROW = 250, 760, 128


def mark(ok, progress, size=64):
    """Animated tick (ink) or cross (red) inside a thin circle."""
    s = 4
    img = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (INK if ok else STAMP_RED) + (255,)
    d.ellipse([s, s, size * s - s, size * s - s], outline=col, width=3 * s)
    k = kit.ease_out(progress)
    lw = 5 * s
    if ok:
        p0, p1, p2 = (0.28, 0.52), (0.44, 0.68), (0.74, 0.34)
        seg = k * 2
        a = (p0[0] + (p1[0] - p0[0]) * min(seg, 1), p0[1] + (p1[1] - p0[1]) * min(seg, 1))
        d.line([tuple(v * size * s for v in p0), tuple(v * size * s for v in a)], fill=col, width=lw)
        if seg > 1:
            b = (p1[0] + (p2[0] - p1[0]) * (seg - 1), p1[1] + (p2[1] - p1[1]) * (seg - 1))
            d.line([tuple(v * size * s for v in p1), tuple(v * size * s for v in b)], fill=col, width=lw)
    else:
        for (x0, y0, x1, y1) in ((0.3, 0.3, 0.7, 0.7), (0.7, 0.3, 0.3, 0.7)):
            d.line([(x0 * size * s, y0 * size * s),
                    ((x0 + (x1 - x0) * k) * size * s, (y0 + (y1 - y0) * k) * size * s)],
                   fill=col, width=lw)
    return img.resize((size, size), Image.LANCZOS)


def s2_frame(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 215, 1, rise=0)
    place(fr, C_TITLE, W / 2, 480, appear(t, 0.05))
    stamp_t = ITEM_T0 + ITEM_STEP * len(CHECKS) + 0.15
    for i, item in enumerate(C_ITEMS):
        t0 = ITEM_T0 + i * ITEM_STEP
        p = appear(t, t0, 0.3)
        if p <= 0:
            continue
        y = LIST_Y + i * ROW
        place(fr, item, LIST_X + 110 + item.width / 2, y, p, rise=20)
        if t >= t0 + 0.18:
            m = mark(i != FAIL_INDEX, (t - t0 - 0.18) / 0.25)
            fr.alpha_composite(m, (LIST_X, int(y - m.height / 2)))
    if t >= stamp_t:
        k = kit.ease_out((t - stamp_t) / 0.16)
        place(fr, C_STAMP, 860, LIST_Y + ROW * 4, min(1, k * 1.5), rise=0, scale=1.6 - 0.6 * k)
    place(fr, C_FOOT, W / 2, LIST_Y + ROW * 5 + 120, appear(t, stamp_t + 0.35))
    return fr


# --------------------------------------------------------------------------- scene 3: on skin

def _skin_base():
    """Warm skin-tone backdrop with soft pore texture and vignette."""
    import numpy as np
    y = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([236, 200, 172]), np.array([214, 166, 136])
    img = top * (1 - y) + bot * y
    img = np.repeat(img, W, axis=1)
    rng = np.random.default_rng(3)
    noise = Image.fromarray((rng.standard_normal((H // 3, W // 3)) * 40 + 128).clip(0, 255).astype("uint8"))
    noise = np.array(noise.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2)), dtype=float)
    img += ((noise - 128) / 128 * 7)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / W) ** 2 + ((yy - H * 0.55) / H) ** 2
    img *= (1 - 0.55 * v)[..., None]
    return Image.fromarray(img.clip(0, 255).astype("uint8")).convert("RGBA")


SKIN = _skin_base()
DROP_X, LAND_Y = W / 2, 1080
T_FALL, T_LAND, T_SWIPE, T_GONE = 0.35, 0.75, 1.55, 3.0


def blob(w, h, alpha):
    """Glossy translucent product blob: soft body, darker rim, specular highlight."""
    pad = 60
    img = Image.new("RGBA", (int(w) + 2 * pad, int(h) + 2 * pad), (0, 0, 0, 0))
    box = [pad, pad, pad + w, pad + h]
    shadow = Image.new("L", img.size, 0)
    ImageDraw.Draw(shadow).ellipse([box[0] + 6, box[1] + 14, box[2] + 6, box[3] + 14], fill=int(90 * alpha))
    img.paste((120, 70, 50, 255), (0, 0), shadow.filter(ImageFilter.GaussianBlur(14)))
    body = Image.new("L", img.size, 0)
    ImageDraw.Draw(body).ellipse(box, fill=int(150 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", img.size, v) for v in (250, 246, 240)]
                                    + [body.filter(ImageFilter.GaussianBlur(5))]))
    hl = Image.new("L", img.size, 0)
    ImageDraw.Draw(hl).ellipse([box[0] + w * 0.22, box[1] + h * 0.16, box[0] + w * 0.5, box[1] + h * 0.38],
                               fill=int(235 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", img.size, 255)] * 3
                                    + [hl.filter(ImageFilter.GaussianBlur(6))]))
    return img


def drop(alpha=1.0, size=70):
    """Falling teardrop."""
    pad = 30
    img = Image.new("RGBA", (size + 2 * pad, int(size * 1.5) + 2 * pad), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([pad, pad + size * 0.5, pad + size, pad + size * 1.5], fill=int(170 * alpha))
    d.polygon([(pad + size * 0.5, pad), (pad + size * 0.08, pad + size * 0.9),
               (pad + size * 0.92, pad + size * 0.9)], fill=int(170 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", img.size, 250)] * 3 + [m.filter(ImageFilter.GaussianBlur(3))]))
    hl = Image.new("L", img.size, 0)
    ImageDraw.Draw(hl).ellipse([pad + size * 0.25, pad + size * 0.75, pad + size * 0.45, pad + size * 1.05],
                               fill=int(230 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", img.size, 255)] * 3 + [hl.filter(ImageFilter.GaussianBlur(3))]))
    return img


SK_H = headline(["Then it goes on skin."], 80)
SK_S = sub(["How it spreads. How it absorbs.", "How it feels after."], 44)


def skin_frame(t, T):
    fr = SKIN.copy()
    fr.alpha_composite(kit.TOP_GRAD)
    if T_FALL <= t < T_LAND:
        k = ((t - T_FALL) / (T_LAND - T_FALL)) ** 2
        dimg = drop(size=90)
        y = 780 + (LAND_Y - 780) * k
        fr.alpha_composite(dimg, (int(DROP_X - dimg.width / 2), int(y - dimg.height)))
    elif t >= T_LAND:
        land = kit.ease_out((t - T_LAND) / 0.45)
        w, h = 90 + 250 * land, 50 + 100 * land
        alpha = 1.0
        if t >= T_SWIPE:  # finger-swipe: stretch sideways, thin out, absorb
            k = kit.ease_in_out((t - T_SWIPE) / (T_GONE - T_SWIPE))
            w, h = 340 + 380 * k, 150 - 90 * k
            alpha = 1 - 0.85 * k
        b = blob(w, h, alpha)
        cx = DROP_X + (90 * kit.ease_in_out((t - T_SWIPE) / (T_GONE - T_SWIPE)) if t >= T_SWIPE else 0)
        fr.alpha_composite(b, (int(cx - b.width / 2), int(LAND_Y - h / 2 - 60)))
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, SK_H, W / 2, 470, appear(t, 0.1))
    place(fr, SK_S, W / 2, 640, appear(t, 0.9))
    return fr


# --------------------------------------------------------------------------- scene 4: dropper

S3_H = headline(["Pass every test?"], 86)
S3_S = sub(["Then it earns a second look."], 48)


def s3_overlay(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, S3_H, W / 2, 470, appear(t, 0.15))
    place(fr, S3_S, W / 2, 600, appear(t, 0.8))


# --------------------------------------------------------------------------- scene 5: shortlist countdown

S4_PRE = headline(["From 700+ samples"], 64)
S4_LABEL = sub(["made the shortlist."], 54)
COUNT_FROM, COUNT_TO = 700, 6


def s4_overlay(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, S4_PRE, W / 2, 420, appear(t, 0.1))
    k = kit.ease_out((t - 0.4) / 1.8)
    n = round(COUNT_FROM + (COUNT_TO - COUNT_FROM) * k)
    big = kit.with_shadow(kit.text_layer([f"only {n}" if k >= 1 else str(n)],
                                         kit.F_DISPLAY_LIGHT, 220, WHITE), 18, 0.55)
    pop = 1.0 + 0.06 * max(0.0, 1 - (t - 2.2) / 0.25) if t > 2.2 else 1.0
    place(fr, big, W / 2, 610, appear(t, 0.35, 0.3), rise=20, scale=pop)
    place(fr, S4_LABEL, W / 2, 790, appear(t, 2.25))


# --------------------------------------------------------------------------- scene 6: the question

S5_H = headline(["Only the best will", "carry the SPOT name."], 74)
S5_S = sub(["Which one would you pick?", "Tell us in the comments."], 46)


def s5_overlay(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, S5_H, W / 2, 470, appear(t, 0.15))
    place(fr, S5_S, W / 2, 680, appear(t, 1.1))


# --------------------------------------------------------------------------- scene 7: end card

E_LINE1 = kit.text_layer(["Day 3: the final cut."], kit.F_DISPLAY_LIGHT, 50, INK)
E_LINE2 = kit.text_layer(["SKINCARE PRODUCTS · COMING SOON"], kit.F_MEDIUM, 28, (120, 112, 104), tracking=6)
E_FOLLOW = kit.text_layer(["Follow the journey"], kit.F_DISPLAY_LIGHT, 40, INK)


def s6_frame(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    k = appear(t, 0.1, 0.9)
    place(fr, kit.LOGO, W / 2, 700, k, rise=0, scale=0.94 + 0.06 * k)
    place(fr, E_LINE1, W / 2, 900, appear(t, 0.7))
    place(fr, E_LINE2, W / 2, 975, appear(t, 0.9))
    place(fr, kit.E_RULE, W / 2, 1080, appear(t, 1.2), rise=0)
    place(fr, E_FOLLOW, W / 2, 1170, appear(t, 1.4))
    place(fr, kit.E_HANDLE, W / 2, 1240, appear(t, 1.6))
    return fr


# --------------------------------------------------------------------------- timeline

SCENES = [
    dict(still=POUCH, dur=3.4, overlay=s1_overlay, zoom=(1.0, 1.1), focus=(0.49, 0.3)),
    dict(card=s2_frame, dur=4.4),
    dict(card=skin_frame, dur=3.6),
    dict(clip=("serum_dropper.mp4", 1.6, 3.4), overlay=s3_overlay, zoom=(1.04, 1.1)),
    dict(still=SHORTLIST, dur=3.6, overlay=s4_overlay, zoom=(1.0, 1.06), focus=(0.5, 0.7)),
    dict(still=SHORTLIST, dur=3.4, overlay=s5_overlay, zoom=(1.14, 1.2), focus=(0.55, 0.75)),
    dict(card=s6_frame, dur=4.2),
]

# Cue times inside scenes, used by the score.
CUES = dict(
    check_times=[ITEM_T0 + i * ITEM_STEP + 0.18 for i in range(len(CHECKS))],
    fail_index=FAIL_INDEX,
    stamp=ITEM_T0 + ITEM_STEP * len(CHECKS) + 0.15,
    drop_land=T_LAND,
    swipe=T_SWIPE,
    count=(0.4, 2.2),
)


def scene_dur(sc):
    return sc["clip"][2] if "clip" in sc else sc["dur"]


def scene_timing():
    durs = [scene_dur(sc) for sc in SCENES]
    starts, offset = [0.0], 0.0
    for i in range(1, len(durs)):
        xf = LAST_XFADE if i == len(durs) - 1 else XFADE
        offset += durs[i - 1] - xf
        starts.append(offset)
    return starts, offset + durs[-1]


def render_scene(sc, path, cover_path=None, cover_t=None):
    enc = kit.encoder(path)
    T = scene_dur(sc)
    n = int(round(T * FPS))
    if "card" in sc:
        frames = (None for _ in range(n))
    elif "still" in sc:
        frames = (sc["still"] for _ in range(n))
    else:
        frames = kit.footage_frames(*sc["clip"])
    for f, img in enumerate(frames):
        t = f / FPS
        if "card" in sc:
            fr = sc["card"](t, T)
        else:
            fx, fy = sc.get("focus", (0.5, 0.5))
            fr = kit.ken_burns(img, t / T, *sc["zoom"], fx=fx, fy=fy).convert("RGBA")
            sc["overlay"](fr, t, T)
        if cover_path and abs(t - cover_t) < 0.5 / FPS:
            fr.convert("RGB").save(cover_path, quality=92)
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()


def main():
    import score

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day02_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        # Cover = the countdown landing on "only 6".
        cover = os.path.join(OUT, "spot_day02_cover.jpg") if i == 4 else None
        render_scene(sc, p, cover, cover_t=3.0)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_day02_music.wav"))
    print(f"wrote {score_path}")

    inputs = []
    for p in parts:
        inputs += ["-i", p]
    chain, last = [], "[0:v]"
    for i in range(1, len(parts)):
        xf = LAST_XFADE if i == len(parts) - 1 else XFADE
        out = f"[v{i}]"
        chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={xf}:offset={starts[i]:.3f}{out}")
        last = out
    video = os.path.join(tmp, "video.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
         "-map", last, "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-r", str(FPS), video],
        check=True)
    for name, audio in [("spot_day02_reel.mp4", ["-i", score_path]),
                        ("spot_day02_reel_no_music.mp4",
                         ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"])]:
        final = os.path.join(OUT, name)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", video, *audio, "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
             "-shortest", final],
            check=True)
        print(f"wrote {final} ({total:.1f}s)")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
