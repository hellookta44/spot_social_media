#!/usr/bin/env python3
"""Render the SPOT "Day 8" Instagram Reel: the journey of one bottle (process film).

Usage:  python3 reels/day08/render.py
Output: reels/day08/out/spot_day08_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

Source: footage/process.mov, a 16s vertical slideshow of 8 process stills with text
printed on them. Each still is cropped to full-bleed 9:16, its printed text is
painted out, and it is given a cinematic treatment: graded, upscaled, a slow
dolly + handheld drift, rack focus on some cuts, live liquid motion (pour stream,
mixing vortex), film grain, vignette and a soft bloom. Series titles on top.
"""
import importlib.util
import math
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.join(HERE, "..")
_spec = importlib.util.spec_from_file_location("day03_render", os.path.join(REELS, "day03", "render.py"))
d3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d3)
kit = d3.kit

SRC = os.path.join(HERE, "footage", "process.mov")
OUT = os.path.join(HERE, "out")
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = d3.XFADE, d3.LAST_XFADE
INK, CREAM = kit.INK, kit.CREAM
GOLD = (176, 141, 87)
place, appear = kit.place, kit.appear
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer
TAG = kit.make_tag("08")
rng = np.random.default_rng(808)

# --------------------------------------------------------------------------- source stills
# frame index in process.mov, image box inside the frame, printed-text boxes to paint out,
# and the 9:16 crop centre (0..1 across the image). All boxes are source pixels.
STILLS = {
    "pour":   dict(frame=8, box=(16, 214, 522, 745), text=[(36, 226, 336, 292), (36, 668, 256, 736)], fx=0.52),
    "mix":    dict(frame=24, box=(28, 236, 524, 721), text=[(40, 244, 186, 306), (40, 652, 232, 714)], fx=0.52),
    "test":   dict(frame=40, box=(42, 236, 522, 721), text=[(56, 244, 252, 306), (56, 652, 258, 714)], fx=0.60),
    "fill":   dict(frame=56, box=(16, 222, 522, 742), text=[(34, 242, 232, 306), (34, 680, 208, 746)], fx=0.50),
    "cap":    dict(frame=72, box=(20, 246, 522, 720), text=[(40, 260, 268, 324), (40, 660, 212, 724)], fx=0.42),
    "label":  dict(frame=88, box=(44, 246, 524, 720), text=[(56, 260, 188, 324), (56, 660, 212, 724)], fx=0.30),
    "row":    dict(frame=104, box=(18, 292, 522, 668), text=[(24, 288, 160, 336)], fx=0.70),
    "hero":   dict(frame=120, box=(24, 284, 524, 680), text=[], fx=0.10),
}


def read_frame(i):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"select=eq(n\\,{i})", "-vsync", "0",
                          "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return Image.frombuffer("RGB", (540, 960), raw, "raw", "RGB", 0, 1).copy()


def paint_out(img, boxes):
    """Remove printed captions: find the light, high-contrast glyph pixels inside each box and
    fill them from the surrounding picture (iterative blur fill, coarse to fine)."""
    a = np.asarray(img, np.float32).copy()
    lum = a.mean(axis=2)
    local = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.MedianFilter(13)), np.float32)
    mask = np.zeros(lum.shape, bool)
    for x0, y0, x1, y1 in boxes:
        sub = (lum[y0:y1, x0:x1] - local[y0:y1, x0:x1] > 22) & (lum[y0:y1, x0:x1] > 120)
        mask[y0:y1, x0:x1] |= sub
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
    mask = np.asarray(m) > 0
    for r in (8, 6, 4, 3, 2, 2, 1, 1, 1):
        for _ in range(6):
            blur = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32)
            a[mask] = blur[mask]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # a touch of matching noise so the filled patches don't look smoother than the photo
    n = rng.normal(0, 3.0, a.shape).astype(np.float32) * mask[..., None]
    return Image.fromarray(np.clip(np.asarray(out, np.float32) + n, 0, 255).astype(np.uint8))


def grade(img):
    """Shared film look: lifted blacks, warm highlights, cooler shadows, gentle contrast."""
    a = np.asarray(img, np.float32) / 255
    lum = a.mean(axis=2, keepdims=True)
    a = 0.03 + 0.95 * a                                     # lift + soft roll-off
    a = a + (a - lum) * -0.08                               # slightly calmer saturation
    shadow, high = np.clip(1 - lum * 2, 0, 1), np.clip(lum * 2 - 1, 0, 1)
    a += shadow * np.array([-0.012, 0.004, 0.018]) + high * np.array([0.022, 0.008, -0.02])
    a = a + 0.08 * (a - 0.5) * (1 - np.abs(a - 0.5) * 2)    # s-curve
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def portrait(name):
    st = STILLS[name]
    fr = paint_out(read_frame(st["frame"]), st["text"])
    img = fr.crop(st["box"])
    cw = round(img.height * W / H)
    x0 = int(np.clip(st["fx"] * img.width - cw / 2, 0, img.width - cw))
    return grade(img.crop((x0, 0, x0 + cw, img.height))), (st["box"][0] + x0, st["box"][1])


