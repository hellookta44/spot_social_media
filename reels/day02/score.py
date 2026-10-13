"""Original score + sound design for the SPOT Day 2 Reel (v2, all synthesised).

Music: 96 BPM in F major (F – Am – Dm – Bb), a memorable 2-bar piano hook doubled
by a soft bell, sidechain-pumped pad, sub bass, kick, finger snaps and shaker.
Arrangement follows the edit: intro → groove under the checklist → hook melody
on the testing shots → breakdown on the pipette → full drop on the 35 → 6
countdown → resolve on the logo.

SFX: pouch crinkle + hit on "Sample #17582", pen ticks on each check, a wrong-note
blip + paper slap + thud on REJECTED, drop plip and rubbing swish on the skin test,
falling ticks under the countdown and an impact on "only 6", shimmer on the logo.
"""
import importlib.util
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("day03_score", os.path.join(HERE, "..", "day03", "score.py"))
s3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s3)
m = s3.m
SR = m.SR
rng = np.random.default_rng(22)

BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
PROG = [  # (bass, pad voicing, melody-friendly chord name)
    dict(bass=41, pad=[53, 57, 60, 64]),   # Fmaj7
    dict(bass=45, pad=[52, 57, 60, 64]),   # Am7
    dict(bass=38, pad=[50, 57, 60, 65]),   # Dm7
    dict(bass=46, pad=[50, 53, 58, 62]),   # Bbmaj7
]
# 2-bar hook in eighth notes (None = rest), over two chords.
HOOK = [69, None, 72, None, 74, 72, 69, None,   67, None, 69, None, 65, None, None, None]
HOOK_B = [69, None, 72, None, 76, 74, 72, None,  74, None, 72, 69, 70, None, None, None]


# --------------------------------------------------------------------------- extra instruments / SFX

def _t(dur):
    return np.arange(int(dur * SR)) / SR


def snap(vel=1.0):
    t = _t(0.18)
    body = m.spectral(rng.standard_normal(len(t)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 2200)) ** 2) / 0.25))
    return body * (np.exp(-t / 0.018) + 0.25 * np.exp(-t / 0.06)) * vel


def shaker(vel=1.0):
    t = _t(0.09)
    x = m.highpass(rng.standard_normal(len(t)), 6000, 3)
    return x * np.sin(np.pi * np.clip(t / 0.06, 0, 1)) ** 2 * vel


def sub(midi, dur):
    t = _t(dur)
    f = m.hz(midi)
    return np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.01) * np.exp(-t / 1.6) * np.clip((dur - t) / 0.05, 0, 1)


def pen_tick():
    t = _t(0.06)
    click = m.spectral(rng.standard_normal(len(t)), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 4200)) ** 2) / 0.2))
    return click * np.exp(-t / 0.006) + 0.4 * np.sin(2 * np.pi * 1850 * t) * np.exp(-t / 0.012)


def paper_slap():
    t = _t(0.25)
    return m.lowpass(rng.standard_normal(len(t)), 3500) * np.exp(-t / 0.035)


def wrong_blip():
    t = _t(0.3)
    f = 420 - 140 * np.minimum(1, t / 0.15)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) * np.minimum(1, t / 0.004)


def crinkle(dur=1.0):
    t = _t(dur)
    x = m.highpass(rng.standard_normal(len(t)), 2200)
    gate = np.zeros(len(t))
    for _ in range(int(dur * 55)):
        i = rng.integers(0, len(t) - 600)
        gate[i:i + 600] += rng.uniform(0.2, 1.0) * np.exp(-np.arange(600) / 90)
    return x * gate * np.minimum(1, t / 0.05) * np.clip((dur - t) / 0.25, 0, 1)


# --------------------------------------------------------------------------- arrangement helpers

