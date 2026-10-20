#!/usr/bin/env python3
"""Render the SPOT "Day 8" Instagram Reel: why I started SPOT (founder letter).

Usage:  python3 reels/day08/render.py
Output: reels/day08/out/spot_day08_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

The founder's story in first person: real founder footage no earlier reel used,
street + factory road clips, and cream "letter" cards in the series look.
"""
import importlib.util
import os
import shutil
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.join(HERE, "..")
_spec = importlib.util.spec_from_file_location("day03_render", os.path.join(REELS, "day03", "render.py"))
d3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d3)
kit = d3.kit

OUT = os.path.join(HERE, "out")
FOOTAGE = {n: os.path.join(REELS, d, "footage") for n, d in [
    ("founder_skin_test.mp4", "day03"), ("road_trip.mp4", "day04"), ("factory_arrival.mp4", "day05")]}
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = d3.XFADE, d3.LAST_XFADE
INK, CREAM, WHITE = kit.INK, kit.CREAM, kit.WHITE
GOLD = (176, 141, 87)
MUTED = (120, 112, 104)
place, appear = kit.place, kit.appear
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer

TAG = kit.make_tag("08")
TAG_INK = kit.text_layer(["DAY 08"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)
BOT_GRAD = kit.gradient(0.75, 1000, bottom=True)
RULE_GOLD = Image.new("RGBA", (120, 2), GOLD + (255,))


def frames(name, start, dur, speed=1.0):
    return d3.footage_frames(name, start, dur, speed, None, footage_dir=FOOTAGE[name])


def tag_only(fr):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)


def lower_scene(lines, size=96, k_lines=None, y=1420):
    """Founder shots: face stays clear, words sit in the lower third."""
    h = title(lines, size)
    k = kicker(k_lines, 42) if k_lines else None

    def overlay(fr, t, T):
        fr.alpha_composite(BOT_GRAD)
        tag_only(fr)
        place(fr, h, W / 2, y, appear(t, 0.2, 0.55), rise=30)
        if k:
            place(fr, k, W / 2, y + h.height / 2 + 60, appear(t, 1.0))
    return overlay


def top_scene(lines, size=96, k_lines=None, y=520):
    h = title(lines, size)
    k = kicker(k_lines, 42) if k_lines else None

    def overlay(fr, t, T):
        fr.alpha_composite(kit.TOP_GRAD)
        fr.alpha_composite(kit.TOP_GRAD)
        place(fr, TAG, W / 2, 215, 1, rise=0)
        place(fr, h, W / 2, y, appear(t, 0.2))
        if k:
            place(fr, k, W / 2, y + h.height / 2 + 60, appear(t, 0.9))
    return overlay


# --------------------------------------------------------------------------- 1. hook

H1 = title(["Why I started", "SPOT."], 124)
H1_K = kicker(["A note from the founder."], 42)


def s_hook(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1, W / 2, 475, appear(t, 0.25, 0.6), rise=30)
    place(fr, d3.RULE, W / 2, 630, appear(t, 0.9), rise=0)
    place(fr, H1_K, W / 2, 685, appear(t, 1.1))


# --------------------------------------------------------------------------- 2. the problem (letter card)

P_KICK = kit.text_layer(["THE PROBLEM"], kit.F_SEMIBOLD, 30, GOLD, tracking=8)
P_TITLE = serif_layer(["I couldn't find", "skincare I", "actually trusted."], 92, INK, weight=600)
P_LINES = [serif_layer([s], 60, INK, weight=500, italic=True) for s in
           ["Long labels.", "Big promises.", "Nobody explaining what's inside."]]
P_T0, P_STEP = 1.5, 0.9


def s_problem(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, P_KICK, W / 2, 520, appear(t, 0.05))
    place(fr, RULE_GOLD, W / 2, 575, appear(t, 0.2), rise=0)
    place(fr, P_TITLE, W / 2, 770, appear(t, 0.3, 0.6))
    for i, ln in enumerate(P_LINES):
        place(fr, ln, W / 2, 1080 + i * 100, appear(t, P_T0 + i * P_STEP, 0.45), rise=20)
    return fr


# --------------------------------------------------------------------------- 5. the numbers

N_35 = serif_layer(["35"], 210, GOLD, weight=500)
N_15 = serif_layer(["15"], 210, GOLD, weight=500)
N_L1 = kit.with_shadow(kit.text_layer(["SAMPLES"], kit.F_SEMIBOLD, 32, WHITE, tracking=8), 10, 0.6)
N_L2 = kit.with_shadow(kit.text_layer(["FACTORIES"], kit.F_SEMIBOLD, 32, WHITE, tracking=8), 10, 0.6)
N_HEAD = title(["So I went looking", "myself."], 96)


