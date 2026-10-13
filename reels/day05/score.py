"""Original score + sound design for the SPOT Day 5 Reel (all synthesised).

Same production as Day 2 v2 (sidechain-pumped pad, sub, kick, snaps, shaker,
piano hook doubled by bell) with a new progression and melody:
Dm – Bb – F – C, 96 BPM.

SFX: drop plip + shimmer on the hook, car-door thud on the arrival, a camera
shutter on each factory photo, pipette plips, a soft swish on the application,
glass clinks and node ticks as the molecule draws, riser + impact on the closing
line, shimmer on the logo.
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
rng = np.random.default_rng(505)

s2.PROG[:] = [
    dict(bass=38, pad=[50, 57, 62, 65]),   # Dm
    dict(bass=46, pad=[50, 53, 58, 62]),   # Bbmaj7
    dict(bass=41, pad=[53, 57, 60, 64]),   # Fmaj7
    dict(bass=48, pad=[52, 55, 60, 67]),   # C
]
HOOK = [74, None, 77, None, 76, 74, 72, None,   69, None, 72, None, 74, None, None, None]
s2.HOOK_B = [74, None, 77, None, 79, 77, 76, None,  77, None, 76, 72, 74, None, None, None]


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def shutter():
    """Camera shutter: two quick mechanical clicks."""
    t = _t(0.12)
    out = np.zeros(len(t))
    for d, a in ((0.0, 1.0), (0.045, 0.7)):
        i = int(d * SR)
        k = t[: len(t) - i]
        click = m.spectral(rng.standard_normal(len(k)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 3200)) ** 2) / 0.4))
        out[i:] += a * click * np.exp(-k / 0.008)
    return out


def car_door():
    t = _t(0.6)
    thud = np.sin(2 * np.pi * (70 + 50 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.12)
    body = m.lowpass(rng.standard_normal(len(t)), 600) * np.exp(-t / 0.06)
    latch = m.highpass(rng.standard_normal(len(t)), 3000) * np.exp(-np.maximum(t - 0.03, 0) / 0.01) * (t > 0.03)
    return thud + 0.5 * body + 0.25 * latch


def compose(starts, total, cues, path):
    s_hook, s_arrive, s_photos, s_pip, s_apply, s_chem, s_std, s_end = starts
    tr = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []
    BAR = s2.BAR

    # Hook: soft pad, drop plip as the serum lands, shimmer, riser into the beat.
    pads.add(0.0, m.pad(s2.PROG[0]["pad"], s_arrive + 0.3, attack=0.5, bright=0.9), 0.24, verb=0.6)
    tr.add(0.9, s3.plip(), 0.16, verb=0.5)
    tr.add(1.0, s3.shimmer([74, 77, 81, 86]), 0.05, pan=0.2, verb=0.7)
    tr.add(0.4, m.epiano(74, 2.2, 0.7), 0.09, verb=0.6)
    tr.add(s_arrive - 1.0, m.riser(1.0), 0.04, verb=0.4)
    tr.add(s_arrive - 0.35, m.whoosh(0.5), 0.09, verb=0.2)

    # 01 Factory visits: groove in, car door, shutter per photo.
    kicks += s2.groove(tr, pads, s_arrive, s_pip, hook=None)
    tr.add(s_arrive + 0.25, car_door(), 0.30, verb=0.25)
    for c in cues["photo_changes"]:
        tr.add(s_photos + c + 0.05, shutter(), 0.22, pan=0.15, verb=0.2)
    tr.add(s_photos - 0.3, m.whoosh(0.45), 0.06, verb=0.2)

    # 02 Formulation testing: hook melody enters.
    tr.add(s_pip - 0.3, m.whoosh(0.45), 0.06, verb=0.2)
    kicks += s2.groove(tr, pads, s_pip, s_chem, hook=HOOK)
    tr.add(s_pip + 0.7, s3.plip(), 0.12, verb=0.4)
    tr.add(s_pip + 1.9, s3.plip(), 0.09, verb=0.4)
    tr.add(s_apply + 0.2, s3.rub_swish(s_chem - s_apply), 0.05, verb=0.2)
    for d in cues["apply_words"]:
        tr.add(s_apply + d, m.tick(91), 0.05, verb=0.3)

    # 03 Chemist consultations: drums out, piano hook alone, clinks + node ticks as it draws.
    tr.add(s_chem - 0.3, m.whoosh(0.45), 0.06, verb=0.3)
    s2.groove(tr, pads, s_chem, s_std, drums=False, snaps=False, shake=False, hook=HOOK, keys=False)
    d0, d1 = cues["chem"]
    for i in range(10):
        tr.add(s_chem + d0 + (d1 - d0) * i / 10, m.tick(96 + (i % 4) * 2), 0.04, pan=-0.4 + 0.08 * i, verb=0.3)
    tr.add(s_chem + d1, s3.glass_clink(1.0), 0.06, pan=-0.2, verb=0.5)
    tr.add(s_chem + d1 + 0.25, s3.glass_clink(1.19), 0.05, pan=0.25, verb=0.5)
    tr.add(s_std - 1.3, m.riser(1.3), 0.06, verb=0.4)

    # The standard: impact, full groove with hook.
    tr.add(s_std, m.boom(1.8, 44), 0.36, verb=0.35)
    tr.add(s_std, m.bell(86), 0.09, verb=0.6)
    kicks += s2.groove(tr, pads, s_std, s_end, hook=HOOK)

    # End card: resolve on Dm(add9)/F colour + shimmer.
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.08, verb=0.4)
    tail = total - s_end
    pads.add(s_end, m.pad([50, 53, 57, 62, 64], tail - 0.6, attack=0.5, release=1.0, bright=1.3), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(38, tail), 0.14)
    for k, n in enumerate([62, 65, 69, 72, 76]):
        tr.add(s_end + 0.12 + k * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * k, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([86, 89, 93, 98]), 0.05, verb=0.8)

    # Mix (same chain as Day 2 v2).
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