def groove(tr, pads, t0, t1, drums=True, snaps=True, shake=True, hook=None, keys=True):
    """Lay bars from t0 until t1. Returns kick times (for sidechain)."""
    kicks = []
    nb = int(np.ceil((t1 - t0) / BAR - 1e-6))
    for b in range(nb):
        tb = t0 + b * BAR
        ch = PROG[b % 4]
        pads.add(tb, m.pad(ch["pad"], BAR, attack=0.25, release=0.5, bright=1.2), 0.26, verb=0.5)
        tr.add(tb, sub(ch["bass"], BEAT * 1.8), 0.17)
        tr.add(tb + BEAT * 2.5, sub(ch["bass"], BEAT * 1.4), 0.13)
        tr.add(tb, m.bass(ch["bass"], BEAT * 3.5), 0.10)
        if keys:  # off-beat chord stabs on the piano
            for q in (0.5, 1.5, 2.5, 3.5):
                for n in ch["pad"][1:]:
                    tr.add(tb + q * BEAT, m.epiano(n + 12, 0.5, 0.55), 0.035, pan=0.15, verb=0.3)
        for q in range(4):
            tq = tb + q * BEAT
            if tq >= t1:
                break
            if drums and q in (0, 2):
                tr.add(tq, m.kick(0.9), 0.36)
                kicks.append(tq)
            if snaps and q in (1, 3):
                tr.add(tq, snap(), 0.16, pan=-0.1, verb=0.35)
            if shake:
                for e in range(4):
                    tr.add(tq + e * BEAT / 4, shaker(0.9 if e % 2 else 0.5), 0.05, pan=0.35)
        if hook and b % 2 == 0:
            phrase = hook if (b // 2) % 2 == 0 else HOOK_B
            for k, n in enumerate(phrase):
                if n is None:
                    continue
                tn = tb + k * BEAT / 2
                if tn >= t1:
                    break
                tr.add(tn, m.epiano(n, 1.4, 0.9), 0.15, pan=-0.1, verb=0.45)
                tr.add(tn, m.bell(n + 12, 1.6), 0.025, pan=0.2, verb=0.6)
    return kicks


def sidechain(n, kicks, depth=0.55, rel=0.16):
    env = np.ones(n)
    t = np.arange(n) / SR
    for k in kicks:
        i = int(k * SR)
        seg = t[i:min(n, i + int(0.6 * SR))] - k
        env[i:i + len(seg)] = np.minimum(env[i:i + len(seg)], 1 - depth * np.exp(-seg / rel))
    return env


# --------------------------------------------------------------------------- score

def compose(starts, total, cues, path):
    s_pouch, s_checks, s_inspect, s_skin, s_pip, s_count, s_q, s_end = starts
    tr = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []

    # 1. Intro on the pouch: filtered pad, crinkle, hit + shimmer as the code lands.
    pads.add(0.0, m.pad(PROG[0]["pad"], s_checks + 0.3, attack=0.5, bright=0.8), 0.24, verb=0.6)
    tr.add(0.05, crinkle(1.1), 0.12, pan=-0.2)
    tr.add(0.3, m.boom(1.6, 46), 0.34, verb=0.35)
    tr.add(0.3, s3.shimmer([77, 81, 84, 88]), 0.05, pan=0.2, verb=0.7)
    tr.add(s_checks - 1.2, m.riser(1.2), 0.04, verb=0.4)
    tr.add(s_checks - 0.35, m.whoosh(0.5), 0.09, verb=0.2)

    # 2. Checklist: groove in (no hook yet), pen ticks, then the rejection.
    kicks += groove(tr, pads, s_checks, s_inspect, hook=None)
    for i, c in enumerate(cues["checks"]):
        if i == cues["fail"]:
            tr.add(s_checks + c, wrong_blip(), 0.10, verb=0.3)
        else:
            tr.add(s_checks + c, pen_tick(), 0.16, pan=0.25, verb=0.2)
            tr.add(s_checks + c + 0.02, m.tick(96 + 2 * i), 0.05, verb=0.3)
    st = s_checks + cues["stamp"]
    tr.add(st, m.thud(), 0.50, verb=0.25)
    tr.add(st, paper_slap(), 0.20, verb=0.2)

    # 3–4. Testing shots: the hook melody enters.
    tr.add(s_inspect - 0.3, m.whoosh(0.45), 0.07, verb=0.2)
    kicks += groove(tr, pads, s_inspect, s_pip, hook=HOOK)
    tr.add(s_inspect + 1.2, s3.plip(), 0.10, verb=0.4)
    tr.add(s_skin - 0.3, m.whoosh(0.45), 0.06, verb=0.2)
    tr.add(s_skin + 0.2, s3.rub_swish(s_pip - s_skin), 0.06, pan=0.1, verb=0.2)
    for i in range(3):  # one soft tick per word
        tr.add(s_skin + 0.15 + i * 0.6, m.tick(91 + i), 0.05, verb=0.3)

    # 5. Pipette breakdown: drums out, hook on piano alone, riser into the drop.
    tr.add(s_pip - 0.3, m.whoosh(0.45), 0.06, verb=0.3)
    groove(tr, pads, s_pip, s_count, drums=False, snaps=False, shake=False, hook=HOOK, keys=False)
    tr.add(s_pip + 0.6, s3.plip(), 0.12, verb=0.5)
    tr.add(s_count - 1.4, m.riser(1.4), 0.06, verb=0.4)

    # 6. Countdown 35 → 6: full groove, falling ticks, impact on "only 6".
    c0, c1 = cues["count"]
    pads.add(s_count, m.pad(PROG[2]["pad"], c1 + 0.3, attack=0.3, bright=1.3), 0.26, verb=0.6)  # tension under the count
    tr.add(s_count, m.bass(PROG[2]["bass"], c1), 0.10)
    last = -1
    for i in range(int((c1 + 0.05) * SR / 400)):
        t = i * 400 / SR
        if t < c0:
            continue
        k = 1 - (1 - min(1, (t - c0) / (c1 - c0))) ** 3
        step = int(k * 24)
        if step != last:
            tr.add(s_count + t, m.tick(102 - step), 0.08, pan=0.3 if step % 2 else -0.3, verb=0.15)
            last = step
    tr.add(s_count + c1, m.boom(1.8, 44), 0.42, verb=0.35)
    tr.add(s_count + c1, m.bell(84), 0.10, verb=0.6)
    kicks += groove(tr, pads, s_count + c1, s_end, hook=HOOK)

    # 7–8. Question → end card: whoosh, Fmaj9 resolve, shimmer on the logo.
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.08, verb=0.4)
    tail = total - s_end
    pads.add(s_end, m.pad([52, 55, 57, 60, 64], tail - 0.6, attack=0.5, release=1.0, bright=1.3), 0.30, verb=0.7)
    tr.add(s_end, sub(41, tail), 0.14)
    for k, n in enumerate([64, 67, 69, 72, 76]):
        tr.add(s_end + 0.12 + k * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * k, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([84, 88, 91, 96]), 0.05, verb=0.8)

    # Mix: sidechain-pumped pad bus + main bus, shared reverb, same master chain as the series.
    n_all = tr.dry.shape[1]
    env = sidechain(n_all, kicks)
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