def s_numbers(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(BOT_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, N_HEAD, W / 2, 500, appear(t, 0.15))
    for i, (num, lab) in enumerate([(N_35, N_L1), (N_15, N_L2)]):
        x = W / 2 + (-230 if i == 0 else 230)
        p = appear(t, 0.9 + i * 0.6, 0.5)
        place(fr, kit.with_shadow(num, 14, 0.5), x, 1360, p, rise=30)
        place(fr, lab, x, 1510, p, rise=20)


# --------------------------------------------------------------------------- 6. the promise (letter card)

S_KICK = kit.text_layer(["SO I'M BUILDING IT"], kit.F_SEMIBOLD, 30, GOLD, tracking=8)
S_TITLE = serif_layer(["SPOT is the", "skincare I wanted", "to find."], 96, INK, weight=600)
S_WORDS = [serif_layer([w], 84, GOLD, weight=500, italic=True) for w in ["Simple.", "Honest.", "Explained."]]
S_T0, S_STEP = 1.4, 0.55


def s_promise(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, S_KICK, W / 2, 520, appear(t, 0.05))
    place(fr, RULE_GOLD, W / 2, 575, appear(t, 0.2), rise=0)
    place(fr, S_TITLE, W / 2, 780, appear(t, 0.3, 0.6))
    for i, wd in enumerate(S_WORDS):
        place(fr, wd, W / 2, 1110 + i * 115, appear(t, S_T0 + i * S_STEP, 0.4), rise=18)
    return fr


# --------------------------------------------------------------------------- 8. signature card

G_LINE = serif_layer(["If I wouldn't put it", "on my own skin,", "it doesn't go into SPOT."], 70, INK,
                     weight=500, italic=True, line_gap=1.15)
G_SIGN = kit.text_layer(["— FOUNDER, SPOT"], kit.F_SEMIBOLD, 30, GOLD, tracking=8)


def s_sign(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, G_LINE, W / 2, 860, appear(t, 0.2, 0.7))
    place(fr, RULE_GOLD, W / 2, 1075, appear(t, 1.1), rise=0)
    place(fr, G_SIGN, W / 2, 1140, appear(t, 1.3))
    return fr


# --------------------------------------------------------------------------- end card

E_NEXT = serif_layer(["Day 9: my skin story."], 58, INK, weight=500, italic=True)


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
    dict(clip=("founder_skin_test.mp4", 0.2, 3.6, 1.0), overlay=s_hook, zoom=(1.0, 1.06), focus=(0.5, 0.3)),
    dict(card=s_problem, dur=5.2),
    dict(clip=("founder_skin_test.mp4", 12.3, 3.8, 1.0),
         overlay=top_scene(["So I started asking", "questions."], 92, ["What's in it? Why? For whom?"], y=475),
         zoom=(1.04, 1.0), focus=(0.5, 0.3)),
    dict(clip=("road_trip.mp4", 19.4, 3.2, 1.0),
         overlay=top_scene(["Every answer led", "somewhere new."], 96), zoom=(1.0, 1.06)),
    dict(clip=("factory_arrival.mp4", 6.0, 3.9, 1.0), overlay=s_numbers, zoom=(1.0, 1.05)),
    dict(card=s_promise, dur=4.6),
    dict(clip=("founder_skin_test.mp4", 24.1, 3.9, 1.0),
         overlay=lower_scene(["Every ingredient.", "Every reason."], 96, ["Explained, not hidden."]),
         zoom=(1.0, 1.05), focus=(0.5, 0.3)),
    dict(card=s_sign, dur=3.8),
    dict(card=s_end, dur=4.5),
]

CUES = dict(problem=[P_T0 + i * P_STEP for i in range(len(P_LINES))],
            words=[S_T0 + i * S_STEP for i in range(len(S_WORDS))],
            numbers=[0.9, 1.5])


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
    src = (None for _ in range(n)) if "card" in sc else frames(*sc["clip"])
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
    _sspec = importlib.util.spec_from_file_location("day08_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day08_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        render_scene(sc, p)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_day08_music.wav"))
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
    for name, audio in [("spot_day08_reel.mp4", ["-i", score_path]),
                        ("spot_day08_reel_no_music.mp4",
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
