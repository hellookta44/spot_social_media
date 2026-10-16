#!/usr/bin/env python3
"""Render the SPOT "Day 7" Instagram Reel: inside Beauty Asia (expo visit).

Usage:  python3 reels/day07/render.py
Output: reels/day07/out/spot_day07_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

Founder footage + photos from the expo, in the series look (Cormorant headlines,
gold numerals, cream lesson card, DAY tag, end card).
"""
import importlib.util
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageEnhance

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
place, appear = kit.place, kit.appear
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer

TAG = kit.make_tag("07")
TAG_INK = kit.text_layer(["DAY 07"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)


def frames(name, start, dur, speed=1.0):
    return d3.footage_frames(name, start, dur, speed, None, footage_dir=FOOTAGE)


def still(name):
    img = Image.open(os.path.join(FOOTAGE, name)).convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((x0, y0, x0 + W, y0 + H))
    return ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.06)).enhance(0.95)


def headline_scene(lines, size=96, k_lines=None, y=500, double_grad=True):
    h = title(lines, size)
    k = kicker(k_lines, 42) if k_lines else None

    def overlay(fr, t, T):
        fr.alpha_composite(kit.TOP_GRAD)
        if double_grad:
            fr.alpha_composite(kit.TOP_GRAD)
        place(fr, TAG, W / 2, 215, 1, rise=0)
        place(fr, h, W / 2, y, appear(t, 0.15))
        if k:
            place(fr, k, W / 2, y + h.height / 2 + 60, appear(t, 0.9))
    return overlay


# --------------------------------------------------------------------------- 1. hook: arrival

H1 = title(["We went to", "Beauty Asia."], 112)
H1_K = kicker(["To learn from the whole industry."], 42)


def s_arrive(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1, W / 2, 500, appear(t, 0.2, 0.6), rise=30)
    place(fr, d3.RULE, W / 2, 640, appear(t, 0.8), rise=0)
    place(fr, H1_K, W / 2, 710, appear(t, 1.0))


# --------------------------------------------------------------------------- lessons card

LESSONS = [
    ("01", ["Everyone sells.", "Few explain."]),
    ("02", ["People ask what's", "inside, not just the price."]),
    ("03", ["Simple, honest", "formulas stand out."]),
]
L_TITLE = serif_layer(["What Beauty Asia", "taught us"], 84, INK, weight=600)
L_NUMS = [serif_layer([n], 100, GOLD, weight=500, italic=True) for n, _ in LESSONS]
L_TEXT = [serif_layer(lines, 60, INK, weight=500, line_gap=1.12, align="left") for _, lines in LESSONS]
L_T0, L_STEP = 0.7, 0.85
L_RULE = Image.new("RGBA", (120, 2), GOLD + (255,))


def s_lessons(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, L_TITLE, W / 2, 470, appear(t, 0.05))
    place(fr, L_RULE, W / 2, 590, appear(t, 0.4), rise=0)
    for i, (num, txt) in enumerate(zip(L_NUMS, L_TEXT)):
        p = appear(t, L_T0 + i * L_STEP, 0.5)
        y = 760 + i * 240
        place(fr, num, 200, y, p, rise=24)
        place(fr, txt, 300 + txt.width / 2, y + 8, p, rise=24)
    return fr


# --------------------------------------------------------------------------- end card

E_NEXT = serif_layer(["Day 8: why I started SPOT."], 58, INK, weight=500, italic=True)


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

WALK = still("walking_hall.jpg")
BOOTH = still("ingredient_booth.jpg")
NOTES = still("taking_notes.jpg")
WALK2 = still("walking_hall_2.jpg")

SCENES = [
    dict(clip=("expo_arrival.mp4", 0.3, 3.2, 0.85), overlay=s_arrive, zoom=(1.0, 1.06)),
    dict(still=WALK, dur=3.0, overlay=headline_scene(["Hall after hall.", "Brand after brand."], 92),
         zoom=(1.0, 1.08), focus=(0.5, 0.6)),
    dict(still=BOOTH, dur=3.2, overlay=headline_scene(["We met ingredient", "suppliers."], 92,
                                                      ["Where does every raw material come from?"]),
         zoom=(1.0, 1.07), focus=(0.4, 0.5)),
    dict(clip=("skin_analyzer.mp4", 0.0, 2.4, 0.5), overlay=headline_scene(["Saw the newest", "skin tech."], 96),
         zoom=(1.0, 1.05)),
    dict(still=NOTES, dur=3.2, overlay=headline_scene(["Asked questions.", "Took notes."], 96,
                                                      ["Lots of notes."]),
         zoom=(1.0, 1.07), focus=(0.6, 0.45)),
    dict(card=s_lessons, dur=4.4),
    dict(still=WALK2, dur=3.0, overlay=headline_scene(["Came home with ideas."], 92,
                                                      ["(and a few bags)"]),
         zoom=(1.06, 1.0), focus=(0.5, 0.6)),
    dict(card=s_end, dur=4.2),
]

CUES = dict(lessons=[L_T0 + i * L_STEP for i in range(len(LESSONS))])


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


def render_scene(sc, path):
    enc = kit.encoder(path)
    T = scene_dur(sc)
    n = int(round(T * FPS))
    if "card" in sc:
        src = (None for _ in range(n))
    elif "still" in sc:
        src = (sc["still"] for _ in range(n))
    else:
        src = frames(*sc["clip"])
    for f, img in enumerate(src):
        t = f / FPS
        if "card" in sc:
            fr = sc["card"](t, T)
        else:
            fx, fy = sc.get("focus", (0.5, 0.5))
            fr = kit.ken_burns(img, t / T, *sc["zoom"], fx=fx, fy=fy).convert("RGBA")
            sc["overlay"](fr, t, T)
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()


def main():
    _sspec = importlib.util.spec_from_file_location("day07_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day07_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        render_scene(sc, p)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_day07_music.wav"))
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
    for name, audio in [("spot_day07_reel.mp4", ["-i", score_path]),
                        ("spot_day07_reel_no_music.mp4",
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
