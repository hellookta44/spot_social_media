#!/usr/bin/env python3
"""Render the SPOT "Day 1" Instagram Reel (1080x1920, 30 fps).

Usage:  python3 reels/day01/render.py
Output: reels/day01/out/spot_day01_reel.mp4 and spot_day01_cover.jpg

Needs ffmpeg, Pillow and numpy. Fonts: Inter / Inter Display.
"""
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTAGE = os.path.join(HERE, "footage")
OUT = os.path.join(HERE, "out")

W, H, FPS = 1080, 1920, 30
XFADE = 0.25  # seconds of crossfade between scenes

FONT_DIR = "/usr/share/fonts/opentype/inter"
F_DISPLAY_LIGHT = os.path.join(FONT_DIR, "InterDisplay-Light.otf")
F_DISPLAY_XLIGHT = os.path.join(FONT_DIR, "InterDisplay-ExtraLight.otf")
F_DISPLAY_THIN = os.path.join(FONT_DIR, "InterDisplay-Thin.otf")
F_MEDIUM = os.path.join(FONT_DIR, "Inter-Medium.otf")
F_SEMIBOLD = os.path.join(FONT_DIR, "Inter-SemiBold.otf")

INK = (34, 32, 30)
CREAM = (245, 241, 235)
WHITE = (255, 255, 255)
STAMP_RED = (200, 58, 44)

HANDLE = "@shopspotbeauty"


# --------------------------------------------------------------------------- helpers

def font(path, size):
    return ImageFont.truetype(path, size)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = min(max(t, 0.0), 1.0)
    return 3 * t * t - 2 * t * t * t


def appear(t, start, dur=0.45):
    """0..1 progress of an element that appears at `start`."""
    return ease_out((t - start) / dur)


def text_layer(lines, font_path, size, color, tracking=0, line_gap=1.18, align="center"):
    """Render text lines to a tight RGBA image."""
    f = font(font_path, size)
    widths = []
    for ln in lines:
        if tracking:
            widths.append(sum(f.getlength(c) + tracking for c in ln) - tracking)
        else:
            widths.append(f.getlength(ln))
    lh = int(size * line_gap)
    w = int(max(widths)) + 8
    h = lh * len(lines) + int(size * 0.3)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = {"center": (w - widths[i]) / 2, "left": 0}[align]
        y = i * lh
        if tracking:
            for c in ln:
                d.text((x, y), c, font=f, fill=color)
                x += f.getlength(c) + tracking
        else:
            d.text((x, y), ln, font=f, fill=color)
    return img


def with_shadow(img, radius=14, opacity=0.55):
    """Soft dark glow behind white text so it reads on busy footage."""
    pad = radius * 3
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    alpha = img.split()[3].point(lambda a: int(a * opacity))
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 255), (pad, pad + 3), alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
    out.alpha_composite(shadow)
    out.alpha_composite(img, (pad, pad))
    return out


def place(frame, layer, cx, cy, progress=1.0, rise=40, scale=1.0):
    """Composite `layer` centred at (cx, cy) with fade + upward slide."""
    if progress <= 0:
        return
    lay = layer
    if scale != 1.0:
        lay = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))),
                           Image.LANCZOS)
    if progress < 1:
        a = lay.split()[3].point(lambda v: int(v * progress))
        lay = lay.copy()
        lay.putalpha(a)
    y = cy - lay.height / 2 + rise * (1 - progress)
    frame.alpha_composite(lay, (int(cx - lay.width / 2), int(y)))


