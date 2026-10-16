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

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

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
L_T0, L_STEP = 0.8, 1.2
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


# --------------------------------------------------------------------------- editorial photo frames

FRAME_W, FRAME_H = 760, 950           # 4:5 frame for every photo
FRAME_CY = 1190
BORDER = 16


def enhance(img):
    """Phone photo → clean editorial grade: even contrast, softer reds, warm tone, crisp detail."""
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Color(img).enhance(0.86)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    r, g, b = img.split()
    img = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.03))), g, b.point(lambda v: int(v * 0.95))))
    return img.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=3))


def crop_to(img, w, h, fx=0.5, fy=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = int((img.width - w) * fx), int((img.height - h) * fy)
    return img.crop((x0, y0, x0 + w, y0 + h))


def photo_set(name, fx=0.5, fy=0.5):
    raw = Image.open(os.path.join(FOOTAGE, name)).convert("RGB")
    pic = enhance(raw)
    bg = crop_to(raw, W // 4, H // 4).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BICUBIC)
    bg = ImageEnhance.Brightness(ImageEnhance.Color(bg).enhance(0.7)).enhance(0.5)
    big = crop_to(pic, int(FRAME_W * 1.08), int(FRAME_H * 1.08), fx, fy)   # room for the inner push-in
    return bg.convert("RGBA"), big


SHADOW = Image.new("RGBA", (FRAME_W + 2 * BORDER + 160, FRAME_H + 2 * BORDER + 160), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW).rectangle([80, 100, 80 + FRAME_W + 2 * BORDER, 100 + FRAME_H + 2 * BORDER], fill=(0, 0, 0, 150))
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(30))


def framed_scene(name, lines, k_lines=None, tilt=-2.0, fx=0.5, fy=0.5, size=88):
    bg, big = photo_set(name, fx, fy)
    h = title(lines, size)
    k = kicker(k_lines, 40) if k_lines else None

    def card(t, T):
        fr = bg.copy()
        fr.alpha_composite(kit.TOP_GRAD)
        place(fr, TAG, W / 2, 215, 1, rise=0)
        # inner slow push-in
        z = 1.0 + 0.07 * kit.ease_in_out(t / T)
        cw, ch = big.width / z / 1.0, big.height / z
        x0, y0 = (big.width - cw) / 2, (big.height - ch) / 2
        inner = big.resize((FRAME_W, FRAME_H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        framed = Image.new("RGBA", (FRAME_W + 2 * BORDER, FRAME_H + 2 * BORDER), (250, 248, 244, 255))
        framed.paste(inner, (BORDER, BORDER))
        # settle in: small scale-up and tilt easing to rest
        k_in = kit.ease_out(t / 0.7)
        ang = tilt * (1.6 - 0.6 * k_in)
        sc = 0.94 + 0.06 * k_in
        layer = Image.new("RGBA", SHADOW.size, (0, 0, 0, 0))
        layer.alpha_composite(SHADOW)
        layer.alpha_composite(framed, (80, 80))
        layer = layer.rotate(ang, resample=Image.BICUBIC, expand=True)
        place(fr, layer, W / 2, FRAME_CY, min(1, t / 0.25), rise=30 * (1 - k_in), scale=sc)
        place(fr, h, W / 2, 440, appear(t, 0.25))
        if k:
            place(fr, k, W / 2, 440 + h.height / 2 + 40, appear(t, 0.9))
        return fr
    return card


# --------------------------------------------------------------------------- interstitial + closing cards

I_KICK = kit.text_layer(["BEAUTY ASIA  ·  EXPO CENTRE"], kit.F_SEMIBOLD, 30, GOLD, tracking=8)
I_TITLE = serif_layer(["One expo.", "Real conversations.", "One question:"], 88, INK, weight=600)
I_Q = serif_layer(["what makes skincare", "worth trusting?"], 76, INK, weight=500, italic=True)


def s_intro(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, I_KICK, W / 2, 560, appear(t, 0.05))
    place(fr, L_RULE, W / 2, 615, appear(t, 0.2), rise=0)
    place(fr, I_TITLE, W / 2, 800, appear(t, 0.3, 0.6))
    place(fr, I_Q, W / 2, 1080, appear(t, 1.3, 0.6))
    return fr


C_TITLE = serif_layer(["Everything we learned", "goes into SPOT."], 88, INK, weight=600)
C_SUB = serif_layer(["Formulas worth explaining."], 64, GOLD, weight=500, italic=True)


def s_close(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, C_TITLE, W / 2, 820, appear(t, 0.2, 0.6))
    place(fr, L_RULE, W / 2, 960, appear(t, 0.8), rise=0)
    place(fr, C_SUB, W / 2, 1040, appear(t, 1.0, 0.6))
    return fr


# --------------------------------------------------------------------------- timeline

SCENES = [
    dict(clip=("expo_arrival.mp4", 0.0, 4.2, 0.95), overlay=s_arrive, zoom=(1.0, 1.08)),
    dict(card=s_intro, dur=3.4),
    dict(card=framed_scene("walking_hall.jpg", ["Hall after hall.", "Brand after brand."], tilt=-2.0, fy=0.35), dur=3.8),
    dict(card=framed_scene("ingredient_booth.jpg", ["We met ingredient", "suppliers."],
                           ["Where does every raw material come from?"], tilt=2.0, fx=0.45, fy=0.55), dur=4.0),
    dict(clip=("skin_analyzer.mp4", 0.0, 2.8, 0.42), overlay=headline_scene(["Saw the newest", "skin tech."], 96),
         zoom=(1.0, 1.06)),
    dict(card=framed_scene("taking_notes.jpg", ["Asked questions.", "Took notes."], ["Lots of notes."],
                           tilt=-1.6, fx=0.62, fy=0.4), dur=4.0),
    dict(card=s_lessons, dur=6.0),
    dict(card=framed_scene("walking_hall_2.jpg", ["Came home with ideas."], ["(and a few bags)"],
                           tilt=1.8, fy=0.4), dur=3.6),
    dict(card=s_close, dur=3.4),
    dict(card=s_end, dur=4.5),
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
