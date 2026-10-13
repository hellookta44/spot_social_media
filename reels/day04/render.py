#!/usr/bin/env python3
"""Render the SPOT "Day 4" Instagram Reel: on the road — 15 factories.

Usage:  python3 reels/day04/render.py
Output: reels/day04/out/spot_day04_reel.mp4 (+ _no_music, music .wav, cover .jpg)

Same look as Day 3 (Cormorant Garamond headlines, Inter labels, DAY tag, end card);
helpers come from reels/day03/render.py and reels/day01/render.py.
"""
import importlib.util
import os
import shutil
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("day03_render", os.path.join(HERE, "..", "day03", "render.py"))
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

TAG = kit.make_tag("04")
FACTORIES = 15


def frames(name, start, dur, speed=1.0):
    return d3.footage_frames(name, start, dur, speed, None, footage_dir=FOOTAGE)


# --------------------------------------------------------------------------- scenes

H1_PRE = title(["We visited"], 76)
H1_POST = title(["factories."], 96)
H1_K = kicker(["Before choosing one."], 44)


def s_hook(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1_PRE, W / 2, 420, appear(t, 0.1))
    k = kit.ease_out((t - 0.3) / 1.4)
    n = round(FACTORIES * k)
    big = kit.with_shadow(serif_layer([str(n)], 340), 20, 0.55)
    pop = 1.0 + 0.07 * max(0.0, 1 - (t - 1.7) / 0.25) if t > 1.7 else 1.0
    place(fr, big, W / 2, 640, appear(t, 0.25, 0.3), rise=20, scale=pop)
    place(fr, H1_POST, W / 2, 860, appear(t, 0.5))
    place(fr, H1_K, W / 2, 980, appear(t, 1.8))


H2 = title(["Day 4 happened", "on the road."], 100)
H2_K = kicker(["City to city. Factory to factory."], 42)


def s_road(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H2, W / 2, 500, appear(t, 0.15))
    place(fr, H2_K, W / 2, 690, appear(t, 1.0))


H3 = title(["We don't pick a partner", "from a screen."], 86)
H3_K = kicker(["We go and see for ourselves."], 42)


def s_city(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H3, W / 2, 490, appear(t, 0.15))
    place(fr, H3_K, W / 2, 670, appear(t, 1.0))


H4 = title(["The samples", "ride along."], 104)
H4_K = kicker(["Tested in real life, not just the lab."], 42)


def s_samples(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H4, W / 2, 500, appear(t, 0.15))
    place(fr, H4_K, W / 2, 690, appear(t, 1.0))


# Lessons card (cream, motion graphic)
TAG_INK = d3.kit.text_layer(["DAY 04"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = d3.kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)
L_TITLE = serif_layer([f"What {FACTORIES} factories", "taught us"], 84, INK, weight=600)
LESSONS = [
    ("01", ["A great sample isn't", "a great batch."]),
    ("02", ["Clean floors tell you", "more than brochures."]),
    ("03", ["Good formulas", "can't be rushed."]),
]
L_NUMS = [serif_layer([n], 100, GOLD, weight=500, italic=True) for n, _ in LESSONS]
L_TEXT = [serif_layer(lines, 62, INK, weight=500, line_gap=1.12, align="left") for _, lines in LESSONS]
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


H6 = title(["Only the best", "get to make SPOT."], 96)


def s_dropper(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H6, W / 2, 500, appear(t, 0.15))


H7 = title(["The journey", "continues."], 100)


def s_dash(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H7, W / 2, 500, appear(t, 0.15))


E_NEXT = serif_layer(["Day 5: what 700 no's look like."], 58, INK, weight=500, italic=True)


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


# (clip, start, dur, speed) per shot
SCENES = [
    dict(shots=[("road_trip.mp4", 4.6, 3.0, 0.85)], overlay=s_hook, zoom=(1.0, 1.06)),
    dict(shots=[("road_trip.mp4", 0.2, 3.4, 0.9)], overlay=s_road, zoom=(1.02, 1.08)),
    dict(shots=[("road_trip.mp4", 9.4, 1.9, 1.0), ("road_trip.mp4", 16.0, 1.8, 1.0)], overlay=s_city, zoom=(1.0, 1.06)),
    dict(shots=[("rural_road.mp4", 0.0, 1.4, 1.0), ("dashboard_two_bottles.mp4", 0.2, 2.4, 1.0)],
         overlay=s_samples, zoom=(1.0, 1.05)),
    dict(card=s_lessons, dur=4.4),
    dict(shots=[("dropper_sunlight.mp4", 0.0, 3.2, 0.85)], overlay=s_dropper, zoom=(1.0, 1.06)),
    dict(shots=[("dashboard_bottle.mp4", 0.2, 2.8, 0.9)], overlay=s_dash, zoom=(1.0, 1.05)),
    dict(card=s_end, dur=4.2),
]

CUES = dict(count=(0.3, 1.7), lessons=[L_T0 + i * L_STEP for i in range(len(LESSONS))])


def scene_dur(sc):
    return sc.get("dur") or sum(s[2] for s in sc["shots"])


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
    if "card" in sc:
        src = (None for _ in range(int(round(T * FPS))))
    else:
        src = (img for clip, st, d, sp in sc["shots"] for img in frames(clip, st, d, sp))
    for f, img in enumerate(src):
        t = f / FPS
        if "card" in sc:
            fr = sc["card"](t, T)
        else:
            fr = kit.ken_burns(img, t / T, *sc["zoom"]).convert("RGBA")
            sc["overlay"](fr, t, T)
        if cover_path and abs(t - cover_t) < 0.5 / FPS:
            fr.convert("RGB").save(cover_path, quality=92)
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()


def main():
    _sspec = importlib.util.spec_from_file_location("day04_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day04_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        render_scene(sc, p)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_day04_music.wav"))
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
    for name, audio in [("spot_day04_reel.mp4", ["-i", score_path]),
                        ("spot_day04_reel_no_music.mp4",
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
