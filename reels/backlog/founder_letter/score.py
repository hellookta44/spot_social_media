"""Original score + sound design for the SPOT Day 8 Reel: the typewritten letter (all synthesised).

The typewriter is the lead instrument: every keystroke is a struck key (click,
type-bar slap, platen thump), spaces are softer, and each line ends with the
margin bell and the carriage-return ratchet. Underneath, a hushed F-major piano
(F – Dm – Bb – C) with a warm pad. When the camera pulls back the room opens up:
a soft boom, the piano hook and a light groove carry the pen marks (felt-tip
squeaks on each underline) and the signature, then an Fmaj9 resolve on the logo.
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
rng = np.random.default_rng(88)

s2.PROG[:] = [
    dict(bass=41, pad=[53, 57, 60, 65]),   # F
    dict(bass=38, pad=[53, 57, 62, 65]),   # Dm
    dict(bass=46, pad=[53, 58, 62, 65]),   # Bb
    dict(bass=48, pad=[55, 60, 64, 67]),   # C
]
HOOK = [72, None, 74, None, 77, 76, 72, None,   70, None, 72, None, 69, None, None, None]
s2.HOOK_B = [72, None, 74, None, 79, 77, 76, None,  77, None, 76, 72, 74, None, None, None]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def bandnoise(n, centre, width=0.6):
    return m.spectral(rng.standard_normal(n), lambda f: np.exp(-((np.log(np.maximum(f, 1) / centre)) ** 2) / width))


def key(vel=1.0, space=False):
    """One typewriter strike: key click, type-bar slap on the platen, body thump."""
    t = _t(0.12)
    n = len(t)
    pitch = rng.uniform(0.85, 1.2)
    click = m.highpass(rng.standard_normal(n), 3000) * np.exp(-t / 0.0025)
    slap_at = int(rng.uniform(0.011, 0.016) * SR)
    slap = np.zeros(n)
    k = t[: n - slap_at]
    slap[slap_at:] = bandnoise(len(k), 2200 * pitch, 0.5) * np.exp(-k / 0.006) * 2.2
    body = np.sin(2 * np.pi * 150 * pitch * t) * np.exp(-t / 0.018) * 0.5
    if space:  # the space bar: duller, no type bar
        return (0.4 * click + 1.4 * body + 0.5 * m.lowpass(rng.standard_normal(n), 900) * np.exp(-t / 0.02)) * vel
    return (0.6 * click + slap + body) * vel


def margin_bell():
    t = _t(1.4)
    y = (np.sin(2 * np.pi * 2093 * t) + 0.5 * np.sin(2 * np.pi * 2093 * 2.41 * t) * np.exp(-t / 0.2)
         + 0.25 * np.sin(2 * np.pi * 2093 * 3.9 * t) * np.exp(-t / 0.08))
    return y * np.exp(-t / 0.5) * np.minimum(1, t / 0.001)


def carriage_return(dur=0.42):
    """Ratchet clicks speeding up as the carriage slides back, then the stop."""
    out = np.zeros(int((dur + 0.1) * SR))
    tc = 0.0
    gap = 0.03
    while tc < dur:
        k = _t(0.01)
        i = int(tc * SR)
        out[i:i + len(k)] += m.highpass(rng.standard_normal(len(k)), 2500) * np.exp(-k / 0.0015) * 0.5
        tc += gap
        gap *= 0.93
    t = _t(dur)
    out[:len(t)] += bandnoise(len(t), 900, 0.8) * np.sin(np.pi * t / dur) * 0.35   # slide
    k = _t(0.1)
    i = int(dur * SR)
    out[i:i + len(k)] += (np.sin(2 * np.pi * 110 * k) * np.exp(-k / 0.03) +
                          m.highpass(rng.standard_normal(len(k)), 1500) * np.exp(-k / 0.004))[: len(out) - i]
    return out


def pen(dur):
    """Felt-tip on paper: band-limited scratch with a stroke-shaped envelope."""
    t = _t(dur)
    x = bandnoise(len(t), 3800, 0.4) + 0.4 * bandnoise(len(t), 1200, 0.5)
    wob = 0.7 + 0.3 * np.sin(2 * np.pi * 9 * t + rng.uniform(0, 6))
    return x * wob * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6


def paper(dur=0.8):
    t = _t(dur)
    x = bandnoise(len(t), 2500, 0.9)
    return x * np.abs(m.lowpass(rng.standard_normal(len(t)), 14)) * 3 * np.clip((dur - t) / 0.3, 0, 1)


def piano_arps(tr, pads, t0, t1, gain, pad_gain):
    b = 0
    while t0 + b * s2.BAR < t1 - 0.05:
        tb = t0 + b * s2.BAR
        ch = s2.PROG[b % 4]
        pads.add(tb, m.pad(ch["pad"], s2.BAR + 0.4, attack=0.6, release=0.9, bright=0.8), pad_gain, verb=0.7)
        tr.add(tb, m.epiano(ch["bass"] + 12, 2.4, 0.6), gain * 0.9, pan=-0.15, verb=0.6)
        for k, idx in enumerate(ARP[::2]):  # quarter notes: leaves room for the keys
            tn = tb + k * s2.BEAT
            if tn >= t1:
                break
            tr.add(tn, m.epiano(ch["pad"][idx] + 12, 1.4, 0.55), gain, pan=0.2, verb=0.65)
        b += 1


def compose(starts, total, cues, path):
    _, s_end = starts
    tr = m.Track(total + 0.5)
    fx = m.Track(total + 0.5)      # typewriter + pens: not ducked by the sidechain
    pads = m.Track(total + 0.5)
    kicks = []
    pull = cues["pull"]

    # Paper in, then the letter: keys, bells and returns over a hushed piano.
    fx.add(0.0, paper(0.7), 0.05, pan=-0.2, verb=0.15)
    for t, ch in cues["keys"]:
        space = ch == " "
        fx.add(t, key(rng.uniform(0.8, 1.0), space), 0.42 if not space else 0.30,
               pan=float(rng.uniform(-0.25, 0.25)), verb=0.08)
    for t in cues["returns"]:
        fx.add(t, margin_bell(), 0.10, pan=0.35, verb=0.25)
        fx.add(t + 0.08, carriage_return(), 0.32, pan=-0.3, verb=0.1)
    piano_arps(tr, pads, 0.0, pull, gain=0.17, pad_gain=0.30)
    tr.add(0.25, s3.shimmer([77, 81, 84, 89]), 0.03, verb=0.7)

    # Pull-back: the room opens, boom + groove with the hook.
    tr.add(pull - 0.9, m.riser(0.9), 0.04, verb=0.4)
    tr.add(pull, m.whoosh(0.9), 0.06, verb=0.4)
    tr.add(pull + 0.4, m.boom(1.6, 41), 0.20, verb=0.35)
    kicks += s2.groove(tr, pads, pull + 0.4, s_end, snaps=True, shake=False, hook=HOOK, keys=False)
    for t, dur, kind in cues["marks"]:
        fx.add(t, pen(dur), 0.16 if kind == "under" else 0.18, pan=0.15, verb=0.15)
        tr.add(t + dur * 0.9, m.bell(84 if kind == "under" else 77, 1.8), 0.04, verb=0.6)
    t_sign, d_sign = cues["sign"]
    fx.add(t_sign, pen(d_sign * 0.5), 0.14, pan=-0.1, verb=0.15)
    fx.add(t_sign + d_sign * 0.55, pen(d_sign * 0.4), 0.12, pan=0.0, verb=0.15)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.07, verb=0.4)

    # End card: Fmaj9 resolve + shimmer.
    tail = total - s_end
    pads.add(s_end, m.pad([53, 57, 60, 64, 67], tail - 0.6, attack=0.5, release=1.0, bright=1.2), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(41, tail), 0.12)
    for j, n in enumerate([65, 69, 72, 76, 79]):
        tr.add(s_end + 0.12 + j * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * j, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([84, 88, 91, 96]), 0.05, verb=0.8)

    # Mix: music bus sidechained to the kick, typewriter on top, shared room reverb.
    n_all = tr.dry.shape[1]
    env = s2.sidechain(n_all, kicks)
    dry = tr.dry + pads.dry * env + fx.dry
    send = tr.send + pads.send * env + fx.send
    wet = np.stack([m.reverb(send[0], seed=11), m.reverb(send[1], seed=23)])
    mix = dry + 0.5 * wet
    mix = np.stack([m.highpass(mix[0], 40), m.highpass(mix[1], 40)])
    n = int(total * SR)
    mix = mix[:, :n]
    mix *= 10 ** (-17 / 20) / np.sqrt(np.mean(mix ** 2))
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