# --------------------------------------------------------------------------- live motion

def remap(img, sx, sy):
    """Bilinear sample img at float coords (sx, sy) — numpy, no scipy."""
    a = np.asarray(img, np.float32)
    h, w = a.shape[:2]
    sx, sy = np.clip(sx, 0, w - 1.001), np.clip(sy, 0, h - 1.001)
    x0, y0 = sx.astype(int), sy.astype(int)
    fx, fy = (sx - x0)[..., None], (sy - y0)[..., None]
    out = (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy)
           + a[y0 + 1, x0] * (1 - fx) * fy + a[y0 + 1, x0 + 1] * fx * fy)
    return Image.fromarray(out.astype(np.uint8))


def vortex(img, origin, centre, radius, shaft_halfw):
    """Mixing vat: liquid turns around the shaft, fastest at the centre, still at the rim."""
    cx, cy = centre[0] - origin[0], centre[1] - origin[1]
    h, w = img.height, img.width
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx, (yy - cy) * 1.9                       # vat seen at an angle: flatten the circle
    r = np.sqrt(dx ** 2 + dy ** 2)
    q = np.clip(r / radius, 0, 1)
    fall = np.clip(4 * q * (1 - q), 0, 1) ** 1.2           # still at the shaft and the rim, fastest between
    near = np.clip((np.abs(xx - cx) - shaft_halfw) / 40, 0, 1)
    below = np.clip((yy - (cy + 50)) / 70, 0, 1)
    fall *= np.maximum(near, below)                         # shaft and agitator stay rigid

    def at(t):
        ang = -0.09 * t * fall
        c, s = np.cos(ang), np.sin(ang)
        return remap(img, cx + c * dx - s * dy, cy + (s * dx + c * dy) / 1.9)
    return at


def flow(img, origin, poly_x, y_range, width):
    """Pour: the stream ripples and runs downward; the beaker surface shivers."""
    h, w = img.height, img.width
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ys = yy + origin[1]
    xc = np.interp(ys, *poly_x) - origin[0]
    inside = np.clip(1 - np.abs(xx - xc) / width, 0, 1) * ((ys > y_range[0]) & (ys < y_range[1]))

    def at(t):
        ph = (ys - 140 * t) / 9.0
        wob = (np.sin(ph) + 0.5 * np.sin(ph * 2.3 + 1.7)) * 1.2 * inside
        return remap(img, xx + wob, yy - 0.8 * inside * np.sin(ph * 1.7))
    return at


# --------------------------------------------------------------------------- camera + film

BIG = 1.14  # working plate size relative to the frame, room for moves


