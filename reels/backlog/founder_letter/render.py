#!/usr/bin/env python3
"""Render the SPOT founder letter reel (backlog, was Day 8 v2): why I started SPOT, typewritten.

Usage:  python3 reels/backlog/founder_letter/render.py
Output: reels/backlog/founder_letter/out/spot_letter_reel.mp4 (+ _no_music, music .wav)
        Cover: python3 reels/covers.py

No footage: a letter is typed live on cream paper. The camera rides the typing
line, pulls back to show the whole page on the desk, a gold pen underlines the
key words, a red pen strikes "Big promises.", and the letter is signed in ink.
"""
import importlib.util
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.join(HERE, "..")
_spec = importlib.util.spec_from_file_location("day03_render", os.path.join(REELS, "day03", "render.py"))
d3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d3)
kit = d3.kit

OUT = os.path.join(HERE, "out")
W, H, FPS = kit.W, kit.H, kit.FPS
LAST_XFADE = d3.LAST_XFADE
INK, CREAM = kit.INK, kit.CREAM
place, appear = kit.place, kit.appear
serif_layer = d3.serif_layer

S = 2                                   # the page is drawn at 2x so close-ups stay crisp
PW, PH = W * S, H * S
TYPE_INK = (30, 28, 34)
GOLD_PEN = (164, 122, 58)
RED_PEN = (178, 52, 40)
SIGN_INK = (36, 44, 92)
DESK = (34, 28, 25)
F_TYPE = "/usr/share/fonts/X11/Type1/c0419bt_.pfb"       # Courier 10 Pitch (typewriter face)
F_TYPE_BOLD = "/usr/share/fonts/X11/Type1/c0583bt_.pfb"
rng = np.random.default_rng(8)

TAG_INK = kit.text_layer(["DAY 08"], kit.F_SEMIBOLD, 64, INK, tracking=10)
TAG_INK_SUB = kit.text_layer(["BUILDING SPOT"], kit.F_MEDIUM, 28, INK, tracking=7)

# --------------------------------------------------------------------------- the letter

HEAD = "WHY I STARTED SPOT."
PARAS = [
    "Dear you,",
    "I started SPOT because I couldn't find skincare I actually trusted.",
    "Long labels. Big promises. Nobody explaining what's inside.",
    "So I asked questions. I tested 35 samples. I visited 15 factories. I said no. A lot.",
    "SPOT is the skincare I wanted to find:",
    "simple, honest, explained.",
    "If I wouldn't put it on my own skin, it doesn't go into SPOT.",
]
GAP_AFTER = [1, 1, 1, 1, 0, 1, 0]       # blank line after each paragraph
MARKS = [  # (phrase, pen) drawn in this order after the pull-back
    ("Big promises.", "strike"),
    ("actually trusted.", "under"),
    ("35 samples.", "under"),
    ("15 factories.", "under"),
    ("simple, honest, explained.", "under"),
]

HEAD_SIZE, BODY_SIZE = 50 * S, 40 * S
LEFT, RIGHT = 120 * S, 960 * S
HEAD_Y, BODY_Y, LINE_H = 400 * S, 540 * S, 60 * S
f_head = ImageFont.truetype(F_TYPE_BOLD, HEAD_SIZE)
f_body = ImageFont.truetype(F_TYPE, BODY_SIZE)
CW_HEAD, CW_BODY = f_head.getlength("M"), f_body.getlength("M")


