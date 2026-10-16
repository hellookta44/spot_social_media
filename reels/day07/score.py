"""Original score + sound design for the SPOT Day 7 Reel: inside Beauty Asia (all synthesised).

Same production as Days 2/5 (sidechain pad, sub, kick, snaps, shaker, piano hook
+ bell), brighter in A major: A – F#m – D – E. SFX: crowd murmur and footsteps in
the halls, a scanner beep + sweep on the skin analyzer, pen scratches on the notes,
a soft thud as each framed photo lands, a bell per lesson, a paper-bag rustle on
the last walk, a calm closing card, shimmer on the logo.
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
rng = np.random.default_rng(77)

s2.PROG[:] = [
    dict(bass=45, pad=[57, 61, 64, 69]),   # A
    dict(bass=42, pad=[54, 57, 61, 66]),   # F#m
    dict(bass=50, pad=[54, 57, 62, 66]),   # D
    dict(bass=52, pad=[56, 59, 64, 68]),   # E
]
HOOK = [73, None, 76, None, 78, 76, 73, None,   71, None, 73, None, 69, None, None, None]
s2.HOOK_B = [73, None, 76, None, 81, 78, 76, None,  78, None, 76, 73, 74, None, None, None]


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def crowd(dur):
    """Soft hall murmur: band-limited noise with syllable-rate movement."""
    t = _t(dur)
    x = m.spectral(rng.standard_normal(len(t)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 600)) ** 2) / 0.7))
    mod = 0.7 + 0.3 * np.abs(m.lowpass(rng.standard_normal(len(t)), 6))
    mod /= mod.max()
    return x * mod * np.minimum(1, t / 0.5) * np.clip((dur - t) / 0.5, 0, 1)


def footsteps(dur, rate=1.8):
    out = np.zeros(int(dur * SR))
    t = 0.1
    while t < dur - 0.2:
        k = _t(0.12)
        step = m.lowpass(rng.standard_normal(len(k)), 700) * np.exp(-k / 0.025)
        step += 0.3 * np.sin(2 * np.pi * 90 * k) * np.exp(-k / 0.03)
        i = int(t * SR)
        out[i:i + len(k)] += step
        t += 1 / rate
    return out


def scanner():
    t = _t(1.6)
    beep = np.sin(2 * np.pi * 1760 * t) * (t < 0.09) + np.sin(2 * np.pi * 2350 * t) * ((t > 0.14) & (t < 0.22))
    sweep = np.sin(2 * np.pi * np.cumsum(400 + 900 * np.clip((t - 0.3) / 1.0, 0, 1)) / SR) * \
        np.sin(np.pi * np.clip((t - 0.3) / 1.2, 0, 1)) * 0.35
    return beep * 0.6 + sweep


def bag_rustle(dur=1.0):
    t = _t(dur)
    x = m.spectral(rng.standard_normal(len(t)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 2500)) ** 2) / 0.8))
    return x * np.abs(m.lowpass(rng.standard_normal(len(t)), 12)) * 3 * np.clip((dur - t) / 0.3, 0, 1)


def compose(starts, total, cues, path):
    s_arrive, s_intro, s_walk, s_booth, s_scan, s_notes, s_less, s_walk2, s_close, s_end = starts
    tr = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []

    # Arrival: pad + shimmer, crowd fades in, riser into the beat.
    pads.add(0.0, m.pad(s2.PROG[0]["pad"], s_walk + 0.3, attack=0.4, bright=1.0), 0.24, verb=0.6)
    tr.add(0.2, s3.shimmer([81, 85, 88, 93]), 0.05, pan=0.2, verb=0.7)
    tr.add(0.0, crowd(s_less + 0.5), 0.05, verb=0.3)  # under the hall shots
    tr.add(s_intro - 0.3, m.whoosh(0.45), 0.06, verb=0.2)
    pads.add(s_intro, m.pad(s2.PROG[1]["pad"], s_walk - s_intro + 0.3, attack=0.3, bright=1.1), 0.22, verb=0.6)
    for j, n in enumerate([73, 76, 81]):
        tr.add(s_intro + 0.3 + j * 0.45, m.epiano(n, 1.8, 0.7), 0.09, pan=-0.2 + 0.2 * j, verb=0.6)
    tr.add(s_intro + 1.3, m.bell(85, 2.0), 0.06, verb=0.7)
    tr.add(s_walk - 1.0, m.riser(1.0), 0.04, verb=0.4)

    # Halls → booth → scanner → notes: full groove, hook from the booth on.
    kicks += s2.groove(tr, pads, s_walk, s_booth, hook=None)
    kicks += s2.groove(tr, pads, s_booth, s_less, hook=HOOK)
    for t in (s_walk, s_booth, s_scan, s_notes):
        tr.add(t - 0.3, m.whoosh(0.45), 0.05, verb=0.2)
    tr.add(s_walk, footsteps(s_booth - s_walk), 0.10, pan=-0.1)
    for t in (s_walk, s_booth, s_notes, s_walk2):
        tr.add(t + 0.05, m.thud(), 0.12, verb=0.25)
    tr.add(s_scan + 0.15, scanner(), 0.10, pan=0.15, verb=0.3)
    tr.add(s_notes + 0.5, s2.pen_tick(), 0.12, verb=0.2)
    tr.add(s_notes + 1.0, s3.rub_swish(1.4, rate=3.0), 0.04, verb=0.2)

    # Lessons: drums out, pad + a bell per lesson.
    tr.add(s_less - 0.3, m.whoosh(0.45), 0.06, verb=0.3)
    s2.groove(tr, pads, s_less, s_walk2, drums=False, snaps=False, shake=False, hook=None, keys=False)
    for i, d in enumerate(cues["lessons"]):
        tr.add(s_less + d, m.bell(81 + 2 * i, 2.4), 0.08, verb=0.6)
        tr.add(s_less + d, m.epiano(69 + 4 * i, 1.6, 0.7), 0.08, verb=0.5)

    # Last walk: groove back with hook, footsteps + bag rustle.
    tr.add(s_walk2 - 0.4, m.riser(0.4), 0.03, verb=0.4)
    tr.add(s_walk2, m.boom(1.4, 46), 0.22, verb=0.35)
    kicks += s2.groove(tr, pads, s_walk2, s_close, hook=HOOK)
    tr.add(s_walk2, footsteps(s_close - s_walk2), 0.09, pan=0.1)
    # Closing statement: drums out, warm pad + slow keys.
    tr.add(s_close - 0.3, m.whoosh(0.45), 0.06, verb=0.3)
    s2.groove(tr, pads, s_close, s_end, drums=False, snaps=False, shake=False, hook=HOOK, keys=False)
    tr.add(s_close + 0.2, m.bell(88, 2.4), 0.06, verb=0.7)
    tr.add(s_walk2 + 0.4, bag_rustle(), 0.06, pan=-0.2, verb=0.2)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.08, verb=0.4)

    # End card: Amaj9 resolve + shimmer.
    tail = total - s_end
    pads.add(s_end, m.pad([57, 61, 64, 68, 71], tail - 0.6, attack=0.5, release=1.0, bright=1.3), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(45, tail), 0.14)
    for j, n in enumerate([69, 73, 76, 80, 83]):
        tr.add(s_end + 0.12 + j * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * j, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([88, 92, 95, 100]), 0.05, verb=0.8)

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
