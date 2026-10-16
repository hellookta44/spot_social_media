"""Booth tester close-up (from the Day 2 v1 animation): a dropper releases a drop onto
the back of a hand, then a fingertip gently rubs it in until it absorbs.

All drawn procedurally (no stock footage). build(kit, tag) returns
(frame_fn, duration, cues) for render.py.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
SKIN_TOP = np.array([238, 203, 176])
SKIN_BOT = np.array([220, 172, 142])

# Timeline (seconds)
DUR = 4.6
T_IN, T_HOLD = 0.0, 0.55          # dropper slides in
T_SWELL = 1.05                    # drop swells at the tip until here
T_LAND = 1.32                     # drop hits the skin
T_OUT = 1.45                      # dropper lifts away from here
T_FINGER_IN, T_RUB0 = 1.75, 2.1   # fingertip arrives
T_RUB1 = 3.75                     # end of rubbing
T_FINGER_OUT = 3.95

TIP = (W * 0.68, 940)             # dropper tip when lowered
LAND = (W * 0.68, 1160)           # where the drop lands


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 3 * t * t - 2 * t * t * t


# --------------------------------------------------------------------------- hand skin

def hand_skin():
    """Close-up of the back of a hand: warm gradient, pores, fine creases, soft light."""
    rng = np.random.default_rng(5)
    y = np.linspace(0, 1, H)[:, None, None]
    img = np.repeat(SKIN_TOP * (1 - y) + SKIN_BOT * y, W, axis=1).astype(float)

    def noise(scale, blur, amp):
        n = rng.standard_normal((H // scale + 1, W // scale + 1)) * 40 + 128
        n = Image.fromarray(n.clip(0, 255).astype("uint8")).resize((W, H), Image.BICUBIC)
        return (np.array(n.filter(ImageFilter.GaussianBlur(blur)), float) - 128) / 128 * amp

    img += (noise(2, 1.2, 6) + noise(40, 30, 10))[..., None]           # pores + blotchiness
    # Fine diagonal skin creases.
    lines = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lines)
    for _ in range(140):
        x0, y0 = rng.uniform(-200, W), rng.uniform(0, H)
        ln = rng.uniform(40, 140)
        a = math.radians(rng.normal(-28, 10))
        d.line([(x0, y0), (x0 + ln * math.cos(a), y0 + ln * math.sin(a))], fill=int(rng.uniform(30, 70)), width=2)
    for k in range(3):  # a few knuckle-style curved folds near the top
        cx, cy = 260 + 300 * k, 260 + 40 * k
        d.arc([cx - 220, cy - 60, cx + 220, cy + 60], 200, 340, fill=90, width=3)
    creases = np.array(lines.filter(ImageFilter.GaussianBlur(1.6)), float) / 255
    img *= (1 - 0.10 * creases)[..., None]
    # Soft window light from top-left + vignette.
    yy, xx = np.mgrid[0:H, 0:W]
    light = np.exp(-(((xx - W * 0.25) / (W * 0.9)) ** 2 + ((yy - H * 0.25) / (H * 0.7)) ** 2))
    img *= (0.86 + 0.2 * light)[..., None]
    vig = ((xx - W / 2) / W) ** 2 + ((yy - H * 0.55) / H) ** 2
    img *= (1 - 0.6 * vig)[..., None]
    return Image.fromarray(img.clip(0, 255).astype("uint8")).convert("RGBA")


# --------------------------------------------------------------------------- dropper

def dropper():
    """Frosted glass pipette with gold collar and white bulb; tip at bottom centre."""
    s = 2
    bw, bh = 128, 230          # bulb
    cw, ch = 158, 120          # collar
    tw, th = 70, 400           # glass tube
    taper = 90
    w = cw + 40
    h = bh + ch + th + taper
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * s / 2
    # Bulb (white rubber) with soft shading.
    d.rounded_rectangle([cx - bw * s / 2, 0, cx + bw * s / 2, (bh + 40) * s], radius=bw * s // 2, fill=(246, 244, 240, 255))
    shade = Image.new("L", img.size, 0)
    ImageDraw.Draw(shade).rounded_rectangle([cx + bw * s * 0.12, 20 * s, cx + bw * s / 2, (bh + 30) * s],
                                            radius=bw * s // 3, fill=60)
    img.paste((150, 145, 140, 255), (0, 0), Image.composite(shade.filter(ImageFilter.GaussianBlur(14 * s)),
                                                            Image.new("L", img.size, 0), img.split()[3]))
    # Gold collar with horizontal metallic banding.
    y0 = bh * s
    col = np.zeros((ch * s, cw * s, 4), np.uint8)
    xs = np.linspace(-1, 1, cw * s)
    band = 0.55 + 0.45 * np.cos(xs * 2.6) + 0.25 * np.exp(-((xs + 0.45) / 0.12) ** 2)
    gold = np.array([196, 150, 62])
    col[..., :3] = (gold[None, None, :] * band[None, :, None]).clip(0, 255)
    col[..., 3] = 255
    for r in range(0, ch * s, 14 * s):  # ridges
        col[r:r + 2 * s, :, :3] = (col[r:r + 2 * s, :, :3] * 0.75).astype(np.uint8)
    img.paste(Image.fromarray(col), (int(cx - cw * s / 2), y0))
    # Glass tube: translucent body, product fill, edges, highlight; tapers to the tip.
    gy0 = (bh + ch) * s
    glass = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glass)
    poly = [(cx - tw * s / 2, gy0), (cx + tw * s / 2, gy0), (cx + tw * s / 2, gy0 + th * s),
            (cx + 9 * s, (bh + ch + th + taper) * s), (cx - 9 * s, (bh + ch + th + taper) * s),
            (cx - tw * s / 2, gy0 + th * s)]
    g.polygon(poly, fill=(255, 255, 255, 105))
    fill_top = gy0 + th * s * 0.45
    g.polygon([(cx - tw * s / 2 + 6 * s, fill_top), (cx + tw * s / 2 - 6 * s, fill_top),
               (cx + tw * s / 2 - 6 * s, gy0 + th * s), (cx + 6 * s, (bh + ch + th + taper - 4) * s),
               (cx - 6 * s, (bh + ch + th + taper - 4) * s), (cx - tw * s / 2 + 6 * s, gy0 + th * s)],
              fill=(255, 252, 246, 140))
    g.line(poly + [poly[0]], fill=(255, 255, 255, 215), width=4 * s)
    g.line([(cx - tw * s * 0.22, gy0 + 20 * s), (cx - tw * s * 0.22, gy0 + th * s - 20 * s)],
           fill=(255, 255, 255, 200), width=5 * s)
    img.alpha_composite(glass.filter(ImageFilter.GaussianBlur(0.6 * s)))
    img = img.resize((w, h), Image.LANCZOS)
    # Drop shadow on the skin, cast down-right.
    sh = Image.new("RGBA", (w + 120, h + 120), (0, 0, 0, 0))
    sh.paste((90, 50, 35, 70), (70, 90), img.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    return img, sh


# --------------------------------------------------------------------------- product

def droplet(r, alpha=1.0, stretch=1.0):
    """Glossy translucent drop of radius r (stretch > 1 elongates it vertically)."""
    w, h = int(2 * r + 40), int(2 * r * stretch + 40)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([20, 20, 20 + 2 * r, 20 + 2 * r * stretch], fill=int(165 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (w, h), v) for v in (252, 249, 244)]
                                    + [m.filter(ImageFilter.GaussianBlur(1.5))]))
    hl = Image.new("L", (w, h), 0)
    ImageDraw.Draw(hl).ellipse([20 + r * 0.45, 20 + r * 0.35 * stretch, 20 + r * 0.95, 20 + r * 0.85 * stretch],
                               fill=int(240 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (w, h), 255)] * 3 + [hl.filter(ImageFilter.GaussianBlur(2.5))]))
    return img


def puddle(w, h, alpha, sheen=1.0):
    """Product on skin: soft translucent body, rim shadow, specular glints."""
    pad = 60
    W2, H2 = int(w) + 2 * pad, int(h) + 2 * pad
    img = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    box = [pad, pad, pad + w, pad + h]
    sh = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(sh).ellipse([box[0] + 5, box[1] + 10, box[2] + 5, box[3] + 10], fill=int(70 * alpha))
    img.paste((120, 70, 50, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    body = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(body).ellipse(box, fill=int(135 * alpha))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (W2, H2), v) for v in (252, 248, 242)]
                                    + [body.filter(ImageFilter.GaussianBlur(4 + 10 * (1 - sheen)))]))
    hl = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(hl).ellipse([box[0] + w * 0.2, box[1] + h * 0.15, box[0] + w * 0.48, box[1] + h * 0.36],
                               fill=int(235 * alpha * sheen))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (W2, H2), 255)] * 3 + [hl.filter(ImageFilter.GaussianBlur(5))]))
    return img


def glow(w, h, alpha):
    """Thin dewy sheen left after rubbing in."""
    pad = 80
    W2, H2 = int(w) + 2 * pad, int(h) + 2 * pad
    m = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(m).ellipse([pad, pad, pad + w, pad + h], fill=int(55 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(28))
    return Image.merge("RGBA", [Image.new("L", (W2, H2), 255)] * 3 + [m])


# --------------------------------------------------------------------------- fingertip

def finger():
    """Index fingertip seen from above, pointing right (tip at the right end)."""
    L, Wd = 900, 190
    s = 2
    img = Image.new("RGBA", (L * s, Wd * s), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, L * s, Wd * s], radius=Wd * s // 2, fill=255)
    # Skin with cylindrical shading across the width.
    ys = np.linspace(-1, 1, Wd * s)[:, None]
    shade = 0.78 + 0.26 * np.sqrt(np.clip(1 - ys ** 2, 0, 1)) - 0.06 * ys
    base = np.array([226, 170, 140])
    arr = np.zeros((Wd * s, L * s, 4), np.uint8)
    arr[..., :3] = (base * shade[..., None]).clip(0, 255)
    arr[..., 3] = np.array(m)
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    # Nail near the tip.
    nx0, nx1 = (L - 250) * s, (L - 28) * s
    d.rounded_rectangle([nx0, 42 * s, nx1, (Wd - 42) * s], radius=60 * s, fill=(240, 205, 196, 255))
    d.rounded_rectangle([nx1 - 46 * s, 46 * s, nx1, (Wd - 46) * s], radius=40 * s, fill=(250, 238, 232, 255))
    d.line([(nx0 + 30 * s, 70 * s), (nx1 - 70 * s, 64 * s)], fill=(255, 250, 248, 200), width=10 * s)
    # Knuckle crease lines further back.
    for xk in (L - 420, L - 445):
        d.arc([xk * s, 30 * s, (xk + 60) * s, (Wd - 30) * s], 120, 240, fill=(185, 130, 105, 200), width=4 * s)
    img = img.filter(ImageFilter.GaussianBlur(1.2 * s)).resize((L, Wd), Image.LANCZOS)
    return img


def rotated_finger(angle_deg):
    f = finger()
    sh = Image.new("RGBA", (f.width + 160, f.height + 160), (0, 0, 0, 0))
    sh.paste((80, 45, 30, 90), (100, 120), f.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    canvas = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(f, (80, 80))
    rot = canvas.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    # Where the fingertip (centre of the rounded end) lands after rotation.
    tx, ty = 80 + f.width - f.height / 2, 80 + f.height / 2
    cx, cy = canvas.width / 2, canvas.height / 2
    a = math.radians(angle_deg)
    rx = cx + (tx - cx) * math.cos(a) + (ty - cy) * math.sin(a)
    ry = cy - (tx - cx) * math.sin(a) + (ty - cy) * math.cos(a)
    return rot, (rx + (rot.width - canvas.width) / 2, ry + (rot.height - canvas.height) / 2)


# --------------------------------------------------------------------------- scene

def build(kit, tag):
    skin = hand_skin()
    drp, drp_shadow = dropper()
    fing, fing_tip = rotated_finger(-125)  # enters from the bottom-right, pointing up-left
    bot_grad = kit.gradient(0.6, 900, bottom=True)
    head = kit.headline(["They tried it", "on their skin."], 80)
    sub = kit.sub(["No pressure.", "Just the texture."], 44)

    def frame(t, T):
        fr = skin.copy()

        # Product on skin (drawn under the dropper and finger).
        if t >= T_LAND:
            spread = ease((t - T_LAND) / 0.4)
            w, h, alpha, sheen = 70 + 170 * spread, 44 + 92 * spread, 1.0, 1.0
            cx, cy = LAND
            if t >= T_RUB0:
                k = ease_io((t - T_RUB0) / (T_RUB1 - T_RUB0))
                w, h = 240 + 260 * k, 136 + 150 * k
                alpha, sheen = 1 - 0.8 * k, 1 - 0.7 * k
                g = glow(w * 1.1, h * 1.1, min(1, k * 1.5))
                fr.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
            if t >= T_RUB1:
                fade = ease((t - T_RUB1) / 0.6)
                alpha *= 1 - fade
                g = glow(560, 330, 1 - 0.55 * fade)
                fr.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
            if alpha > 0.02:
                p = puddle(w, h, alpha, sheen)
                fr.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))

        # Dropper: slide in, hold, lift out.
        if t < T_OUT + 0.6:
            if t < T_HOLD:
                off = -900 * (1 - ease((t - T_IN) / (T_HOLD - T_IN)))
            elif t < T_OUT:
                off = 0
            else:
                off = -1000 * ease_io((t - T_OUT) / 0.6)
            x = int(TIP[0] - drp.width / 2)
            y = int(TIP[1] - drp.height + off)
            fr.alpha_composite(drp_shadow, (x + 10, y - 30))
            fr.alpha_composite(drp, (x, y))
            # Drop swelling at the tip.
            if T_HOLD <= t < T_SWELL:
                r = 6 + 18 * ease((t - T_HOLD) / (T_SWELL - T_HOLD))
                dl = droplet(r, stretch=1.1)
                fr.alpha_composite(dl, (int(TIP[0] - dl.width / 2), int(TIP[1] + off - 26)))

        # Falling drop.
        if T_SWELL <= t < T_LAND:
            k = ((t - T_SWELL) / (T_LAND - T_SWELL)) ** 2
            dl = droplet(24, stretch=1.25)
            y = TIP[1] + (LAND[1] - TIP[1]) * k
            fr.alpha_composite(dl, (int(TIP[0] - dl.width / 2), int(y - dl.height / 2)))

        # Fingertip: arrive, rub in small circles, leave.
        if T_FINGER_IN <= t < T_FINGER_OUT + 0.45:
            far = (LAND[0] + 520, LAND[1] + 760)
            if t < T_RUB0:
                k = ease((t - T_FINGER_IN) / (T_RUB0 - T_FINGER_IN))
                px, py = far[0] + (LAND[0] - far[0]) * k, far[1] + (LAND[1] - far[1]) * k
            elif t < T_RUB1:
                ph = (t - T_RUB0) / (T_RUB1 - T_RUB0) * 2 * math.pi * 3  # three gentle circles
                rad = 55 + 35 * math.sin(ph / 6)
                px, py = LAND[0] + rad * math.cos(ph), LAND[1] + rad * 0.6 * math.sin(ph)
            else:
                k = ease_io((t - T_RUB1) / (T_FINGER_OUT + 0.45 - T_RUB1))
                px, py = LAND[0] + (far[0] - LAND[0]) * k, LAND[1] + (far[1] - LAND[1]) * k
            fr.alpha_composite(fing, (int(px - fing_tip[0]), int(py - fing_tip[1])))

        fr.alpha_composite(kit.TOP_GRAD)
        fr.alpha_composite(bot_grad)
        kit.place(fr, tag, W / 2, 215, 1, rise=0)
        kit.place(fr, head, W / 2, 1400, kit.appear(t, 0.2))
        kit.place(fr, sub, W / 2, 1540, kit.appear(t, 2.0))
        return fr

    cues = dict(drop_land=T_LAND, rub=(T_RUB0, T_RUB1))
    return frame, DUR, cues