def make_logo(height, color=INK):
    """Vector re-draw of the SPOT. wordmark (thin S P T, double-ring O, dot)."""
    s = 4  # supersample
    hh = height * s
    f = font(F_DISPLAY_XLIGHT, int(hh * 1.36))
    stroke = max(2, int(hh * 0.045))
    gap = int(hh * 0.22)
    o_w = int(hh * 0.78)
    letters = ["S", "P", "O", "T", "."]
    widths = []
    for c in letters:
        if c == "O":
            widths.append(o_w)
        elif c == ".":
            widths.append(int(hh * 0.16))
        else:
            bb = f.getbbox(c)
            widths.append(bb[2] - bb[0])
    total = sum(widths) + gap * 4 + int(hh * 0.06)
    img = Image.new("RGBA", (total + 4 * s, hh + 4 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 2 * s
    for c, w in zip(letters, widths):
        if c == "O":
            d.ellipse([x, 0, x + w, hh], outline=color, width=stroke)
            ins = int(hh * 0.075)
            d.ellipse([x + ins, ins, x + w - ins, hh - ins], outline=color, width=stroke)
            x += w + gap
        elif c == ".":
            r = int(hh * 0.07)
            d.ellipse([x, hh - 2 * r, x + 2 * r, hh], fill=color)
        else:
            bb = f.getbbox(c)
            d.text((x - bb[0], -bb[1]), c, font=f, fill=color)
            # scale glyph height to cap height == hh
            x += w + gap
    # glyph cap height may differ slightly from hh; crop to content
    img = img.crop(img.getbbox())
    return img.resize((max(1, img.width // s), max(1, img.height // s)), Image.LANCZOS)


def stamp(text="REJECTED", size=72, color=STAMP_RED, angle=-12):
    f = font(F_SEMIBOLD, size)
    tracking = size * 0.12
    tw = sum(f.getlength(c) + tracking for c in text) - tracking
    padx, pady = int(size * 0.55), int(size * 0.38)
    w, h = int(tw + 2 * padx), int(size * 1.15 + 2 * pady)
    img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw = max(4, size // 12)
    d.rounded_rectangle([10, 10, 10 + w, 10 + h], radius=size // 5, outline=color + (235,), width=bw)
    d.rounded_rectangle([10 + bw * 2, 10 + bw * 2, 10 + w - bw * 2, 10 + h - bw * 2],
                        radius=size // 7, outline=color + (160,), width=max(2, bw // 2))
    x = 10 + padx
    for c in text:
        d.text((x, 10 + pady - size * 0.05), c, font=f, fill=color + (235,))
        x += f.getlength(c) + tracking
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)


def gradient(top_alpha=0.55, height=900, bottom=False):
    """Vertical black gradient (top or bottom) to lift text legibility."""
    a = np.zeros((H, 1), dtype=np.float32)
    ramp = np.linspace(1, 0, height) ** 1.6 * top_alpha
    if bottom:
        a[H - height:, 0] = ramp[::-1]
    else:
        a[:height, 0] = ramp
    alpha = (np.repeat(a, W, axis=1) * 255).astype(np.uint8)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g.putalpha(Image.fromarray(alpha))
    return g


# --------------------------------------------------------------------------- footage

GRADE = "eq=contrast=1.06:saturation=0.9:brightness=0.01,colorbalance=rs=0.03:gs=0.01:bs=-0.03"


def footage_frames(name, start, dur):
    """Yield graded 1080x1920 RGB frames from a source clip (auto-rotated)."""
    src = os.path.join(FOOTAGE, name)
    n = int(round(dur * FPS))
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur + 0.5), "-i", src,
           "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                  f"crop={W}:{H},{GRADE}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = W * H * 3
    last = None
    for _ in range(n):
        buf = p.stdout.read(size)
        if len(buf) == size:
            last = Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1)
        yield last.copy()
    p.stdout.close()
    p.wait()


def ken_burns(img, t, z0=1.0, z1=1.07, fx=0.5, fy=0.5):
    z = z0 + (z1 - z0) * ease_in_out(t)
    if z == 1.0:
        return img
    cw, ch = W / z, H / z
    x0 = (W - cw) * fx
    y0 = (H - ch) * fy
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


# --------------------------------------------------------------------------- scenes
# Each scene: list of (clip, start, dur) shots, plus an overlay(frame, t, T) callback.

TOP_GRAD = gradient(0.6, 1000)
BOT_GRAD = gradient(0.35, 700, bottom=True)

TAG = with_shadow(text_layer(["DAY 01  ·  BUILDING SPOT"], F_MEDIUM, 30, WHITE, tracking=5), 8, 0.4)


def headline(lines, size=78):
    return with_shadow(text_layer(lines, F_DISPLAY_LIGHT, size, WHITE, line_gap=1.16))


def sub(lines, size=40):
    return with_shadow(text_layer(lines, F_MEDIUM, size, (240, 236, 230), line_gap=1.3), 10, 0.5)


# Scene 1 — hook: 700+ counter over the rejected samples
S1_LABEL = sub(["samples rejected."], 54)
S1_PRE = headline(["We said no to"], 64)


def s1_overlay(fr, t, T):
    fr.alpha_composite(TOP_GRAD)
    place(fr, TAG, W / 2, 250, appear(t, 0.0, 0.35), rise=0)
    place(fr, S1_PRE, W / 2, 600, appear(t, 0.1))
    k = ease_out((t - 0.25) / 1.6)
    n = int(round(700 * k))
    label = f"{n}+" if k >= 1 else f"{n}"
    big = with_shadow(text_layer([label], F_DISPLAY_LIGHT, 300, WHITE), 18, 0.5)
    pop = 1.0 + 0.06 * max(0.0, 1 - (t - 1.85) / 0.25) if t > 1.85 else 1.0
    place(fr, big, W / 2, 850, appear(t, 0.2, 0.3), rise=20, scale=pop)
    place(fr, S1_LABEL, W / 2, 1090, appear(t, 1.0))


# Scene 2 — on the road
S2_H = headline(["Day 1 didn't start", "in a lab."])
S2_S = sub(["It started on the road —", "meeting manufacturer after manufacturer."])


def s2_overlay(fr, t, T):
    fr.alpha_composite(TOP_GRAD)
    place(fr, TAG, W / 2, 250, 1, rise=0)
    place(fr, S2_H, W / 2, 470, appear(t, 0.15))
    place(fr, S2_S, W / 2, 680, appear(t, 0.9))


# Scene 3 — samples arriving
S3_H = headline(["Sample after sample", "landed on our desk."])
S3_S = sub(["Every one opened. Every one tested."])


def s3_overlay(fr, t, T):
    fr.alpha_composite(TOP_GRAD)
    place(fr, TAG, W / 2, 250, 1, rise=0)
    place(fr, S3_H, W / 2, 470, appear(t, 0.15))
    place(fr, S3_S, W / 2, 660, appear(t, 0.9))


# Scene 4 — rejections
S4_H = headline(["Most of them?"])
STAMPS = [
    (stamp("REJECTED", 70, angle=-11), 300, 1000, 0.55),
    (stamp("REJECTED", 62, angle=8), 760, 1240, 1.15),
    (stamp("REJECTED", 78, angle=-4), 470, 1480, 1.75),
]
S4_S = sub(["“Good enough” wasn't good enough."], 44)


def s4_overlay(fr, t, T):
    fr.alpha_composite(TOP_GRAD)
    fr.alpha_composite(BOT_GRAD)
    place(fr, TAG, W / 2, 250, 1, rise=0)
    place(fr, S4_H, W / 2, 440, appear(t, 0.1))
    for img, x, y, t0 in STAMPS:
        if t >= t0:
            k = ease_out((t - t0) / 0.16)
            place(fr, img, x, y, min(1, k * 1.5), rise=0, scale=1.6 - 0.6 * k)
    place(fr, S4_S, W / 2, 600, appear(t, 2.4))


# Scene 5 — the standard
S5_H = headline(["Because your skin", "deserves the one", "that's right."])
S5_S = sub(["Not the one that's easy."])


def s5_overlay(fr, t, T):
    fr.alpha_composite(TOP_GRAD)
    place(fr, TAG, W / 2, 250, 1, rise=0)
    place(fr, S5_H, W / 2, 520, appear(t, 0.15))
    place(fr, S5_S, W / 2, 760, appear(t, 1.2))


# Scene 6 — end card (cream, logo)
LOGO = make_logo(150)
E_LINE1 = text_layer(["Serums & a face cleanser."], F_DISPLAY_LIGHT, 50, INK)
E_LINE2 = text_layer(["COMING SOON"], F_MEDIUM, 30, (120, 112, 104), tracking=8)
E_FOLLOW = text_layer(["Follow the journey from Day 1"], F_DISPLAY_LIGHT, 40, INK)
E_HANDLE = text_layer([HANDLE], F_MEDIUM, 40, INK, tracking=1)
E_RULE = Image.new("RGBA", (120, 2), INK + (255,))


def s6_frame(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    k = appear(t, 0.1, 0.9)
    place(fr, LOGO, W / 2, 700, k, rise=0, scale=0.94 + 0.06 * k)
    place(fr, E_LINE1, W / 2, 900, appear(t, 0.7))
    place(fr, E_LINE2, W / 2, 975, appear(t, 0.9))
    place(fr, E_RULE, W / 2, 1080, appear(t, 1.2), rise=0)
    place(fr, E_FOLLOW, W / 2, 1170, appear(t, 1.4))
    place(fr, E_HANDLE, W / 2, 1240, appear(t, 1.6))
    return fr


SCENES = [
    dict(shots=[("rejected_samples.mp4", 0.0, 3.3)], overlay=s1_overlay, zoom=(1.0, 1.08)),
    dict(shots=[("road.mp4", 12.0, 1.3), ("road.mp4", 15.7, 3.0)], overlay=s2_overlay, zoom=(1.02, 1.08)),
    dict(shots=[("sample_package.mp4", 0.0, 3.8)], overlay=s3_overlay, zoom=(1.0, 1.06)),
    dict(shots=[("rejected_samples.mp4", 3.6, 3.9)], overlay=s4_overlay, zoom=(1.08, 1.0)),
    dict(shots=[("serum_dropper.mp4", 0.0, 4.4)], overlay=s5_overlay, zoom=(1.0, 1.07)),
    dict(card=s6_frame, dur=4.2),
]


# --------------------------------------------------------------------------- render

def encoder(path):
    return subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", path],
        stdin=subprocess.PIPE)


def render_scene(i, sc, path, cover_path=None):
    enc = encoder(path)
    if "card" in sc:
        T = sc["dur"]
        for f in range(int(round(T * FPS))):
            enc.stdin.write(sc["card"](f / FPS, T).convert("RGB").tobytes())
    else:
        T = sum(s[2] for s in sc["shots"])
        z0, z1 = sc["zoom"]
        f = 0
        for clip, start, dur in sc["shots"]:
            for img in footage_frames(clip, start, dur):
                t = f / FPS
                fr = ken_burns(img, t / T, z0, z1).convert("RGBA")
                sc["overlay"](fr, t, T)
                if cover_path and abs(t - 2.6) < 0.5 / FPS:
                    fr.convert("RGB").save(cover_path, quality=92)
                enc.stdin.write(fr.convert("RGB").tobytes())
                f += 1
    enc.stdin.close()
    enc.wait()
    return T


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day01_")
    parts, durs = [], []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        cover = os.path.join(OUT, "spot_day01_cover.jpg") if i == 0 else None
        durs.append(render_scene(i, sc, p, cover))
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({durs[-1]:.1f}s)")

    # Chain crossfades between scenes, add a silent stereo track (add music in Instagram).
    inputs = []
    for p in parts:
        inputs += ["-i", p]
    chain, last, offset = [], "[0:v]", 0.0
    for i in range(1, len(parts)):
        offset += durs[i - 1] - XFADE
        xf = 0.45 if i == len(parts) - 1 else XFADE
        if xf != XFADE:
            offset -= xf - XFADE
        out = f"[v{i}]"
        chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={xf}:offset={offset:.3f}{out}")
        last = out
    total = offset + durs[-1]
    final = os.path.join(OUT, "spot_day01_reel.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs,
         "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex", ";".join(chain),
         "-map", last, "-map", f"{len(parts)}:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", "-shortest", final],
        check=True)
    shutil.rmtree(tmp)
    print(f"wrote {final} ({total:.1f}s)")


if __name__ == "__main__":
    main()
