#!/usr/bin/env python3
"""Render the SPOT "Day 5" Instagram Reel: behind the formula.

Usage:  python3 reels/day05/render.py
Output: reels/day05/out/spot_day05_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

Three chapters — 01 factory visits, 02 formulation testing, 03 chemist
consultations — in the series look (Cormorant headlines, gold numerals, cream
editorial cards). Factory photos sit in framed cards (they are small, so they
are never stretched full-screen); the chemist chapter is a drawn motion graphic.
"""
import importlib.util
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.join(HERE, "..")
_spec = importlib.util.spec_from_file_location("day03_render", os.path.join(REELS, "day03", "render.py"))
d3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d3)
kit = d3.kit

FOOTAGE = os.path.join(HERE, "footage")
OUT = os.path.join(HERE, "out")
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = d3.XFADE, d3.LAST_XFADE
INK, CREAM, WHITE = kit.INK, kit.CREAM, kit.WHITE
GOLD = (176, 141, 87)
MUTED = (120, 112, 104)
place, appear = kit.place, kit.appear
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer

TAG = kit.make_tag("05")
TAG_INK = kit.text_layer(["DAY 05"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)


def frames(day, name, start, dur, speed=1.0):
    return d3.footage_frames(name, start, dur, speed, None, footage_dir=os.path.join(REELS, day, "footage"))


def chapter(num, label, dark=False):
    """Gold italic numeral + spaced caps label, e.g. '01  FACTORY VISITS'."""
    col = INK if dark else WHITE
    n = serif_layer([num], 92, GOLD, weight=500, italic=True)
    lb = kit.text_layer([label], kit.F_SEMIBOLD, 30, col, tracking=8)
    img = Image.new("RGBA", (n.width + 26 + lb.width, max(n.height, lb.height)), (0, 0, 0, 0))
    img.alpha_composite(n, (0, 0))
    img.alpha_composite(lb, (n.width + 26, (img.height - lb.height) // 2 - 6))
    return img if dark else kit.with_shadow(img, 12, 0.6)


# --------------------------------------------------------------------------- 1. hook

H1 = title(["What goes into", "one drop?"], 110)


def s_hook(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1, W / 2, 500, appear(t, 0.25, 0.6), rise=30)


# --------------------------------------------------------------------------- 2. 01 factory visits (real footage)

CH1 = chapter("01", "FACTORY VISITS")
H2 = title(["15 factories.", "Every one in person."], 92)


def s_arrive(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, CH1, W / 2, 420, appear(t, 0.1), rise=20)
    place(fr, H2, W / 2, 590, appear(t, 0.5))


# --------------------------------------------------------------------------- 3. factory photos (framed cards)

def load_photo(name, blur_boxes=()):
    img = Image.open(os.path.join(FOOTAGE, name)).convert("RGB")
    for box in blur_boxes:
        img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(6)), box[:2])
    return ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.05)).enhance(0.95)


PHOTOS = [
    (load_photo("production_line.png"), ["Production lines,", "checked up close."]),
    (load_photo("raw_materials.png"), ["Raw materials,", "inspected at the source."]),
    (load_photo("tube_filling.png", [(45, 140, 100, 185), (195, 160, 228, 196), (82, 190, 110, 226)]),
     ["Filling and hygiene,", "seen with our own eyes."]),  # other brand's tube text blurred
]
FRAME_W, FRAME_H, FRAME_Y = 860, 1000, 520
PHOTO_DUR = 1.75
CAPS = [serif_layer(c, 64, INK, weight=600) for _, c in PHOTOS]


def framed(img, t_local, dur):
    """Photo cover-cropped into the frame with a slow push-in."""
    z = 1.0 + 0.08 * kit.ease_in_out(t_local / dur)
    s = max(FRAME_W / img.width, FRAME_H / img.height) * z
    big = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (big.width - FRAME_W) // 2, (big.height - FRAME_H) // 2
    return big.crop((x0, y0, x0 + FRAME_W, y0 + FRAME_H))


SHADOW = Image.new("RGBA", (FRAME_W + 120, FRAME_H + 120), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW).rectangle([60, 72, 60 + FRAME_W, 72 + FRAME_H], fill=(60, 40, 30, 70))
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(24))
CH1_INK = chapter("01", "FACTORY VISITS", dark=True)


