#!/usr/bin/env python3
"""Render the SPOT "Day 3" Instagram Reel: the final cut — unboxing + skin testing.

Usage:  python3 reels/day03/render.py
Output: reels/day03/out/spot_day03_reel.mp4 (+ _no_music, music .wav, cover .jpg)

Typography: Cormorant Garamond SemiBold (brand/fonts, OFL) for headlines, Inter for labels.
Product labels and the shipping box are never shown readable: shots are picked
around them and the bottle lineup has tracked blur boxes.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "day01"))
import render as kit  # noqa: E402

FOOTAGE = os.path.join(HERE, "footage")
OUT = os.path.join(HERE, "out")
FONTS = os.path.join(HERE, "..", "..", "brand", "fonts")
W, H, FPS = kit.W, kit.H, kit.FPS
XFADE, LAST_XFADE = 0.22, 0.45
INK, CREAM, WHITE = kit.INK, kit.CREAM, kit.WHITE
place, appear = kit.place, kit.appear
SRC_SCALE = W / 576  # all phone clips are 576x1024 portrait

TAG = kit.make_tag("03")


# --------------------------------------------------------------------------- typography

def serif(size, weight=500, italic=False):
    path = os.path.join(FONTS, "CormorantGaramond-Italic[wght].ttf" if italic else "CormorantGaramond[wght].ttf")
    f = ImageFont.truetype(path, size)
    f.set_variation_by_axes([weight])
    return f


def serif_layer(lines, size, color=WHITE, weight=600, italic=False, line_gap=1.08, align="center"):
    """Cormorant text with lining (modern) figures, so "15" never reads as "I5"."""
    f = serif(size, weight, italic)
    feats = ["lnum"]
    widths = [f.getlength(ln, features=feats) for ln in lines]
    lh = int(size * line_gap)
    img = Image.new("RGBA", (int(max(widths)) + 10, lh * len(lines) + int(size * 0.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = (img.width - widths[i]) / 2 if align == "center" else 0
        d.text((x, i * lh), ln, font=f, fill=color, features=feats)
    return img


def title(lines, size=104, italic=False):
    """Main headline: Cormorant Garamond SemiBold, white, soft shadow."""
    return kit.with_shadow(serif_layer(lines, size, italic=italic), 16, 0.6)


def kicker(lines, size=40):
    """Supporting line: Inter Medium, slightly warm white."""
    return kit.with_shadow(kit.text_layer(lines, kit.F_MEDIUM, size, (244, 240, 234), line_gap=1.32), 10, 0.55)


def rule(width=90):
    return kit.with_shadow(Image.new("RGBA", (width, 3), WHITE + (235,)), 6, 0.4)


RULE = rule()


# --------------------------------------------------------------------------- footage

GRADE = "eq=contrast=1.07:saturation=0.95:brightness=0.005,colorbalance=rs=0.025:gs=0.008:bs=-0.025"


def footage_frames(name, start, dur, speed=1.0, blur=None, footage_dir=FOOTAGE):
    """Yield graded 1080x1920 frames. speed < 1 = slow motion. blur = tracked boxes."""
    src = os.path.join(footage_dir, name)
    n = int(round(dur * FPS))
    src_len = dur * speed + 0.5
    vf = (f"setpts={1 / speed:.4f}*PTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:"
          f"flags=lanczos,crop={W}:{H},{GRADE}")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-t", f"{src_len:.3f}", "-i", src,
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = W * H * 3
    last = None
    for i in range(n):
        buf = p.stdout.read(size)
        if len(buf) == size:
            last = Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1).copy()
        img = last.copy()
        if blur:
            apply_blur(img, blur, start + i / FPS * speed)
        yield img
    p.stdout.close()
    p.wait()


def _lerp_track(track, t):
    """track: [(src_time, cx, cy), ...] in source pixels; linear interpolation."""
    if t <= track[0][0]:
        return track[0][1:]
    for (t0, x0, y0), (t1, x1, y1) in zip(track, track[1:]):
        if t <= t1:
            k = (t - t0) / (t1 - t0)
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    return track[-1][1:]


def apply_blur(img, boxes, t):
    for track, (bw, bh) in boxes:
        cx, cy = _lerp_track(track, t)
        x0 = int((cx - bw / 2) * SRC_SCALE)
        y0 = int((cy - bh / 2) * SRC_SCALE)
        x1, y1 = int(x0 + bw * SRC_SCALE), int(y0 + bh * SRC_SCALE)
        region = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(22))
        mask = Image.new("L", region.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([8, 8, region.width - 8, region.height - 8], radius=30, fill=255)
        img.paste(region, (x0, y0), mask.filter(ImageFilter.GaussianBlur(8)))


# Bottle lineup (unboxing.mp4 ~101–111 s): collar label on the frosted bottle + label on the pink bottle.
LINEUP_BLUR = [
    ([(101, 195, 395), (104, 169, 395), (107, 178, 390), (110, 212, 388)], (110, 170)),
    ([(101, 350, 340), (104, 324, 310), (107, 343, 310), (110, 367, 295)], (110, 185)),
]


# --------------------------------------------------------------------------- scenes

H1 = title(["The final cut."], 128)
H1_K = kicker(["Round two begins."], 44)


def s_hook(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, appear(t, 0.0, 0.35), rise=0)
    place(fr, H1, W / 2, 470, appear(t, 0.2, 0.6), rise=30)
    place(fr, RULE, W / 2, 580, appear(t, 0.7), rise=0)
    place(fr, H1_K, W / 2, 650, appear(t, 0.9))


H2 = title(["The shortlist", "just arrived."], 100)
H2_K = kicker(["Sealed. Wrapped. Ready for testing."], 40)


def s_unbox(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H2, W / 2, 500, appear(t, 0.15))
    place(fr, H2_K, W / 2, 690, appear(t, 1.2))


H3 = title(["Every formula", "gets tested again."], 96)


def s_lineup(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H3, W / 2, 500, appear(t, 0.15))


H4 = title(["On our own skin,"], 104)
H4_I = kit.with_shadow(serif_layer(["first."], 104, italic=True, weight=400), 16, 0.6)


def s_drop(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H4, W / 2, 450, appear(t, 0.15))
    place(fr, H4_I, W / 2, 560, appear(t, 0.8))


H5_ITEMS = ["Texture", "Absorption", "Feel"]
H5_LAYERS = [kit.with_shadow(serif_layer([w], 88), 14, 0.6) for w in H5_ITEMS]


def s_rub(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    for i, lay in enumerate(H5_LAYERS):  # words land one by one
        place(fr, lay, W / 2, 420 + i * 128, appear(t, 0.2 + i * 0.6), rise=25)


H6 = title(["Only the best", "make the final cut."], 96)
H6_K = kicker(["Which one makes it? Find out tomorrow."], 40)


def s_close(fr, t, T):
    fr.alpha_composite(kit.TOP_GRAD)
    place(fr, TAG, W / 2, 215, 1, rise=0)
    place(fr, H6, W / 2, 500, appear(t, 0.15))
    place(fr, H6_K, W / 2, 690, appear(t, 1.1))


E_NEXT = serif_layer(["Day 4: on the road to the factory."], 58, INK, weight=500, italic=True)
E_SOON = kit.text_layer(["SKINCARE PRODUCTS  ·  COMING SOON"], kit.F_MEDIUM, 28, (120, 112, 104), tracking=6)
E_FOLLOW = serif_layer(["Follow the journey"], 46, INK, weight=500)


def s_end(t, T):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    k = appear(t, 0.1, 0.9)
    place(fr, kit.LOGO, W / 2, 690, k, rise=0, scale=0.94 + 0.06 * k)
    place(fr, E_NEXT, W / 2, 900, appear(t, 0.7))
    place(fr, E_SOON, W / 2, 985, appear(t, 0.9))
    place(fr, kit.E_RULE, W / 2, 1080, appear(t, 1.2), rise=0)
    place(fr, E_FOLLOW, W / 2, 1165, appear(t, 1.4))
    place(fr, kit.E_HANDLE, W / 2, 1240, appear(t, 1.6))
    return fr


# (clip, start, dur, speed, blur) per shot; scene durations are output seconds.
SCENES = [
    dict(shots=[("pipette_macro.mp4", 1.6, 3.2, 0.7, None)], overlay=s_hook, zoom=(1.0, 1.06)),
    dict(shots=[("unboxing.mp4", 48.9, 1.6, 1.0, None),   # flaps open (box branding out of shot)
                ("unboxing.mp4", 50.6, 1.5, 1.0, None),
                ("unboxing.mp4", 66.0, 1.9, 1.0, None)], overlay=s_unbox, zoom=(1.04, 1.1)),
    dict(shots=[("unboxing.mp4", 104.5, 3.4, 0.85, LINEUP_BLUR)], overlay=s_lineup, zoom=(1.0, 1.05)),
    dict(shots=[("founder_skin_test.mp4", 19.6, 3.8, 0.9, None)], overlay=s_drop, zoom=(1.0, 1.05)),
    dict(shots=[("founder_skin_test.mp4", 36.2, 3.6, 1.0, None)], overlay=s_rub, zoom=(1.05, 1.1)),
    dict(shots=[("pipette_macro.mp4", 26.0, 3.4, 0.75, None)], overlay=s_close, zoom=(1.0, 1.05)),
    dict(card=s_end, dur=4.2),
]

# Sound-design cue points (seconds inside each scene).
CUES = dict(
    unbox_cuts=[0.0, 1.6, 3.1],  # flaps / bubble wrap / bottle reveal
    rub_words=[0.2, 0.8, 1.4],
)


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
        frames = (None for _ in range(int(round(T * FPS))))
    else:
        frames = (img for clip, st, d, sp, bl in sc["shots"] for img in footage_frames(clip, st, d, sp, bl))
    for f, img in enumerate(frames):
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
    import score

    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="spot_day03_")
    parts = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(tmp, f"scene{i}.mp4")
        cover = os.path.join(OUT, "spot_day03_cover.jpg") if i == 0 else None
        render_scene(sc, p, cover, cover_t=2.6)
        parts.append(p)
        print(f"scene {i + 1}/{len(SCENES)} rendered ({scene_dur(sc):.1f}s)")

    starts, total = scene_timing()
    score_path = score.compose(starts, total, CUES, os.path.join(OUT, "spot_day03_music.wav"))
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
    for name, audio in [("spot_day03_reel.mp4", ["-i", score_path]),
                        ("spot_day03_reel_no_music.mp4",
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
