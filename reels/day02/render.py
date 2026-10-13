#!/usr/bin/env python3
"""Render the SPOT "Day 2" Instagram Reel: how a sample gets a yes (v2).

Usage:  python3 reels/day02/render.py
Output: reels/day02/out/spot_day02_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

Follows the 30-day plan (hook "Sample #17582."). Same look as Days 3–5:
Cormorant Garamond headlines, Inter labels, DAY tag, cream motion graphics,
real skin-test footage (reels/day03/footage) instead of an animation.
"""
import importlib.util
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
INK, CREAM, WHITE, RED = kit.INK, kit.CREAM, kit.WHITE, kit.STAMP_RED
GOLD = (176, 141, 87)
place, appear = kit.place, kit.appear
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer

TAG = kit.make_tag("02")


def frames(day, name, start, dur, speed=1.0):
    return d3.footage_frames(name, start, dur, speed, None, footage_dir=os.path.join(REELS, day, "footage"))


def still(name, blur_boxes=()):
    """Photo → blurred private/label areas → cover-cropped 1080x1920, graded."""
    img = Image.open(os.path.join(FOOTAGE, name)).convert("RGB")
    for box in blur_boxes:
        img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((x0, y0, x0 + W, y0 + H))
    return ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.06)).enhance(0.93)


POUCH = still("sample_pouch.jpg", [(0, 260, 275, 625)])        # laptop screen blurred
SHORTLIST = still("shortlist.jpg", [(306, 708, 404, 762)])     # "GEL Cleanser" label blurred
BOT_GRAD = kit.gradient(0.75, 1150, bottom=True)


# --------------------------------------------------------------------------- 1. hook: the pouch

H1 = title(["Sample #17582."], 112)
H1_K = kicker(["Every sample arrives like this.", "No brand. No name. Just a code."], 42)