def plate(small):
    big = small.resize((int(W * BIG), int(H * BIG)), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    bloom = big.filter(ImageFilter.GaussianBlur(28)).point(lambda v: max(0, v - 150) * 2)
    return Image.fromarray(np.clip(np.asarray(big, np.int16) + np.asarray(bloom, np.int16) // 5, 0, 255)
                           .astype(np.uint8))


def handheld(t, seed):
    r = np.random.default_rng(seed)
    ph = r.uniform(0, 6.3, 6)
    dx = 5.0 * math.sin(2 * math.pi * 0.37 * t + ph[0]) + 2.4 * math.sin(2 * math.pi * 0.91 * t + ph[1])
    dy = 4.2 * math.sin(2 * math.pi * 0.29 * t + ph[2]) + 2.0 * math.sin(2 * math.pi * 1.13 * t + ph[3])
    rot = 0.22 * math.sin(2 * math.pi * 0.23 * t + ph[4]) + 0.08 * math.sin(2 * math.pi * 0.71 * t + ph[5])
    return dx, dy, rot


def camera(big, t, T, z0, z1, pan, seed):
    """Dolly (z0 -> z1), slow pan (dx, dy in output px over the shot) and handheld drift."""
    k = kit.ease_in_out(t / T)
    z = z0 + (z1 - z0) * k
    hx, hy, rot = handheld(t, seed)
    cx = big.width / 2 + (pan[0] * (k - 0.5) + hx) * BIG
    cy = big.height / 2 + (pan[1] * (k - 0.5) + hy) * BIG
    s = BIG / z                                       # source px per output px
    a, b = s * math.cos(math.radians(rot)), s * math.sin(math.radians(rot))
    c0 = cx - a * W / 2 - b * H / 2
    f0 = cy + b * W / 2 - a * H / 2
    return big.transform((W, H), Image.AFFINE, (a, b, c0, -b, a, f0), resample=Image.BICUBIC)


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = (1 - 0.32 * (((xx / W - 0.5) ** 2) * 1.4 + ((yy / H - 0.5) ** 2)) ** 1.1)[..., None]
GRAINS = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
del yy, xx


def film(fr, f):
    a = np.asarray(fr, np.float32) * VIGNETTE
    g = GRAINS[f % len(GRAINS)]
    g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)[..., None]
    lum = a.mean(axis=2, keepdims=True) / 255
    a += g * (5.5 + 5 * (1 - np.abs(lum - 0.45) * 2))   # grain strongest in the mid-tones
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


# --------------------------------------------------------------------------- overlays

BOT_GRAD = kit.gradient(0.72, 900, bottom=True)


def lower(lines, size=100, k_lines=None, y=1400, hook=False):
    h = title(lines, size)
    k = kicker(k_lines, 42) if k_lines else None

    def overlay(fr, t, T):
        fr.alpha_composite(kit.TOP_GRAD)
        fr.alpha_composite(BOT_GRAD)
        place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35) if hook else 1, rise=0)
        place(fr, h, W / 2, y, appear(t, 0.25, 0.55), rise=26)
        if k:
            place(fr, k, W / 2, y + h.height / 2 + 56, appear(t, 0.8))
    return overlay


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
    dict(still="pour", dur=3.2, z=(1.00, 1.10), pan=(0, 30), focus=0.5,
         live=lambda img, o: flow(img, o, ([212, 300, 470], [345, 322, 296]), (212, 470), 26),
         overlay=lower(["What goes into", "one bottle?"], 108, ["The journey of a formula."], hook=True)),
    dict(still="mix", dur=3.0, z=(1.08, 1.0), pan=(0, -20),
         live=lambda img, o: vortex(img, o, (281, 568), 250, 95),
         overlay=lower(["Mixed slowly.", "Never rushed."])),
    dict(still="test", dur=3.0, z=(1.0, 1.09), pan=(-24, 0), focus=0.45,
         overlay=lower(["Tested before", "it's trusted."])),
    dict(still="fill", dur=2.6, z=(1.02, 1.08), pan=(70, 0),
         overlay=lower(["Filled with care."])),
    dict(still="cap", dur=2.6, z=(1.08, 1.02), pan=(-60, 0),
         overlay=lower(["Sealed to stay fresh."], 96)),
    dict(still="label", dur=2.6, z=(1.0, 1.07), pan=(40, 10),
         overlay=lower(["Packaging", "comes last."], 100, ["The formula always comes first."])),
    dict(still="row", dur=2.8, z=(1.06, 1.0), pan=(-30, 0), focus=0.5,
         overlay=lower(["Simple. Honest.", "Explained."], 104, y=1500)),
    dict(still="hero", dur=3.4, z=(1.0, 1.08), pan=(0, -20),
         overlay=lower(["Skincare products,", "coming soon."], 96, ["Follow the journey."], y=1480)),
    dict(card=s_end, dur=4.5),
]


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


def scene_frames(i, sc):
    T = sc["dur"]
    n = int(round(T * FPS))
    if "card" in sc:
        for f in range(n):
            yield sc["card"](f / FPS, T)
        return
    small, origin = portrait(sc["still"])
    live = sc["live"](small, origin) if "live" in sc else None
    big = plate(small) if live is None else None
    for f in range(n):
        t = f / FPS
        pl = big if live is None else plate(live(t))
        fr = camera(pl, t, T, *sc["z"], sc["pan"], seed=i)
        if "focus" in sc and t < sc["focus"]:          # rack focus in
            k = 1 - kit.ease_out(t / sc["focus"])
            if k > 0.02:
                fr = fr.filter(ImageFilter.GaussianBlur(9 * k))
        fr = film(fr, f + 7 * i)
        sc["overlay"](fr, t, T)
        yield fr


CUES = {}


def main():
    _sspec = importlib.util.spec_from_file_location("day08_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day08_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        enc = kit.encoder(p)
        for fr in scene_frames(i, sc):
            enc.stdin.write(fr.convert("RGB").tobytes())
        enc.stdin.close()
        enc.wait()
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({sc['dur']:.1f}s)")

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
