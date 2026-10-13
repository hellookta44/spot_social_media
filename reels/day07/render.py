#!/usr/bin/env python3
"""Render the SPOT "Day 7" Instagram Reel: a day building SPOT, 6am to midnight.

Usage:  python3 reels/day07/fetch_pexels.py   # once: downloads the stock clips
        python3 reels/day07/render.py
Output: reels/day07/out/spot_day07_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

All footage is new Pexels stock (free licence; credits in footage/credits.json).
A gold analog clock + serif time stamp ticks forward at every cut.
"""
import importlib.util
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw

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
GOLD = (196, 160, 104)
place, appear = kit.place, kit.appear
serif_layer = d3.serif_layer

TAG = kit.make_tag("07")

# (slot file, clock minutes since midnight, time label, line, clip start, duration)
HOURS = [
    ("0600_sunrise", 6 * 60, ("6:00", "AM"), "The day starts before the city does.", 0.5, 3.0),
    ("0730_coffee", 7 * 60 + 30, ("7:30", "AM"), "Coffee first. Then the list.", 0.5, 2.4),
    ("0900_laptop", 9 * 60, ("9:00", "AM"), "Emails to manufacturers.", 0.5, 2.4),
    ("1100_call", 11 * 60, ("11:00", "AM"), "A call with our chemist.", 0.5, 2.4),
    ("1300_lab", 13 * 60, ("1:00", "PM"), "Back to the formulas.", 0.5, 2.6),
    ("1600_notes", 16 * 60, ("4:00", "PM"), "Notes. Decisions. More notes.", 0.5, 2.4),
    ("1900_drive", 19 * 60, ("7:00", "PM"), "On the road again.", 0.5, 2.4),
    ("2300_night", 23 * 60, ("11:00", "PM"), "Still at it.", 0.5, 2.6),
    ("0000_city", 24 * 60, ("12:00", "AM"), "Tomorrow, we go again.", 0.5, 2.8),
]
HAND_SWEEP = 0.55  # seconds for the clock hands to sweep to the new time at each cut


def frames(name, start, dur):
    return d3.footage_frames(f"{name}.mp4", start, dur, 1.0, None, footage_dir=FOOTAGE)


# --------------------------------------------------------------------------- clock + time stamp

def clock(minutes, size=150):
    """Gold analog clock face (supersampled); hour and minute hands at `minutes`."""
    s = 4
    S = size * s
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    d.ellipse([3 * s, 3 * s, S - 3 * s, S - 3 * s], outline=GOLD + (255,), width=4 * s)
    for k in range(12):  # hour ticks
        a = math.radians(k * 30)
        r0, r1 = c * (0.80 if k % 3 else 0.70), c * 0.88
        d.line([(c + r0 * math.sin(a), c - r0 * math.cos(a)), (c + r1 * math.sin(a), c - r1 * math.cos(a))],
               fill=GOLD + (255,), width=(3 if k % 3 else 5) * s)
    ha = math.radians((minutes / 60.0) % 12 * 30)
    ma = math.radians((minutes % 60) * 6)
    d.line([(c, c), (c + c * 0.45 * math.sin(ha), c - c * 0.45 * math.cos(ha))], fill=WHITE + (255,), width=7 * s)
    d.line([(c, c), (c + c * 0.68 * math.sin(ma), c - c * 0.68 * math.cos(ma))], fill=WHITE + (255,), width=4 * s)
    d.ellipse([c - 7 * s, c - 7 * s, c + 7 * s, c + 7 * s], fill=GOLD + (255,))
    return kit.with_shadow(img.resize((size, size), Image.LANCZOS), 12, 0.6)


def stamp(label):
    """'6:00' in big serif + 'AM' in spaced caps, side by side."""
    t = serif_layer([label[0]], 150, WHITE, weight=600)
    ap = kit.text_layer([label[1]], kit.F_SEMIBOLD, 40, GOLD, tracking=6)
    img = Image.new("RGBA", (t.width + 18 + ap.width, t.height), (0, 0, 0, 0))
    img.alpha_composite(t, (0, 0))
    img.alpha_composite(ap, (t.width + 18, int(t.height * 0.42)))
    return kit.with_shadow(img, 16, 0.6)


STAMPS = [stamp(h[2]) for h in HOURS]
LINES = [kit.with_shadow(serif_layer([h[3]], 66, WHITE, weight=500, italic=True), 14, 0.6) for h in HOURS]


def make_overlay(i):
    prev_min = HOURS[i - 1][1] if i else HOURS[0][1] - 60

    def overlay(fr, t, T):
        fr.alpha_composite(kit.TOP_GRAD)
        fr.alpha_composite(kit.TOP_GRAD)
        place(fr, TAG, W / 2, 215, 1 if i else appear(t, 0.0, 0.35), rise=0)
        k = kit.ease_in_out(t / HAND_SWEEP)
        minutes = prev_min + (HOURS[i][1] - prev_min) * k
        cl = clock(minutes)
        st = STAMPS[i]
        row_w = cl.width + 10 + st.width
        x0 = (W - row_w) / 2
        p = 1 if i else appear(t, 0.2, 0.4)
        place(fr, cl, x0 + cl.width / 2, 470, p, rise=0)
        place(fr, st, x0 + cl.width + 10 + st.width / 2, 470, appear(t, 0.05, 0.3), rise=14)
        place(fr, LINES[i], W / 2, 640, appear(t, 0.35, 0.4), rise=18)
    return overlay


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

SCENES = [dict(slot=h[0], start=h[4], dur=h[5], overlay=make_overlay(i), zoom=(1.0, 1.06))
          for i, h in enumerate(HOURS)] + [dict(card=s_end, dur=4.2)]
CUES = dict(hand_sweep=HAND_SWEEP)


def scene_dur(sc):
    return sc["dur"]


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
    src = (None for _ in range(n)) if "card" in sc else frames(sc["slot"], sc["start"], T)
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
    missing = [h[0] for h in HOURS if not os.path.exists(os.path.join(FOOTAGE, f"{h[0]}.mp4"))]
    if missing:
        raise SystemExit(f"Missing footage {missing} — run reels/day07/fetch_pexels.py first.")
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