def s_pouch(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(BOT_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1, W / 2, 1200, appear(t, 0.15, 0.6), rise=30)
    place(fr, d3.RULE, W / 2, 1300, appear(t, 0.7), rise=0)
    place(fr, H1_K, W / 2, 1390, appear(t, 0.9))


# --------------------------------------------------------------------------- 2. the five checks

TAG_INK = kit.text_layer(["DAY 02"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)
C_TITLE = serif_layer(["Before any formulation", "gets a yes, it must", "pass all five."], 72, INK, weight=600)
CHECKS = ["Texture", "Absorption", "Feel on skin", "Ingredients", "Fragrance"]
FAIL = 4
C_NUMS = [serif_layer([f"0{i + 1}"], 64, GOLD, weight=500, italic=True) for i in range(len(CHECKS))]
C_ITEMS = [serif_layer([c], 68, INK, weight=500, align="left") for c in CHECKS]
C_FOOT = serif_layer(["One fail and it's out."], 66, INK, weight=500, italic=True)
C_STAMP = kit.stamp("REJECTED", 50, angle=-8)
ROW0, ROW = 780, 132
X_NUM, X_TXT, X_MARK = 190, 270, 900
ITEM_T0, ITEM_STEP = 0.7, 0.55
STAMP_T = ITEM_T0 + ITEM_STEP * len(CHECKS) + 0.1
CARD_DUR = 5.4


def mark(ok, progress, size=70):
    """Animated tick (ink) or cross (red) in a thin ring, drawn at 4x for smooth edges."""
    s = 4
    img = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (INK if ok else RED) + (255,)
    d.ellipse([2 * s, 2 * s, (size - 2) * s, (size - 2) * s], outline=col, width=3 * s)
    k = kit.ease_out(progress)
    lw = 5 * s
    P = lambda x, y: (x * size * s, y * size * s)  # noqa: E731
    if ok:
        a, b, c = (0.28, 0.52), (0.44, 0.68), (0.74, 0.35)
        seg = k * 2
        e1 = min(seg, 1)
        d.line([P(*a), P(a[0] + (b[0] - a[0]) * e1, a[1] + (b[1] - a[1]) * e1)], fill=col, width=lw)
        if seg > 1:
            e2 = seg - 1
            d.line([P(*b), P(b[0] + (c[0] - b[0]) * e2, b[1] + (c[1] - b[1]) * e2)], fill=col, width=lw)
    else:
        for x0, y0, x1, y1 in ((0.3, 0.3, 0.7, 0.7), (0.7, 0.3, 0.3, 0.7)):
            d.line([P(x0, y0), P(x0 + (x1 - x0) * k, y0 + (y1 - y0) * k)], fill=col, width=lw)
    return img.resize((size, size), Image.LANCZOS)


def s_checks(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 196, 1, rise=0)
    place(fr, TAG_INK_SUB, W / 2, 254, 1, rise=0)
    place(fr, C_TITLE, W / 2, 500, appear(t, 0.05, 0.5))
    place(fr, Image.new("RGBA", (120, 2), GOLD + (255,)), W / 2, 668, appear(t, 0.4), rise=0)
    for i in range(len(CHECKS)):
        t0 = ITEM_T0 + i * ITEM_STEP
        p = appear(t, t0, 0.35)
        if p <= 0:
            continue
        y = ROW0 + i * ROW
        place(fr, C_NUMS[i], X_NUM, y, p, rise=18)
        place(fr, C_ITEMS[i], X_TXT + C_ITEMS[i].width / 2, y + 4, p, rise=18)
        if i < len(CHECKS) - 1:
            ln = Image.new("RGBA", (int((X_MARK + 40 - X_NUM + 40) * p), 1), INK + (40,))
            fr.alpha_composite(ln, (X_NUM - 40, int(y + ROW / 2)))
        if t >= t0 + 0.2:
            m = mark(i != FAIL, (t - t0 - 0.2) / 0.25)
            fr.alpha_composite(m, (X_MARK - m.width // 2, int(y - m.height / 2)))
    if t >= STAMP_T:
        # Strike through the failed check, then slam the stamp just below it.
        y = ROW0 + ROW * FAIL - 2
        strike = kit.ease_out((t - STAMP_T + 0.05) / 0.2)
        fr.alpha_composite(Image.new("RGBA", (int((C_ITEMS[FAIL].width + 10) * strike), 4), RED + (230,)),
                           (X_TXT - 5, int(y)))
        k = kit.ease_out((t - STAMP_T - 0.15) / 0.16)
        if t >= STAMP_T + 0.15:
            place(fr, C_STAMP, 700, ROW0 + ROW * FAIL + 92, min(1, k * 1.5), rise=0, scale=1.6 - 0.6 * k)
    place(fr, C_FOOT, W / 2, ROW0 + ROW * 5 + 130, appear(t, STAMP_T + 0.5))
    return fr


# --------------------------------------------------------------------------- 3–4. real testing

H3 = title(["Then we test it", "ourselves."], 104)
H3_K = kicker(["Look. Smell. Texture."], 42)


def s_inspect(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H3, W / 2, 500, appear(t, 0.15))
    place(fr, H3_K, W / 2, 690, appear(t, 0.9))


H4_WORDS = ["On skin.", "Rubbed in.", "Felt after."]
H4_LAYERS = [kit.with_shadow(serif_layer([w], 92), 14, 0.6) for w in H4_WORDS]


def s_skin(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    for i, lay in enumerate(H4_LAYERS):
        place(fr, lay, W / 2, 430 + i * 125, appear(t, 0.15 + i * 0.6), rise=25)


# --------------------------------------------------------------------------- 5. second look

H5 = title(["Pass every test?"], 112)
H5_I = kit.with_shadow(serif_layer(["Then it earns a second look."], 66, italic=True, weight=500), 14, 0.6)


def s_pipette(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H5, W / 2, 470, appear(t, 0.15))
    place(fr, H5_I, W / 2, 590, appear(t, 0.9))


# --------------------------------------------------------------------------- 6. 35 → 6

SAMPLES = 35
S6_PRE = title([f"From {SAMPLES} samples,"], 76)
S6_POST = kit.with_shadow(serif_layer(["made the shortlist."], 76, italic=True, weight=500), 14, 0.6)
COUNT0, COUNT1 = 0.35, 2.15


def s_count(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, S6_PRE, W / 2, 400, appear(t, 0.1))
    k = kit.ease_out((t - COUNT0) / (COUNT1 - COUNT0))
    n = round(SAMPLES + (6 - SAMPLES) * k)
    big = kit.with_shadow(serif_layer([f"only {n}" if k >= 1 else str(n)], 230), 20, 0.6)
    pop = 1.0 + 0.07 * max(0.0, 1 - (t - COUNT1) / 0.25) if t > COUNT1 else 1.0
    place(fr, big, W / 2, 600, appear(t, 0.3, 0.3), rise=20, scale=pop)
    place(fr, S6_POST, W / 2, 790, appear(t, COUNT1 + 0.1))


# --------------------------------------------------------------------------- 7. the question

H7 = title(["Only the best will", "carry the SPOT name."], 92)
H7_K = kicker(["Which one would you pick?", "Tell us in the comments."], 42)


def s_question(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H7, W / 2, 480, appear(t, 0.15))
    place(fr, H7_K, W / 2, 680, appear(t, 1.0))


# --------------------------------------------------------------------------- 8. end card

E_NEXT = serif_layer(["Day 3: the final cut."], 58, INK, weight=500, italic=True)


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
    dict(still=POUCH, dur=3.4, overlay=s_pouch, zoom=(1.0, 1.12), focus=(0.49, 0.3)),
    dict(card=s_checks, dur=CARD_DUR),
    dict(shots=[("day03", "founder_skin_test.mp4", 8.5, 2.8, 0.9)], overlay=s_inspect, zoom=(1.0, 1.06)),
    dict(shots=[("day03", "founder_skin_test.mp4", 32.0, 3.0, 1.0)], overlay=s_skin, zoom=(1.05, 1.1)),
    dict(shots=[("day03", "pipette_macro.mp4", 8.0, 2.8, 0.75)], overlay=s_pipette, zoom=(1.0, 1.06)),
    dict(still=SHORTLIST, dur=3.4, overlay=s_count, zoom=(1.0, 1.06), focus=(0.5, 0.7)),
    dict(still=SHORTLIST, dur=3.0, overlay=s_question, zoom=(1.12, 1.18), focus=(0.55, 0.75)),
    dict(card=s_end, dur=4.2),
]

CUES = dict(
    checks=[ITEM_T0 + i * ITEM_STEP + 0.2 for i in range(len(CHECKS))],
    fail=FAIL,
    stamp=STAMP_T + 0.15,
    count=(COUNT0, COUNT1),
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
    elif "still" in sc:
        src = (sc["still"] for _ in range(n))
    else:
        src = (img for day, clip, st, d, sp in sc["shots"] for img in frames(day, clip, st, d, sp))
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
    _sspec = importlib.util.spec_from_file_location("day02_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day02_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        render_scene(sc, p)
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
