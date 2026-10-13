#!/usr/bin/env python3
"""Render the SPOT "Day 5" Instagram Reel: what 700 no's look like.

Usage:  python3 reels/day05/render.py
Output: reels/day05/out/spot_day05_reel.mp4 (+ _no_music, music .wav, cover .jpg)

Built from earlier footage (new crops / unused sections) plus a data motion
graphic: 700 dots, one per rejected sample, then the 6 that made the shortlist.
"""
import importlib.util
import math
import os
import random
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

OUT = os.path.join(HERE, "out")
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = d3.XFADE, d3.LAST_XFADE
INK, CREAM, WHITE = kit.INK, kit.CREAM, kit.WHITE
GOLD = (176, 141, 87)
place, appear = kit.place, kit.appear
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer

TAG = kit.make_tag("05")
REJECTED, SHORTLIST = 700, 6


def frames(day, name, start, dur, speed=1.0):
    return d3.footage_frames(name, start, dur, speed, None, footage_dir=os.path.join(REELS, day, "footage"))


# --------------------------------------------------------------------------- scene 1: hook

H1 = title(["What do", "700 no's look like?"], 100)


def s_hook(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1, W / 2, 500, appear(t, 0.2, 0.6), rise=30)


# --------------------------------------------------------------------------- scene 2: 700 dots

COLS, ROWS = 25, 28
GAP = 36
GX0 = (W - (COLS - 1) * GAP) / 2
GY0 = 640
DOT_R = 11
FILL0, FILL1 = 0.5, 4.2          # dots appear between these times
FADE0 = 5.0                      # rejected dots fade, 6 turn gold
GATHER0, GATHER1 = 6.3, 7.4      # the 6 glide to the centre
CARD_DUR = 9.2

rnd = random.Random(5)
ORDER = list(range(COLS * ROWS))
rnd.shuffle(ORDER)               # dots land in a scattered order, like samples arriving
APPEAR_AT = {}
for rank, idx in enumerate(ORDER):
    k = rank / (len(ORDER) - 1)
    APPEAR_AT[idx] = FILL0 + (FILL1 - FILL0) * (k ** 0.55)   # slow start, then a rush
CHOSEN = rnd.sample(range(COLS * ROWS), SHORTLIST)


def dot_sprite(r, color, alpha=255, glow=False):
    s = 4
    pad = r * 2 if glow else 2
    size = (2 * r + 2 * pad) * s
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([c - r * 1.9 * s, c - r * 1.9 * s, c + r * 1.9 * s, c + r * 1.9 * s],
                                  fill=color + (90,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * s * 0.7)))
    d.ellipse([c - r * s, c - r * s, c + r * s, c + r * s], fill=color + (alpha,))
    return img.resize((size // s, size // s), Image.LANCZOS)


DOT = dot_sprite(DOT_R, (120, 108, 98))
DOT_FADED = dot_sprite(DOT_R, (205, 196, 186))
DOT_GOLD = dot_sprite(DOT_R + 4, GOLD, glow=True)

TAG_INK = kit.text_layer(["DAY 05"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)
C_LABEL = kit.text_layer(["SAMPLES REJECTED  ·  ONE DOT = ONE SAMPLE"], kit.F_MEDIUM, 26, (120, 112, 104), tracking=4)
C_SHORT = serif_layer([f"Only {SHORTLIST} made the shortlist."], 76, INK, weight=600)
C_PCT = kit.text_layer(["That's less than 1%."], kit.F_MEDIUM, 40, GOLD)


def dot_pos(idx):
    return GX0 + (idx % COLS) * GAP, GY0 + (idx // COLS) * GAP


def paste_center(fr, spr, x, y, scale=1.0):
    if scale != 1.0:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.LANCZOS)
    fr.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))


def s_dots(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)

    # Counter (phase 1) → shortlist line (phase 2).
    if t < FADE0 + 0.2:
        n = sum(1 for idx in ORDER if APPEAR_AT[idx] <= t)
        label = f"{n}+" if n >= REJECTED else str(n)
        big = serif_layer([label], 190, INK, weight=600)
        out = 1 - appear(t, FADE0 - 0.1, 0.3)
        place(fr, big, W / 2, 430, min(appear(t, 0.1, 0.3), out), rise=0)
        place(fr, C_LABEL, W / 2, 560, min(appear(t, 0.3), out), rise=0)
    place(fr, C_SHORT, W / 2, 440, appear(t, FADE0 + 0.2, 0.5))
    place(fr, C_PCT, W / 2, 545, appear(t, FADE0 + 0.8, 0.5))

    fade = appear(t, FADE0, 0.6)
    gather = kit.ease_in_out((t - GATHER0) / (GATHER1 - GATHER0)) if t > GATHER0 else 0
    for idx in range(COLS * ROWS):
        a0 = APPEAR_AT[idx]
        if t < a0:
            continue
        pop = min(1.0, (t - a0) / 0.12)
        x, y = dot_pos(idx)
        if idx in CHOSEN:
            continue
        if fade <= 0:
            paste_center(fr, DOT, x, y, 0.4 + 0.6 * pop)
        else:
            spr = DOT_FADED if fade >= 1 else Image.blend(DOT, DOT_FADED, fade)
            if gather > 0:  # rejected dots dissolve while the shortlist gathers
                spr = spr.copy()
                spr.putalpha(spr.split()[3].point(lambda v: int(v * (1 - 0.85 * gather))))
            paste_center(fr, spr, x, y)
    # The 6 shortlisted samples: same as the rest until FADE0, then gold, then gather in a row.
    for j, idx in enumerate(sorted(CHOSEN)):
        a0 = APPEAR_AT[idx]
        if t < a0:
            continue
        x, y = dot_pos(idx)
        tx, ty = W / 2 + (j - (SHORTLIST - 1) / 2) * 110, GY0 + (ROWS * GAP) / 2
        x, y = x + (tx - x) * gather, y + (ty - y) * gather
        if fade <= 0:
            paste_center(fr, DOT, x, y, 0.4 + 0.6 * min(1.0, (t - a0) / 0.12))
        else:
            g = kit.ease_out(fade)
            paste_center(fr, DOT_GOLD, x, y, 0.6 + 0.4 * g + 0.6 * gather)
    return fr


# --------------------------------------------------------------------------- scene 3: shortlist photo

def _shortlist_still():
    img = Image.open(os.path.join(REELS, "day02", "footage", "shortlist.jpg")).convert("RGB")
    box = (306, 708, 404, 762)  # "GEL Cleanser" label stays blurred
    img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
    img = img.resize((W, H), Image.LANCZOS)
    return ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.05)).enhance(0.92)


