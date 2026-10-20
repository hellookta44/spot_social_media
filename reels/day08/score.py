"""Original score + sound design for the SPOT Day 8 Reel: the journey of one bottle (all synthesised).

Cinematic pulse in D minor → F (Dm – Bb – F – C) on the Day 2 engine: pad, sub,
soft kick, piano hook. Room tone of a quiet production floor runs underneath, and
every shot has its own foley: liquid pour, mixer motor + swirl, pipette drip and
glass clink, filling-nozzle hiss + conveyor ticks, cap screw clicks, label-feed
whirr, glass bottles touching, and a calm resolve with shimmer for the hero shot.
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
rng = np.random.default_rng(800)

s2.PROG[:] = [
    dict(bass=38, pad=[50, 53, 57, 62]),   # Dm
    dict(bass=46, pad=[50, 53, 58, 62]),   # Bb
    dict(bass=41, pad=[53, 57, 60, 65]),   # F
    dict(bass=48, pad=[52, 55, 60, 64]),   # C
]
HOOK = [69, None, 72, None, 74, 72, 69, None,   70, None, 69, None, 65, None, None, None]
s2.HOOK_B = [69, None, 72, None, 77, 76, 74, None,  72, None, 74, 72, 69, None, None, None]


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def bandnoise(n, centre, width=0.6):
    return m.spectral(rng.standard_normal(n), lambda f: np.exp(-((np.log(np.maximum(f, 1) / centre)) ** 2) / width))


def room_tone(dur):
    """Production floor: low air-handling rumble + a faint electrical hum."""
    t = _t(dur)
    rumble = bandnoise(len(t), 140, 1.2)
    hum = 0.25 * np.sin(2 * np.pi * 100 * t) + 0.12 * np.sin(2 * np.pi * 200 * t)
    return (rumble + hum * 0.4) * np.minimum(1, t / 0.6) * np.clip((dur - t) / 0.8, 0, 1)


def pour(dur):
    """Liquid stream into a beaker: bubbly band noise, rising in pitch as it fills."""
    t = _t(dur)
    x = bandnoise(len(t), 700, 0.5) + 0.6 * bandnoise(len(t), 1800, 0.4)
    gurgle = 0.6 + 0.4 * np.abs(m.lowpass(rng.standard_normal(len(t)), 25)) * 3
    bubbles = np.zeros(len(t))
    for tb in np.sort(rng.uniform(0.1, dur - 0.1, 22)):
        k = _t(0.05)
        f = rng.uniform(700, 1500) * (1 + 0.4 * tb / dur)
        b = np.sin(2 * np.pi * np.cumsum(f * (1 + 2 * k)) / SR) * np.exp(-k / 0.012)
        i = int(tb * SR)
        bubbles[i:i + len(k)] += b[: len(bubbles) - i]
    env = np.minimum(1, t / 0.15) * np.clip((dur - t) / 0.3, 0, 1)
    return (x * gurgle + 0.5 * bubbles) * env


def mixer(dur):
    t = _t(dur)
    f = 58 * (1 + 0.02 * np.sin(2 * np.pi * 0.7 * t))
    motor = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(3 * f) / SR)
    swirl = bandnoise(len(t), 500, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.6 * t))
    return (0.35 * motor + swirl) * np.minimum(1, t / 0.4) * np.clip((dur - t) / 0.4, 0, 1)


def hiss(dur=0.5):
    t = _t(dur)
    return m.highpass(rng.standard_normal(len(t)), 3500) * np.exp(-t / (dur / 3)) * np.minimum(1, t / 0.01)


def tick():
    t = _t(0.03)
    return m.highpass(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.003) + \
        0.5 * np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.006)


def cap_twist():
    out = np.zeros(int(0.5 * SR))
    for k in range(6):
        c = tick() * (0.5 + 0.1 * k)
        i = int((0.03 + 0.055 * k) * SR)
        out[i:i + len(c)] += c
    return out


def label_feed(dur):
    t = _t(dur)
    whirr = np.sin(2 * np.pi * np.cumsum(np.full(len(t), 220.0)) / SR) * 0.3 + bandnoise(len(t), 1600, 0.3)
    return whirr * np.minimum(1, t / 0.08) * np.clip((dur - t) / 0.12, 0, 1)


def compose(starts, total, cues, path):
    s_pour, s_mix, s_test, s_fill, s_cap, s_label, s_row, s_hero, s_end = starts
    tr = m.Track(total + 0.5)
    fx = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []

    fx.add(0.0, room_tone(s_end + 0.4), 0.10)

    # Pour: hushed intro, pad + piano, the stream up front.
    pads.add(0.0, m.pad(s2.PROG[0]["pad"], s_mix + 0.3, attack=0.5, bright=0.9), 0.24, verb=0.6)
    tr.add(0.2, s3.shimmer([74, 77, 81, 86]), 0.04, pan=0.2, verb=0.7)
    for j, n in enumerate([62, 65, 69, 74]):
        tr.add(0.4 + j * 0.5, m.epiano(n, 1.8, 0.6), 0.08, pan=-0.2 + 0.13 * j, verb=0.6)
    fx.add(0.1, pour(s_mix - 0.1), 0.22, pan=0.1, verb=0.2)
    tr.add(s_mix - 0.8, m.riser(0.8), 0.04, verb=0.4)

    # Mixing → hero: the pulse, hook from the filling line on.
    tr.add(s_mix, m.boom(1.4, 38), 0.18, verb=0.35)
    kicks += s2.groove(tr, pads, s_mix, s_fill, snaps=False, shake=True, hook=None, keys=True)
    kicks += s2.groove(tr, pads, s_fill, s_hero, snaps=True, shake=True, hook=HOOK, keys=False)
    for t in (s_mix, s_test, s_fill, s_cap, s_label, s_row):
        tr.add(t - 0.3, m.whoosh(0.45), 0.045, verb=0.25)
    fx.add(s_mix, mixer(s_test - s_mix + 0.2), 0.16, pan=-0.1, verb=0.15)
    fx.add(s_test + 0.9, s3.plip(), 0.14, pan=0.1, verb=0.3)
    fx.add(s_test + 1.3, s3.glass_clink(1.05), 0.05, pan=0.15, verb=0.4)
    for k in range(int((s_cap - s_fill) / 0.32)):
        fx.add(s_fill + 0.15 + k * 0.32, tick(), 0.10, pan=-0.3 + 0.08 * k, verb=0.1)
    fx.add(s_fill + 0.35, hiss(0.45), 0.08, pan=0.1, verb=0.2)
    fx.add(s_fill + 1.35, hiss(0.45), 0.07, pan=-0.1, verb=0.2)
    fx.add(s_cap + 0.4, cap_twist(), 0.20, pan=0.05, verb=0.15)
    fx.add(s_cap + 1.5, cap_twist(), 0.16, pan=-0.1, verb=0.15)
    fx.add(s_label + 0.3, label_feed(1.0), 0.07, pan=0.2, verb=0.15)
    fx.add(s_row + 0.4, s3.glass_clink(0.92), 0.05, pan=-0.2, verb=0.4)
    fx.add(s_row + 0.9, s3.glass_clink(1.0), 0.04, pan=0.2, verb=0.4)

    # Hero: drums out, warm pad, hook on the piano.
    tr.add(s_hero - 0.4, m.whoosh(0.6), 0.06, verb=0.4)
    s2.groove(tr, pads, s_hero, s_end, drums=False, snaps=False, shake=False, hook=HOOK, keys=False)
    tr.add(s_hero + 0.2, s3.shimmer([81, 84, 88, 93]), 0.04, verb=0.8)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.07, verb=0.4)

    # End card: Fmaj9 resolve + shimmer.
    tail = total - s_end
    pads.add(s_end, m.pad([53, 57, 60, 64, 67], tail - 0.6, attack=0.5, release=1.0, bright=1.2), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(41, tail), 0.12)
    for j, n in enumerate([65, 69, 72, 76, 79]):
        tr.add(s_end + 0.12 + j * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * j, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([84, 88, 91, 96]), 0.05, verb=0.8)

    # Mix: music bus sidechained to the kick, foley on top, shared room.
    n_all = tr.dry.shape[1]
    env = s2.sidechain(n_all, kicks)
    dry = tr.dry + pads.dry * env + fx.dry
    send = tr.send + pads.send * env + fx.send
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
