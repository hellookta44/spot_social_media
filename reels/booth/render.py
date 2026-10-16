#!/usr/bin/env python3
"""Render the SPOT "Our booth at Beauty Asia" recap reel (animated, 1080x1920, 30 fps).

Usage:  python3 reels/booth/render.py
Output: reels/booth/out/spot_booth_reel.mp4 (+ _no_music, music .wav, cover .jpg, design board .png)

We had a booth but no footage, so the reel says so ("We were too busy talking to
film it. So we drew it for you.") and retells the day as an illustrated recap:
the booth lights up, visitors arrive, try a tester, ask what's inside, join the
waitlist and leave with a SPOT bag.
"""
import importlib.util
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import booth  # noqa: E402
import hand_test  # noqa: E402

_spec = importlib.util.spec_from_file_location("day03_render", os.path.join(REELS, "day03", "render.py"))
d3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d3)
kit = d3.kit

OUT = os.path.join(HERE, "out")
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = d3.XFADE, d3.LAST_XFADE
INK, CREAM, WHITE = kit.INK, kit.CREAM, kit.WHITE
GOLD = (176, 141, 87)
place, appear, ease_out, ease_io = kit.place, kit.appear, kit.ease_out, kit.ease_in_out
title, kicker, serif_layer = d3.title, d3.kicker, d3.serif_layer