def s_photos(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, CH1_INK, W / 2, 380, 1, rise=0)
    fx = (W - FRAME_W) // 2
    fr.alpha_composite(SHADOW, (fx - 60, FRAME_Y - 60))
    i = min(int(t / PHOTO_DUR), len(PHOTOS) - 1)
    tl = t - i * PHOTO_DUR
    cur = framed(PHOTOS[i][0], tl, PHOTO_DUR).convert("RGBA")
    if i > 0 and tl < 0.3:  # quick dissolve between photos
        prev = framed(PHOTOS[i - 1][0], PHOTO_DUR + tl, PHOTO_DUR).convert("RGBA")
        cur = Image.blend(prev, cur, tl / 0.3)
    fr.alpha_composite(cur, (fx, FRAME_Y))
    ImageDraw.Draw(fr).rectangle([fx, FRAME_Y, fx + FRAME_W - 1, FRAME_Y + FRAME_H - 1], outline=WHITE + (255,), width=10)
    place(fr, CAPS[i], W / 2, FRAME_Y + FRAME_H + 120, appear(tl, 0.05, 0.35) if i else appear(t, 0.2), rise=16)
    return fr


# --------------------------------------------------------------------------- 4–5. 02 formulation testing

CH2 = chapter("02", "FORMULATION TESTING")
H4 = title(["Batch after batch,", "drop by drop."], 92)


def s_pipette(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, CH2, W / 2, 420, appear(t, 0.1), rise=20)
    place(fr, H4, W / 2, 590, appear(t, 0.5))


H5_WORDS = ["How it absorbs.", "How it feels.", "How it lasts."]
H5_LAYERS = [kit.with_shadow(serif_layer([w], 84), 14, 0.6) for w in H5_WORDS]