SHORT_IMG = _shortlist_still()
H3 = title(["Those 6 are still", "being tested."], 96)
H3_K = kicker(["Not every one will make it."], 42)


def s_short(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H3, W / 2, 490, appear(t, 0.15))
    place(fr, H3_K, W / 2, 680, appear(t, 1.0))


# --------------------------------------------------------------------------- scene 4: the line

H4 = title(["Saying no is how", "we'll earn your yes."], 92)


def s_line(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H4, W / 2, 500, appear(t, 0.2, 0.6))


# --------------------------------------------------------------------------- end card

E_NEXT = serif_layer(["Day 6: a day building SPOT."], 58, INK, weight=500, italic=True)


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
    dict(shots=[("day01", "rejected_samples.mp4", 4.2, 3.0, 0.8)], overlay=s_hook, zoom=(1.0, 1.08), defocus=16),  # brand labels unreadable
    dict(card=s_dots, dur=CARD_DUR),
    dict(still=SHORT_IMG, dur=3.6, overlay=s_short, zoom=(1.0, 1.08)),
    dict(shots=[("day03", "pipette_macro.mp4", 6.0, 3.6, 0.75)], overlay=s_line, zoom=(1.0, 1.06)),
    dict(card=s_end, dur=4.2),
]

CUES = dict(
    dot_times=sorted(APPEAR_AT.values()),
    fade=FADE0,
    gather=(GATHER0, GATHER1),
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


def render_scene(sc, path, cover_path=None, cover_t=None):
    enc = kit.encoder(path)
    T = scene_dur(sc)
    n = int(round(T * FPS))
    if "card" in sc:
        src = (None for _ in range(n))
    elif "still" in sc:
        src = (sc["still"] for _ in range(n))
    else:
        src = (img for day, clip, st, d, sp in sc["shots"] for img in frames(day, clip, st, d, sp))
    for f, img in enumerate(src):
        t = f / FPS
        if "card" in sc:
            fr = sc["card"](t, T)
        else:
            fr = kit.ken_burns(img, t / T, *sc["zoom"])
            if sc.get("defocus"):
                fr = fr.filter(ImageFilter.GaussianBlur(sc["defocus"]))
            fr = fr.convert("RGBA")
            sc["overlay"](fr, t, T)
        if cover_path and abs(t - cover_t) < 0.5 / FPS:
            fr.convert("RGB").save(cover_path, quality=92)
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