def tag_layer(dark=False):
    col = INK if dark else WHITE
    a = kit.text_layer(["BEAUTY ASIA"], kit.F_SEMIBOLD, 52, col, tracking=10)
    b = kit.text_layer(["OUR BOOTH"], kit.F_MEDIUM, 28, GOLD, tracking=8)
    w = max(a.width, b.width)
    img = Image.new("RGBA", (w, a.height + b.height + 6), (0, 0, 0, 0))
    img.alpha_composite(a, ((w - a.width) // 2, 0))
    img.alpha_composite(b, ((w - b.width) // 2, a.height + 6))
    return img if dark else kit.with_shadow(img, 12, 0.6)


TAG, TAG_INK = tag_layer(), tag_layer(dark=True)

BASE_LIT, COUNTER = booth.draw_booth(1.0)
BASE_DARK, _ = booth.draw_booth(0.0)

# people
STAFF = {r: booth.person(470, color=(84, 78, 74), accent=(190, 154, 98), reach=r, facing=1) for r in (0.0, 0.35, 0.7, 1.0)}
STAFF_POS = (418, 925)


def staff(reach):
    k = min(STAFF, key=lambda r: abs(r - reach))
    return STAFF[k], STAFF_POS


def visitor(color, step, facing=-1, height=560):
    return booth.person(height, color=color, facing=facing, step=step)


V1_COL, V2_COL = (150, 140, 134), (118, 110, 106)
STEPS = {s: (visitor(V1_COL, s), visitor(V2_COL, s, height=530)) for s in (-0.5, 0.0, 0.5)}
STEPS_OUT = {s: (visitor(V1_COL, s, facing=1), visitor(V2_COL, s, facing=1, height=530)) for s in (-0.5, 0.0, 0.5)}


def walkers(t, x_from, x_to, t0, t1, out=False):
    """Two visitors walking between x positions; legs swing while moving."""
    k = ease_io((t - t0) / (t1 - t0))
    moving = t0 < t < t1
    s = (-0.5, 0.0, 0.5, 0.0)[int(t * 6) % 4] if moving else 0.0
    v1, v2 = (STEPS_OUT if out else STEPS)[s]
    x1 = x_from[0] + (x_to[0] - x_from[0]) * k
    x2 = x_from[1] + (x_to[1] - x_from[1]) * k
    bob = 6 * abs(math.sin(t * 9)) if moving else 0
    return [(v2, (x2, 1090 - bob)), (v1, (x1, 1060 - bob))]


def booth_frame(t, lights=1.0, behind=(), front=(), zoom=(1.0, 1.0), T=1.0):
    base = BASE_LIT if lights >= 1 else Image.blend(BASE_DARK, BASE_LIT, lights)
    fr = booth.compose(lights, base, COUNTER, behind=behind, front=front)
    z = zoom[0] + (zoom[1] - zoom[0]) * ease_io(t / T)
    if z != 1.0:
        cw, ch = W / z, H / z
        x0, y0 = (W - cw) / 2, (H - ch) * 0.55
        fr = fr.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    return fr


def pop_bubble(fr, bub, x, y, t, t0):
    if t < t0:
        return
    k = ease_out((t - t0) / 0.25)
    place(fr, bub, x + bub.width / 2, y + bub.height / 2, min(1, k * 1.4), rise=0, scale=0.85 + 0.15 * k)


# --------------------------------------------------------------------------- scenes

S1_H = title(["We had a booth", "at Beauty Asia."], 100)
LIGHTS_ON = (0.5, 1.4)


def s_reveal(t, T):
    l = ease_out((t - LIGHTS_ON[0]) / (LIGHTS_ON[1] - LIGHTS_ON[0]))
    fr = booth_frame(t, lights=max(0.0, l), behind=[staff(0.0)], zoom=(1.0, 1.06), T=T)
    place(fr, TAG, W / 2, 118, appear(t, 0.0, 0.35), rise=0)
    place(fr, S1_H, W / 2, 335, appear(t, 1.2, 0.6))
    return fr


C2_H = serif_layer(["We were too busy", "talking to film it."], 88, INK, weight=600)
C2_I = serif_layer(["So we drew it for you."], 72, GOLD, weight=500, italic=True)
RULE_G = Image.new("RGBA", (120, 2), GOLD + (255,))


def s_confess(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 210, 1, rise=0)
    place(fr, C2_H, W / 2, 840, appear(t, 0.15, 0.6))
    place(fr, RULE_G, W / 2, 990, appear(t, 0.9), rise=0)
    place(fr, C2_I, W / 2, 1080, appear(t, 1.1, 0.6))
    return fr


B_HI = booth.bubble(["Hi! Want to try it?"], 42)
S3_H = title(["Visitors came by."], 84)


def s_arrive(t, T):
    reach = 0.7 + 0.3 * math.sin(t * 7) if 1.6 < t < 2.8 else 0.0
    front = walkers(t, (1180, 1340), (640, 820), 0.0, 1.8)
    fr = booth_frame(t, behind=[staff(reach)], front=front)
    place(fr, TAG, W / 2, 118, 1, rise=0)
    place(fr, S3_H, W / 2, 320, appear(t, 0.2))
    pop_bubble(fr, B_HI, 250, 770, t, 2.0)
    return fr


B_Q = booth.bubble(["What's inside?"], 42, dark=True)
B_A = booth.bubble(["Let us explain", "every ingredient."], 42)
S5_H = title(["And asked the", "best questions."], 84)


def s_qa(t, T):
    reach = 0.35 if t > 1.6 else 0.0
    fr = booth_frame(t, behind=[staff(reach)], front=walkers(t, (640, 820), (640, 820), 0, 1))
    place(fr, TAG, W / 2, 118, 1, rise=0)
    place(fr, S5_H, W / 2, 335, appear(t, 0.15))
    pop_bubble(fr, B_Q, 600, 900, t, 0.5)
    pop_bubble(fr, B_A, 160, 760, t, 1.7)
    return fr


# waitlist close-up: tablet + phone scan
W_H = serif_layer(["They joined", "the waitlist."], 84, INK, weight=600)
W_OK = serif_layer(["You're on the list."], 56, INK, weight=500, italic=True)
SCAN0, SCAN1, OK_T = 0.9, 1.9, 2.1


def tablet_card():
    tw, th = 560, 760
    im = Image.new("RGBA", (tw + 80, th + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 40, 40 + tw, 40 + th], radius=46, fill=(28, 28, 28, 255))
    d.rounded_rectangle([64, 64, 16 + tw, 16 + th], radius=28, fill=(250, 246, 238, 255))
    lg = booth._logo(220)
    im.alpha_composite(lg, (40 + (tw - lg.width) // 2, 120))
    t1 = kit.text_layer(["JOIN THE WAITLIST"], kit.F_SEMIBOLD, 26, GOLD, tracking=6)
    im.alpha_composite(t1, (40 + (tw - t1.width) // 2, 230))
    q0, qs, n = 40 + (tw - 300) // 2, 300, 11
    cell = qs / n
    import random
    rnd = random.Random(8)
    for y in range(n):
        for x in range(n):
            corner = (x < 3 and y < 3) or (x > n - 4 and y < 3) or (x < 3 and y > n - 4)
            if corner:
                on = (x in (0, 2) or y in (0, 2) or (x == 1 and y == 1)) if (x < 3 and y < 3) else \
                     (x in (n - 3, n - 1) or y in (0, 2) or (x == n - 2 and y == 1)) if (y < 3) else \
                     (x in (0, 2) or y in (n - 3, n - 1) or (x == 1 and y == n - 2))
            else:
                on = rnd.random() < 0.5
            if on:
                d.rectangle([q0 + x * cell, 300 + y * cell, q0 + (x + 1) * cell - 2, 300 + (y + 1) * cell - 2], fill=INK + (255,))
    t2 = serif_layer(["Be first to know."], 44, INK, weight=500, italic=True)
    im.alpha_composite(t2, (40 + (tw - t2.width) // 2, 640))
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    sh.paste((60, 40, 30, 110), (40, 64), im.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    sh.alpha_composite(im, (40, 40))
    return sh


TABLET = tablet_card()


def phone(scan_k):
    pw, ph = 300, 600
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=44, fill=(20, 20, 20, 255))
    d.rounded_rectangle([14, 14, pw - 15, ph - 15], radius=34, fill=(46, 44, 42, 255))
    if scan_k > 0:
        y = 60 + (ph - 120) * scan_k
        d.line([(30, y), (pw - 30, y)], fill=GOLD + (255,), width=5)
    for cx, cy in ((40, 60), (pw - 40, 60), (40, ph - 60), (pw - 40, ph - 60)):
        sx = 1 if cx < pw / 2 else -1
        sy = 1 if cy < ph / 2 else -1
        d.line([(cx, cy), (cx + 40 * sx, cy)], fill=WHITE + (220,), width=5)
        d.line([(cx, cy), (cx, cy + 40 * sy)], fill=WHITE + (220,), width=5)
    return im


def check_badge(k):
    s = 3
    r = 70
    im = Image.new("RGBA", (r * 2 * s, r * 2 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, r * 2 * s - 1, r * 2 * s - 1], fill=GOLD + (255,))
    p = [(0.30, 0.52), (0.45, 0.66), (0.72, 0.36)]
    P = lambda x, y: (x * r * 2 * s, y * r * 2 * s)  # noqa: E731
    seg = k * 2
    e1 = min(1, seg)
    d.line([P(*p[0]), P(p[0][0] + (p[1][0] - p[0][0]) * e1, p[0][1] + (p[1][1] - p[0][1]) * e1)], fill=WHITE + (255,), width=12 * s)
    if seg > 1:
        e2 = seg - 1
        d.line([P(*p[1]), P(p[1][0] + (p[2][0] - p[1][0]) * e2, p[1][1] + (p[2][1] - p[1][1]) * e2)], fill=WHITE + (255,), width=12 * s)
    return im.resize((r * 2, r * 2), Image.LANCZOS)


def s_waitlist(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 210, 1, rise=0)
    place(fr, W_H, W / 2, 440, appear(t, 0.1))
    place(fr, TABLET, W / 2, 1120, appear(t, 0.0, 0.4), rise=30)
    # phone slides up over the QR, scans, then moves away
    k_in = ease_out((t - 0.4) / 0.5)
    k_out = ease_io((t - 2.6) / 0.6) if t > 2.6 else 0
    sk = min(1, max(0, (t - SCAN0) / (SCAN1 - SCAN0)))
    ph = phone(sk if SCAN0 <= t <= SCAN1 else 0)
    py = 1900 - (1900 - 1180) * k_in
    px = W / 2 + 120 + 900 * k_out          # slides off to the right after the scan
    if px < W + 300:
        fr.alpha_composite(ph, (int(px - ph.width / 2), int(py - ph.height / 2)))
    if t >= OK_T:
        k = ease_out((t - OK_T) / 0.35)
        place(fr, check_badge(min(1, (t - OK_T) / 0.4)), W / 2, 1640, min(1, k * 1.3), rise=0, scale=0.7 + 0.3 * k)
        place(fr, W_OK, W / 2, 1760, appear(t, OK_T + 0.2))
    return fr


# bag close-up
G_H = serif_layer(["And took a little", "SPOT home."], 84, INK, weight=600)


def bag_img():
    bw, bh = 520, 600
    im = Image.new("RGBA", (bw + 120, bh + 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = 60, 200
    for hx in (bw * 0.3, bw * 0.7):  # rope handles
        d.arc([ox + hx - 90, oy - 170, ox + hx + 90, oy + 40], 180, 360, fill=(150, 120, 80, 255), width=12)
    d.polygon([(ox, oy), (ox + bw, oy), (ox + bw - 20, oy + bh), (ox + 20, oy + bh)], fill=(240, 233, 222, 255))
    d.polygon([(ox, oy), (ox + bw, oy), (ox + bw - 8, oy + 40), (ox + 8, oy + 40)], fill=(226, 216, 202, 255))
    d.line([(ox + 30, oy + 60), (ox + bw - 30, oy + 60)], fill=GOLD + (255,), width=4)
    lg = booth._logo(300)
    im.alpha_composite(lg, (ox + (bw - lg.width) // 2, oy + 250))
    t1 = kit.text_layer(["SKINCARE  ·  COMING SOON"], kit.F_SEMIBOLD, 20, GOLD, tracking=5)
    im.alpha_composite(t1, (ox + (bw - t1.width) // 2, oy + 360))
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    sh.paste((60, 40, 30, 110), (40, 70), im.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    sh.alpha_composite(im, (40, 40))
    return sh


BAG = bag_img()


def s_bag(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    place(fr, TAG_INK, W / 2, 210, 1, rise=0)
    place(fr, G_H, W / 2, 440, appear(t, 0.1))
    k = ease_out((t - 0.3) / 0.8)
    sway = math.sin(t * 3.2) * 2.5 * (1 - min(1, t / 3))
    bag = BAG.rotate(sway, resample=Image.BICUBIC, expand=False)
    place(fr, bag, W / 2, 1150 + 300 * (1 - k), min(1, k * 1.3), rise=0)
    return fr


S8_H = title(["Thank you for", "stopping by."], 96)


def s_bye(t, T):
    reach = 0.7 + 0.3 * math.sin(t * 7) if t < 1.6 else 0.0
    front = walkers(t, (640, 820), (-300, -150), 0.4, 2.8, out=True)
    fr = booth_frame(t, behind=[staff(reach)], front=front, zoom=(1.05, 1.0), T=T)
    place(fr, TAG, W / 2, 118, 1, rise=0)
    place(fr, S8_H, W / 2, 335, appear(t, 0.2))
    return fr


E_THANKS = serif_layer(["Thank you, Beauty Asia."], 62, INK, weight=500, italic=True)


def s_end(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    k = appear(t, 0.1, 0.9)
    place(fr, kit.LOGO, W / 2, 690, k, rise=0, scale=0.94 + 0.06 * k)
    place(fr, E_THANKS, W / 2, 900, appear(t, 0.7))
    place(fr, d3.E_SOON, W / 2, 985, appear(t, 0.9))
    place(fr, kit.E_RULE, W / 2, 1080, appear(t, 1.2), rise=0)
    place(fr, d3.E_FOLLOW, W / 2, 1165, appear(t, 1.4))
    place(fr, kit.E_HANDLE, W / 2, 1240, appear(t, 1.6))
    return fr


HAND_FRAME, HAND_DUR, HAND_CUES = hand_test.build(kit, TAG)

SCENES = [
    dict(card=s_reveal, dur=4.5),
    dict(card=s_confess, dur=3.6),
    dict(card=s_arrive, dur=4.8),
    dict(card=HAND_FRAME, dur=HAND_DUR),
    dict(card=s_qa, dur=4.6),
    dict(card=s_waitlist, dur=4.4),
    dict(card=s_bag, dur=3.8),
    dict(card=s_bye, dur=3.6),
    dict(card=s_end, dur=4.5),
]
CUES = dict(lights=LIGHTS_ON, hi=2.0, q=0.5, a=1.7, scan=(SCAN0, SCAN1), ok=OK_T,
            hand_land=HAND_CUES["drop_land"], hand_rub=HAND_CUES["rub"])


# --------------------------------------------------------------------------- design board (still)

def design_board(path):
    fr = booth.compose(1.0, BASE_LIT, COUNTER)
    d = ImageDraw.Draw(fr)
    notes = [
        ((540, 760), (540, 400), "Backlit SPOT wall · “Skincare, explained.”"),
        ((90, 900), (90, 330), "Oak slat wall"),
        ((960, 980), (960, 330), "Brass shelves · unlabelled bottles + boxes"),
        ((420, 1140), (230, 1700), "Tester counter · gold edge"),
        ((665, 1080), (860, 1700), "Waitlist QR tablet"),
    ]
    for (px, py), (lx, ly), label in notes:
        d.line([(px, py), (lx, ly)], fill=GOLD + (255,), width=3)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=GOLD + (255,))
        lab = kit.text_layer([label.upper()], kit.F_SEMIBOLD, 22, WHITE, tracking=3)
        bg = Image.new("RGBA", (lab.width + 28, lab.height + 14), (20, 18, 17, 220))
        bg.alpha_composite(lab, (14, 7))
        x = min(max(10, lx - bg.width / 2), W - bg.width - 10)
        fr.alpha_composite(bg, (int(x), int(ly - bg.height / 2)))
    t = kit.text_layer(["SPOT BOOTH  ·  3 M × 3 M  ·  BEAUTY ASIA"], kit.F_SEMIBOLD, 30, GOLD, tracking=6)
    fr.alpha_composite(t, ((W - t.width) // 2, 1820))
    fr.convert("RGB").save(path, quality=95)


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
    for f in range(int(round(T * FPS))):
        enc.stdin.write(sc["card"](f / FPS, T).convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()


def main():
    _sspec = importlib.util.spec_from_file_location("booth_score", os.path.join(HERE, "score.py"))
    score = importlib.util.module_from_spec(_sspec)
    _sspec.loader.exec_module(score)

    os.makedirs(OUT, exist_ok=True)
    design_board(os.path.join(OUT, "spot_booth_design_board.jpg"))
    s_reveal(3.6, 4.5).convert("RGB").save(os.path.join(OUT, "spot_booth_cover.jpg"), quality=94)
    tmp = tempfile.mkdtemp(prefix="spot_booth_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        render_scene(sc, p)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_booth_music.wav"))
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
    for name, audio in [("spot_booth_reel.mp4", ["-i", score_path]),
                        ("spot_booth_reel_no_music.mp4",
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
