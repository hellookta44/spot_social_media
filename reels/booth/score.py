"""Original score + sound design for the SPOT booth recap reel (all synthesised).

Same production as Days 2/5/7 (sidechain pad, sub, kick, snaps, shaker, piano hook +
bell), warm and upbeat in D major: D – Bm – G – A. SFX: light-switch clunk + hum as
the booth lights up, expo crowd murmur, footsteps, a soft pop for every speech bubble,
drop + rub on the tester, scanner beep + success chime on the waitlist, bag rustle,
gentle applause on "Thank you for stopping by", shimmer on the logo.
"""
import importlib.util
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s2 = _load("day02_score", os.path.join(HERE, "..", "day02", "score.py"))
s7 = _load("day07_score", os.path.join(HERE, "..", "day07", "score.py"))
s3, m = s2.s3, s2.m
SR = m.SR
rng = np.random.default_rng(303)

s2.PROG[:] = [
    dict(bass=38, pad=[50, 54, 57, 62]),   # D
    dict(bass=47, pad=[50, 54, 59, 62]),   # Bm
    dict(bass=43, pad=[55, 59, 62, 66]),   # Gmaj7
    dict(bass=45, pad=[52, 57, 61, 64]),   # A
]
HOOK = [74, None, 78, None, 81, 78, 74, None,   73, None, 74, None, 71, None, None, None]
s2.HOOK_B = [74, None, 78, None, 83, 81, 78, None,  81, None, 78, 74, 76, None, None, None]


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def light_switch():
    t = _t(0.25)
    click = m.highpass(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.006)
    thunk = np.sin(2 * np.pi * (110 + 80 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.05)
    return click * 0.8 + thunk


def hum(dur):
    t = _t(dur)
    x = sum(np.sin(2 * np.pi * f * t) / k for k, f in enumerate((100, 200, 300), start=1))
    return x * np.minimum(1, t / 0.4) * np.clip((dur - t) / 0.5, 0, 1)


def pop():
    t = _t(0.12)
    f = 900 + 700 * np.exp(-t / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)


def success():
    out = np.zeros(int(1.4 * SR))
    for k, n in enumerate([79, 83, 86]):
        b = m.bell(n, 1.0)
        i = int(k * 0.09 * SR)
        out[i:i + len(b)] += b[: len(out) - i]
    return out


def applause(dur=2.4):
    out = np.zeros(int(dur * SR))
    for _ in range(int(dur * 60)):
        i = rng.integers(0, len(out) - 2000)
        k = _t(0.04)
        clap = m.spectral(rng.standard_normal(len(k)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 1800)) ** 2) / 0.4))
        out[i:i + len(k)] += clap * np.exp(-k / 0.01) * rng.uniform(0.3, 1.0)
    t = _t(dur)
    return out * np.minimum(1, t / 0.4) * np.clip((dur - t) / 0.8, 0, 1)


def compose(starts, total, cues, path):
    s_rev, s_conf, s_arr, s_hand, s_qa, s_wait, s_bag, s_bye, s_end = starts
    tr = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []

    # Reveal: dark hall, switch clunk, hum + pad swell as the lights come on.
    l0, l1 = cues["lights"]
    tr.add(0.0, s7.crowd(s_conf + 0.3), 0.04, verb=0.3)
    tr.add(l0, light_switch(), 0.30, verb=0.3)
    tr.add(l0, hum(s_conf - l0 + 0.2), 0.03)
    pads.add(l0, m.pad(s2.PROG[0]["pad"], s_conf - l0 + 0.4, attack=0.8, bright=1.0), 0.26, verb=0.6)
    tr.add(l1, s3.shimmer([81, 86, 90, 93]), 0.05, pan=0.2, verb=0.7)

    # Confession card: soft piano + bell, a smile in the melody.
    tr.add(s_conf - 0.3, m.whoosh(0.45), 0.06, verb=0.2)
    for j, n in enumerate([74, 78, 81, 86]):
        tr.add(s_conf + 0.3 + j * 0.32, m.epiano(n, 1.8, 0.7), 0.09, pan=-0.2 + 0.13 * j, verb=0.6)
    tr.add(s_arr - 0.9, m.riser(0.9), 0.04, verb=0.4)

    # Visitors → tester → Q&A → waitlist → bag: groove with hook.
    kicks += s2.groove(tr, pads, s_arr, s_bye, hook=HOOK)
    tr.add(s_arr, s7.crowd(s_wait - s_arr), 0.05, verb=0.3)
    tr.add(s_arr, s7.footsteps(1.8, rate=2.2), 0.10, pan=0.3)
    tr.add(s_arr + cues["hi"], pop(), 0.10, verb=0.3)
    for t in (s_hand, s_qa, s_wait, s_bag, s_bye):
        tr.add(t - 0.3, m.whoosh(0.45), 0.05, verb=0.2)
    tr.add(s_hand + cues["hand_land"], s3.plip(), 0.14, verb=0.4)
    r0, r1 = cues["hand_rub"]
    tr.add(s_hand + r0, s3.rub_swish(r1 - r0), 0.05, verb=0.2)
    tr.add(s_qa + cues["q"], pop(), 0.10, pan=0.25, verb=0.3)
    tr.add(s_qa + cues["a"], pop(), 0.10, pan=-0.25, verb=0.3)
    sc0, sc1 = cues["scan"]
    tr.add(s_wait + sc0, s7.scanner(), 0.10, pan=0.15, verb=0.3)
    tr.add(s_wait + cues["ok"], success(), 0.10, verb=0.5)
    tr.add(s_bag + 0.3, s7.bag_rustle(1.2), 0.08, verb=0.2)

    # Goodbye: drums out, applause, warm pad; logo resolve.
    s2.groove(tr, pads, s_bye, s_end, drums=False, snaps=False, shake=False, hook=HOOK, keys=False)
    tr.add(s_bye + 0.2, applause(), 0.10, verb=0.4)
    tr.add(s_bye + 0.4, s7.footsteps(2.4, rate=2.0), 0.07, pan=-0.3)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.08, verb=0.4)
    tail = total - s_end
    pads.add(s_end, m.pad([50, 54, 57, 61, 64], tail - 0.6, attack=0.5, release=1.0, bright=1.3), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(38, tail), 0.14)
    for j, n in enumerate([62, 66, 69, 73, 76]):
        tr.add(s_end + 0.12 + j * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * j, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([86, 90, 93, 98]), 0.05, verb=0.8)

    # Mix (same chain as Days 2, 5, 7).
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
