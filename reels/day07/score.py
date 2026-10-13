"""Original score + sound design for the SPOT Day 7 Reel (all synthesised).

A day from 6am to midnight: same production as Days 2/5 (sidechain pad, sub, kick,
snaps, shaker, piano hook + bell), progression G – D – Em – C, with a soft
clock-tick pulse on every eighth note. Each hour gets its own sound: alarm chime,
coffee pour, keyboard typing, phone buzz, lab glass clink, pen scratch, passing
car; the drums drop out for the night and resolve on the logo.
"""
import importlib.util
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("day02_score", os.path.join(HERE, "..", "day02", "score.py"))
s2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s2)
s3, m = s2.s3, s2.m
SR = m.SR
rng = np.random.default_rng(707)

s2.PROG[:] = [
    dict(bass=43, pad=[55, 59, 62, 67]),   # G
    dict(bass=38, pad=[54, 57, 62, 66]),   # D
    dict(bass=40, pad=[52, 55, 59, 64]),   # Em
    dict(bass=48, pad=[52, 55, 60, 64]),   # C
]
HOOK = [71, None, 74, None, 76, 74, 71, None,   69, None, 71, None, 67, None, None, None]
s2.HOOK_B = [71, None, 74, None, 79, 76, 74, None,  76, None, 74, 71, 72, None, None, None]


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def clock_tick(high=True):
    t = _t(0.05)
    f = 3400 if high else 2600
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.004) + 0.3 * m.highpass(rng.standard_normal(len(t)), 5000) * np.exp(-t / 0.003)


def alarm_chime():
    out = np.zeros(int(1.6 * SR))
    for k, n in enumerate([79, 83, 86, 91]):
        b = m.bell(n, 1.2)
        i = int(k * 0.11 * SR)
        out[i:i + len(b)] += b[: len(out) - i] * 0.8
    return out


def pour(dur=1.6):
    t = _t(dur)
    x = m.spectral(rng.standard_normal(len(t)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 900)) ** 2) / 0.6))
    gurgle = 1 + 0.6 * np.sin(2 * np.pi * (9 + 5 * t) * t)
    return x * gurgle * np.minimum(1, t / 0.1) * np.clip((dur - t) / 0.3, 0, 1)


def typing(dur=2.0):
    out = np.zeros(int(dur * SR))
    t = 0.0
    while t < dur - 0.05:
        k = _t(0.03)
        click = m.spectral(rng.standard_normal(len(k)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 2800)) ** 2) / 0.3))
        i = int(t * SR)
        out[i:i + len(k)] += click * np.exp(-k / 0.005) * rng.uniform(0.5, 1.0)
        t += rng.uniform(0.06, 0.16)
    return out


def phone_buzz():
    t = _t(0.9)
    gate = ((t % 0.45) < 0.3).astype(float)
    return np.sin(2 * np.pi * 150 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * gate * np.minimum(1, t / 0.02)


def pen_scratch(dur=1.2):
    t = _t(dur)
    x = m.spectral(rng.standard_normal(len(t)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 3500)) ** 2) / 0.5))
    strokes = np.clip(np.sin(2 * np.pi * 3.2 * t), 0, 1) ** 2
    return x * strokes * np.clip((dur - t) / 0.2, 0, 1)


def car_pass(dur=1.8):
    t = _t(dur)
    x = m.lowpass(rng.standard_normal(len(t)), 900)
    return x * np.exp(-((t - dur / 2) / (dur / 4)) ** 2)


def compose(starts, total, cues, path):
    *hours, s_end = starts
    tr = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []
    BAR = s2.BAR

    # 6:00 — alarm chime, soft pad, ticking clock begins.
    pads.add(0.0, m.pad(s2.PROG[0]["pad"], hours[1] + 0.3, attack=0.4, bright=0.9), 0.24, verb=0.6)
    tr.add(0.15, alarm_chime(), 0.10, pan=0.2, verb=0.6)
    # Clock pulse under the whole day (until midnight).
    t = 0.0
    k = 0
    while t < s_end - 0.2:
        tr.add(t, clock_tick(k % 2 == 0), 0.045 if k % 2 == 0 else 0.03, pan=0.3, verb=0.1)
        t += s2.BEAT / 2
        k += 1

    # 7:30 → 7:00 PM — full groove with the hook from 9:00.
    kicks += s2.groove(tr, pads, hours[1], hours[2], hook=None)
    kicks += s2.groove(tr, pads, hours[2], hours[7], hook=HOOK)

    # Hour sounds + a whoosh and a quick clock "whirr" on every cut.
    for i, h in enumerate(hours[1:], start=1):
        tr.add(h - 0.3, m.whoosh(0.45), 0.05, verb=0.2)
        for j in range(5):
            tr.add(h + j * 0.09, clock_tick(True), 0.05, pan=-0.2, verb=0.15)
    tr.add(hours[1] + 0.3, pour(), 0.12, pan=-0.15, verb=0.2)
    tr.add(hours[2] + 0.2, typing(2.0), 0.10, pan=0.2, verb=0.15)
    tr.add(hours[3] + 0.3, phone_buzz(), 0.12, verb=0.15)
    tr.add(hours[4] + 0.6, s3.glass_clink(1.0), 0.06, pan=-0.2, verb=0.5)
    tr.add(hours[4] + 1.0, s3.plip(), 0.10, verb=0.4)
    tr.add(hours[5] + 0.3, pen_scratch(), 0.08, pan=0.2, verb=0.2)
    tr.add(hours[6] + 0.2, car_pass(), 0.20, pan=0.0, verb=0.3)

    # 11 PM → midnight: drums out, hook on piano alone, then a hush before the logo.
    s2.groove(tr, pads, hours[7], s_end, drums=False, snaps=False, shake=False, hook=HOOK, keys=False)
    tr.add(hours[8] + 0.3, m.bell(91, 2.6), 0.06, verb=0.8)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.08, verb=0.4)

    # End card: Gmaj9 resolve + shimmer.
    tail = total - s_end
    pads.add(s_end, m.pad([55, 59, 62, 66, 69], tail - 0.6, attack=0.5, release=1.0, bright=1.3), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(43, tail), 0.14)
    for j, n in enumerate([67, 71, 74, 78, 81]):
        tr.add(s_end + 0.12 + j * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * j, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([86, 90, 93, 98]), 0.05, verb=0.8)

    # Mix (same chain as Days 2 and 5).
    n_all = tr.dry.shape[1]
    env = s2.sidechain(n_all, kicks)
    dry = tr.dry + pads.dry * env
    send = tr.send + pads.send * env
    wet = np.stack([m.reverb(send[0], seed=11), m.reverb(send[1], seed=23)])
    mix = dry + 0.5 * wet
    mix = np.stack([m.highpass(mix[0], 40), m.highpass(mix[1], 40)])
    n = int(total * SR)
    mix = mix[:, :n]
    mix *= 10 ** (-16.5 / 20) / np.sqrt(np.mean(mix ** 2))
    mix = np.tanh(mix * 1.15) / np.tanh(1.15)
    mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    t = np.arange(n) / SR
    mix *= np.minimum(1, t / 0.03)
    mix *= np.clip((total - t) / 1.6, 0, 1) ** 1.5
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix.T * 32767).astype("<i2").tobytes())
    return path