def s_apply(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    for i, lay in enumerate(H5_LAYERS):
        place(fr, lay, W / 2, 420 + i * 115, appear(t, 0.15 + i * 0.55), rise=24)


# --------------------------------------------------------------------------- 6. 03 chemist consultations (motion graphic)

CH3_INK = chapter("03", "CHEMIST CONSULTATIONS", dark=True)
C3_H = serif_layer(["Every ingredient", "questioned."], 84, INK, weight=600)
C3_K = serif_layer(["Every claim checked with chemists."], 54, INK, weight=500, italic=True)
CHEM_DUR = 4.4


def _hex(cx, cy, r, rot=0.0):
    return [(cx + r * math.cos(math.radians(60 * k + 30 + rot)), cy + r * math.sin(math.radians(60 * k + 30 + rot)))
            for k in range(6)]


# A simple drawn molecule: two fused rings + side chains (decorative, not a real formula).
_R = 118
_C1 = (W / 2 - _R * math.sqrt(3) / 2, 1120)
_C2 = (W / 2 + _R * math.sqrt(3) / 2, 1120)
_H1, _H2 = _hex(*_C1, _R), _hex(*_C2, _R)
SEGMENTS = []
for poly in (_H1, _H2):
    for k in range(6):
        SEGMENTS.append((poly[k], poly[(k + 1) % 6]))
SEGMENTS += [(_H1[3], (_H1[3][0] - 90, _H1[3][1] + 52)), ((_H1[3][0] - 90, _H1[3][1] + 52), (_H1[3][0] - 180, _H1[3][1])),
             (_H2[0], (_H2[0][0] + 90, _H2[0][1] - 52)), ((_H2[0][0] + 90, _H2[0][1] - 52), (_H2[0][0] + 90, _H2[0][1] - 156))]
INNER = [(_C1, _R * 0.6), (_C2, _R * 0.6)]  # aromatic circles
NODES = sorted({p for seg in SEGMENTS for p in seg})
DRAW0, DRAW1 = 0.5, 2.3


def s_chem(t, T):
    s = 3
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, CH3_INK, W / 2, 400, appear(t, 0.05), rise=16)
    place(fr, C3_H, W / 2, 600, appear(t, 0.3))
    # Molecule drawn stroke by stroke (supersampled for clean lines).
    layer = Image.new("RGBA", (W * s, H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    k = (t - DRAW0) / (DRAW1 - DRAW0)
    n = len(SEGMENTS)
    for i, (a, b) in enumerate(SEGMENTS):
        p = min(1.0, max(0.0, k * n - i))
        if p <= 0:
            break
        e = (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p)
        d.line([(a[0] * s, a[1] * s), (e[0] * s, e[1] * s)], fill=GOLD + (255,), width=5 * s)
    ring = appear(t, DRAW1 - 0.2, 0.5)
    for (cx, cy), r in INNER:
        if ring > 0:
            d.arc([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], -90, -90 + 360 * ring,
                  fill=GOLD + (200,), width=3 * s)
    if k >= 1:
        pop = appear(t, DRAW1, 0.4)
        for x, y in NODES:
            rr = 9 * pop
            d.ellipse([(x - rr) * s, (y - rr) * s, (x + rr) * s, (y + rr) * s], fill=INK + (255,))
    fr.alpha_composite(layer.resize((W, H), Image.LANCZOS))
    place(fr, C3_K, W / 2, 1420, appear(t, DRAW1 + 0.3))
    return fr


# --------------------------------------------------------------------------- 7. the standard

H7 = title(["All this,", "before one drop", "reaches you."], 96)


def s_standard(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H7, W / 2, 540, appear(t, 0.2, 0.6))


# --------------------------------------------------------------------------- 8. end card

E_NEXT = serif_layer(["Day 6: what 29 no's look like."], 58, INK, weight=500, italic=True)


def s_end(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    k = appear(t, 0.1, 0.9)
    place(fr, kit.LOGO, W / 2, 690, k, rise=0, scale=0.94 + 0.06 * k)
    place(fr, E_NEXT, W / 2, 900, appear(t, 0.7))
    place(fr, d3.E_SOON, W / 2, 985, appear(t, 0.9))
    place(fr, kit.E_RULE, W / 2, 1080, appear(t, 1.2), rise=0)
    place(fr, d3.E_FOLLOW, W / 2, 1165, appear(t, 1.4))
    place(fr, kit.E_HANDLE, W / 2, 1240, appear(t, 1.6))
    return fr


# --------------------------------------------------------------------------- timeline

SCENES = [
    dict(shots=[("day05", "serum_application_pexels.mp4", 0.8, 3.2, 0.8)], overlay=s_hook, zoom=(1.0, 1.05)),
    dict(shots=[("day05", "factory_arrival.mp4", 3.9, 1.6, 1.0), ("day05", "factory_arrival.mp4", 16.0, 1.6, 1.0)],
         overlay=s_arrive, zoom=(1.0, 1.06)),
    dict(card=s_photos, dur=PHOTO_DUR * len(PHOTOS)),
    dict(shots=[("day03", "pipette_macro.mp4", 15.0, 3.0, 0.75)], overlay=s_pipette, zoom=(1.0, 1.06)),
    dict(shots=[("day05", "serum_application_pexels.mp4", 12.0, 3.0, 0.9)], overlay=s_apply, zoom=(1.0, 1.05)),
    dict(card=s_chem, dur=CHEM_DUR),
    dict(shots=[("day05", "serum_application_pexels.mp4", 4.0, 2.8, 0.7)], overlay=s_standard, zoom=(1.06, 1.12)),
    dict(card=s_end, dur=4.2),
]

CUES = dict(
    photo_changes=[i * PHOTO_DUR for i in range(len(PHOTOS))],
    apply_words=[0.15 + i * 0.55 for i in range(3)],
    chem=(DRAW0, DRAW1),
)


def scene_dur(sc):
    return sc.get("dur") or sum(s[3] for s in sc["shots"])


def scene_timing():
    durs = [scene_dur(sc) for sc in SCENES]
    starts, offset = [0.0], 0.0
    for i in range(1, len(durs)):
        xf = LAST_XFADE if i == len(durs) - 1 else XFADE
        offset += durs[i - 1] - xf
        starts.append(offset)
    return starts, offset + durs[-1]


def render_scene(sc, path):
    enc = kit.encoder(path)
    T = scene_dur(sc)
    n = int(round(T * FPS))
    if "card" in sc:
        src = (None for _ in range(n))
    else:
        src = (img for day, clip, st, d, sp in sc["shots"] for img in frames(day, clip, st, d, sp))
    for f, img in enumerate(src):
        t = f / FPS
        if "card" in sc:
            fr = sc["card"](t, T)
        else:
            fr = kit.ken_burns(img, t / T, *sc["zoom"]).convert("RGBA")
            sc["overlay"](fr, t, T)
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()


def main():
    _sspec = importlib.util.spec_from_file_location("day05_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day05_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        render_scene(sc, p)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_day05_music.wav"))
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
    for name, audio in [("spot_day05_reel.mp4", ["-i", score_path]),
                        ("spot_day05_reel_no_music.mp4",
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