def layout():
    """Every typed character: (x, y, ch, font, line). Positions are page pixels (2x)."""
    chars = []
    x = (PW - CW_HEAD * len(HEAD)) / 2
    for c in HEAD:
        chars.append([x, HEAD_Y, c, f_head, 0])
        x += CW_HEAD
    per_line = int((RIGHT - LEFT) // CW_BODY)
    line, y = 1, BODY_Y
    for p, gap in zip(PARAS, GAP_AFTER):
        rows, cur = [], ""
        for word in p.split(" "):
            if cur and len(cur) + 1 + len(word) > per_line:
                rows.append(cur)
                cur = word
            else:
                cur = f"{cur} {word}" if cur else word
        rows.append(cur)
        for r_i, row in enumerate(rows):
            for k, c in enumerate(row + (" " if r_i < len(rows) - 1 else "")):
                chars.append([LEFT + k * CW_BODY, y, c, f_body, line])
            line += 1
            y += LINE_H
        chars[-1].append("para")
        y += LINE_H * gap
    return chars, y


CHARS, TEXT_END_Y = layout()
SIGN_Y = TEXT_END_Y + 10 * S


def schedule():
    """Keystroke times: steady rhythm, little human jitter, pauses at punctuation and line ends."""
    t, times, returns = 0.35, [], []
    for i, ch in enumerate(CHARS):
        times.append(t)
        c = ch[2]
        step = (0.045 if ch[4] == 0 else 0.044) * rng.uniform(0.75, 1.3)
        if c in ".:":
            step += 0.20
        elif c == ",":
            step += 0.10
        nxt = CHARS[i + 1] if i + 1 < len(CHARS) else None
        if nxt is not None and nxt[4] != ch[4]:
            step += 0.42 if len(ch) > 5 or ch[4] == 0 else 0.22
            returns.append(t + 0.12)
        t += step
    return np.array(times), returns, t


KEY_T, RETURN_T, TYPE_END = schedule()

# --------------------------------------------------------------------------- paper, ink, pens


def make_paper():
    base = np.ones((PH, PW, 3), np.float32) * np.array([244, 239, 230], np.float32)
    lo = np.array(Image.fromarray((rng.random((PH // 64, PW // 64)) * 255).astype(np.uint8))
                  .resize((PW, PH), Image.BICUBIC), np.float32) / 255 - 0.5
    fine = rng.normal(0, 1, (PH, PW)).astype(np.float32)
    fibre = np.array(Image.fromarray(np.clip(fine * 40 + 128, 0, 255).astype(np.uint8))
                     .filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255 - 0.5
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    vig = ((xx / PW - 0.5) ** 2 + (yy / PH - 0.42) ** 2) * 0.32
    light = 1.0 - vig + 0.012 * lo + 0.03 * fibre
    out = base * light[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


PAPER = make_paper()
GRAIN = Image.fromarray(np.clip(rng.normal(246, 18, (PH, PW)), 0, 255).astype(np.uint8))
INK_FILL = Image.new("RGB", (PW, PH), TYPE_INK)


def strike_masks():
    """One ink mask per typed character, struck unevenly like a real typewriter."""
    masks = []
    for x, y, c, f, *_ in CHARS:
        if c == " ":
            masks.append(None)
            continue
        size = int(f.size * 1.4)
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).text((0, 0), c, font=f, fill=int(255 * rng.uniform(0.86, 1.0)))
        if rng.random() < 0.25:  # uneven strike: one side of the letter lighter
            g = np.linspace(rng.uniform(0.7, 0.9), 1, size)[None, :]
            m = Image.fromarray((np.array(m) * (g if rng.random() < 0.5 else g[:, ::-1])).astype(np.uint8))
        masks.append((m.filter(ImageFilter.GaussianBlur(0.7)),
                      int(x + rng.normal(0, 0.8)), int(y + rng.normal(0, 1.2))))
    return masks


MASKS = strike_masks()


def phrase_spans(phrase):
    """(x0, x1, top_y) per line covered by `phrase`, in page pixels."""
    text = "".join(c[2] for c in CHARS)
    i = text.index(phrase)
    spans = {}
    for ch in CHARS[i:i + len(phrase)]:
        if ch[2] == " ":
            continue
        x0, x1, _ = spans.get(ch[4], (ch[0], ch[0], ch[1]))
        spans[ch[4]] = (min(x0, ch[0]), max(x1, ch[0] + CW_BODY), ch[1])
    return list(spans.values())


def pen_stroke(x0, x1, y, seed):
    r = np.random.default_rng(seed)
    n = 40
    xs = np.linspace(x0 - 6 * S, x1 + 8 * S, n)
    ys = y + 2.2 * S * np.sin(np.linspace(0, r.uniform(2, 4) * np.pi, n) + r.uniform(0, 6)) \
        + np.linspace(r.uniform(-2, 2) * S, r.uniform(-5, -1) * S, n)
    return list(zip(xs, ys))


STROKES = []  # (mark index, points, colour, width)
for k, (phrase, pen) in enumerate(MARKS):
    for x0, x1, y in phrase_spans(phrase):
        yy = y + (BODY_SIZE * 0.52 if pen == "strike" else BODY_SIZE * 1.02)
        STROKES.append((k, pen_stroke(x0, x1, yy, k * 7 + int(x0)), RED_PEN if pen == "strike" else GOLD_PEN,
                        5 * S if pen == "strike" else 6 * S))


def draw_strokes(img, prog_per_mark):
    d = ImageDraw.Draw(img)
    for k, pts, col, wd in STROKES:
        p = prog_per_mark[k]
        if p <= 0:
            continue
        m = max(2, int(round(len(pts) * min(1, p))))
        d.line(pts[:m], fill=col, width=wd, joint="curve")
        for px, py in (pts[0], pts[m - 1]):
            d.ellipse([px - wd / 2, py - wd / 2, px + wd / 2, py + wd / 2], fill=col)


SIGN_TEXT = serif_layer(["Founder, SPOT"], 74 * S, SIGN_INK, weight=500, italic=True)
SIGN_DASH = Image.new("RGBA", (60 * S, 3 * S), SIGN_INK + (255,))
SIGN_X = LEFT + 80 * S


def draw_signature(img, p):
    """Write-on: soft-edged wipe left to right."""
    if p <= 0:
        return
    w = SIGN_TEXT.width
    edge = np.clip((p * (w + 80 * S) - np.arange(w)) / (80 * S), 0, 1)
    a = (np.array(SIGN_TEXT.getchannel("A"), np.float32) * edge[None, :]).astype(np.uint8)
    img.paste(SIGN_INK, (SIGN_X, SIGN_Y), Image.fromarray(a))
    dw = int(SIGN_DASH.width * min(1, p * 4))
    if dw > 0:
        img.paste(SIGN_INK, (LEFT, SIGN_Y + SIGN_TEXT.height // 2 - 2 * S),
                  SIGN_DASH.getchannel("A").crop((0, 0, dw, SIGN_DASH.height)))


# --------------------------------------------------------------------------- timeline

PULL_T0 = TYPE_END + 0.5
PULL_DUR = 1.9
MARK_T0 = PULL_T0 + PULL_DUR + 0.2
MARK_DUR, MARK_GAP = 0.55, 0.32
MARK_T = [MARK_T0 + k * (MARK_DUR + MARK_GAP) for k in range(len(MARKS))]
SIGN_T0 = MARK_T[-1] + MARK_DUR + 0.35
SIGN_DUR = 1.4
LETTER_DUR = SIGN_T0 + SIGN_DUR + 1.6
END_DUR = 4.5
Z_CLOSE, Z_FAR = 1.45, 0.92


def typed_count(t):
    return int(np.searchsorted(KEY_T, t, side="right"))


def cursor_target(n):
    ch = CHARS[max(0, min(n, len(CHARS) - 1))]
    return ch[0] / S, ch[1] / S


def compose_page(n, t):
    """Whole page at 2x with n characters, pen marks and signature (used once the camera is wide)."""
    mask = Image.new("L", (PW, PH), 0)
    for m in MASKS[:n]:
        if m:
            mask.paste(m[0], (m[1], m[2]), m[0])
    page = Image.composite(INK_FILL, PAPER, ImageChops.multiply(mask, GRAIN))
    draw_strokes(page, [(t - mt) / MARK_DUR for mt in MARK_T])
    draw_signature(page, (t - SIGN_T0) / SIGN_DUR)
    return page


SHADOW = Image.new("L", (W + 200, H + 200), 0)
ImageDraw.Draw(SHADOW).rectangle([100, 120, W + 100, H + 110], fill=170)
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(40))
TOP_FADE = Image.new("RGBA", (W, 480), (240, 235, 226, 255))
TOP_FADE.putalpha(Image.fromarray((255 * np.clip((480 - np.arange(480)) / 200, 0, 1) ** 1.5)[:, None]
                                  .repeat(W, 1).astype(np.uint8)))


def letter_frames():
    """Yield every frame of the letter scene."""
    mask = Image.new("L", (PW, PH), 0)
    drawn = 0
    cx, cy = cursor_target(0)
    full, full_key = None, None
    for f in range(int(round(LETTER_DUR * FPS))):
        t = f / FPS
        n = typed_count(t)
        while drawn < n:
            m = MASKS[drawn]
            if m:
                mask.paste(m[0], (m[1], m[2]), m[0])
            drawn += 1
        tx, ty = cursor_target(n)
        p = kit.ease_in_out((t - PULL_T0) / PULL_DUR) if t > PULL_T0 else 0.0
        z = Z_CLOSE + (Z_FAR - Z_CLOSE) * p
        if p == 0:
            cx += (tx - cx) * 0.14
            cy += (ty - 110 - cy) * 0.10
            ccx, ccy = cx, cy
        else:
            q = min(1, p / 0.6)
            ccx, ccy = cx + (W / 2 - cx) * q, cy + (H / 2 - cy) * q
        if z >= 1:
            ww, wh = PW / z, PH / z
            x0 = min(max(ccx * S - ww / 2, 0), PW - ww)
            y0 = min(max(ccy * S - wh / 2, 0), PH - wh)
            if n and t - KEY_T[n - 1] < 0.035 and t < PULL_T0:  # tiny strike jolt
                y0 = min(y0 + 1.5 * S, PH - wh)
            box = tuple(int(round(v)) for v in (x0, y0, x0 + ww, y0 + wh))
            ink = ImageChops.multiply(mask.crop(box), GRAIN.crop(box))
            fr = Image.composite(INK_FILL.crop(box), PAPER.crop(box), ink).resize((W, H), Image.LANCZOS)
            fr = fr.convert("RGBA")
            fr.alpha_composite(TOP_FADE)
            ty1, ty2 = 196, 254
        else:
            key = None if t >= MARK_T0 - 0.05 else n
            if full is None or key is None or key != full_key:
                full, full_key = compose_page(n, t).resize((W, H), Image.LANCZOS), key
            fr = Image.new("RGBA", (W, H), DESK + (255,))
            sw, sh = int(W * z), int(H * z)
            sx, sy = (W - sw) // 2, (H - sh) // 2
            sh_img = SHADOW.resize((int(SHADOW.width * z), int(SHADOW.height * z)))
            fr.paste((0, 0, 0), (sx - int(100 * z), sy - int(100 * z)), sh_img)
            fr.paste(full.resize((sw, sh), Image.LANCZOS), (sx, sy))
            # the tag rides on the paper as it shrinks
            ty1, ty2 = sy + 196 * z, sy + 254 * z
        place(fr, TAG_INK, W / 2, ty1, 1, rise=0)
        place(fr, TAG_INK_SUB, W / 2, ty2, 1, rise=0)
        yield fr


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


CUES = dict(keys=[(float(t), CHARS[i][2]) for i, t in enumerate(KEY_T)], returns=RETURN_T,
            type_end=TYPE_END, pull=PULL_T0, marks=[(mt, MARK_DUR, pen) for mt, (_, pen) in zip(MARK_T, MARKS)],
            sign=(SIGN_T0, SIGN_DUR))


def scene_timing():
    start_end = LETTER_DUR - LAST_XFADE
    return [0.0, start_end], start_end + END_DUR


def main():
    _sspec = importlib.util.spec_from_file_location("letter_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_letter_")
    parts = [os.path.join(tmp, "letter.mp4"), os.path.join(tmp, "end.mp4")]
    enc = kit.encoder(parts[0])
    for fr in letter_frames():
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"letter rendered ({LETTER_DUR:.1f}s)")
    enc = kit.encoder(parts[1])
    for f in range(int(round(END_DUR * FPS))):
        enc.stdin.write(s_end(f / FPS, END_DUR).convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_letter_music.wav"))
    print(f"wrote {score_path}")

    video = os.path.join(tmp, "video.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", parts[0], "-i", parts[1], "-filter_complex",
         f"[0:v][1:v]xfade=transition=fade:duration={LAST_XFADE}:offset={starts[1]:.3f}[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-r", str(FPS), video],
        check=True)
    for name, audio in [("spot_letter_reel.mp4", ["-i", score_path]),
                        ("spot_letter_reel_no_music.mp4",
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
