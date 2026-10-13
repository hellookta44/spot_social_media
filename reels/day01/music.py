#!/usr/bin/env python3
"""Original background score for the SPOT Day 1 Reel, synthesised from scratch
(no samples or third-party music).

Cues follow the edit: ticks under the 700+ counter, a boom when it lands,
a soft beat while we're on the road, a thud on every REJECTED stamp, drums drop
out for the "your skin deserves" line, and a warm resolve on the logo.

compose(starts, total, path) is called by render.py; it can also be run alone:
    python3 reels/day01/music.py  ->  out/spot_day01_music.wav
"""
import os
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


# --------------------------------------------------------------------------- dsp

def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def spectral(x, fn):
    """Static filter applied in the frequency domain; fn(freqs) -> gain."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * fn(f), len(x))


def lowpass(x, fc, order=2):
    return spectral(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def highpass(x, fc, order=2):
    return spectral(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def reverb(x, seconds=2.4, decay=0.55, seed=1):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-t / decay)
    ir = lowpass(ir, 5500)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    ir /= np.sqrt(np.sum(ir ** 2))
    size = len(x) + n
    nfft = 1 << (size - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return y


class Track:
    def __init__(self, seconds):
        self.n = int(seconds * SR) + SR
        self.dry = np.zeros((2, self.n))
        self.send = np.zeros((2, self.n))

    def add(self, t0, sig, gain=1.0, pan=0.0, verb=0.0):
        i = int(t0 * SR)
        if i >= self.n:
            return
        sig = sig[: self.n - i]
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        for ch, g in ((0, l), (1, r)):
            self.dry[ch, i:i + len(sig)] += sig * gain * g * np.sqrt(2)
            if verb:
                self.send[ch, i:i + len(sig)] += sig * gain * g * np.sqrt(2) * verb


def env_adsr(n, a, r, sustain_until=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    end = sustain_until if sustain_until is not None else n / SR - r
    e *= np.clip(1 - (t - end) / r, 0, 1)
    return e


# --------------------------------------------------------------------------- instruments

def pad(notes, dur, attack=0.8, release=1.0, bright=1.0):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for m in notes:
        f = hz(m)
        for det in (-0.004, 0.0, 0.0035):
            ph = rng.uniform(0, 2 * np.pi)
            for k in range(1, 7):
                if f * k > 6000:
                    break
                y += np.sin(2 * np.pi * f * (1 + det) * k * t + ph * k) / k ** (1.9 - 0.4 * bright)
    y *= env_adsr(n, attack, release, dur)
    # slow shimmer
    y *= 1 + 0.08 * np.sin(2 * np.pi * 0.23 * t)
    return y / (len(notes) * 3)


def epiano(m, dur=1.6, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    index = 1.6 * vel * np.exp(-t / 0.22)
    y = np.sin(2 * np.pi * f * t + index * np.sin(2 * np.pi * f * t))
    y += 0.18 * vel * np.sin(2 * np.pi * f * 4.02 * t) * np.exp(-t / 0.08)  # tine
    e = np.exp(-t / (0.55 + 120 / f)) * np.minimum(1, t / 0.004)
    e *= np.clip((dur - t) / 0.05, 0, 1)
    return y * e * vel


def bell(m, dur=3.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    y = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.6)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.25))
    return y * np.exp(-t / 1.4) * np.minimum(1, t / 0.002)


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return y * np.exp(-t / 0.9) * np.minimum(1, t / 0.01) * np.clip((dur - t) / 0.06, 0, 1)


def kick(vel=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 42 + 85 * np.exp(-t / 0.035)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    click = highpass(rng.standard_normal(n), 2500) * np.exp(-t / 0.004) * 0.15
    return (y + click) * vel


def hat(vel=1.0, length=0.05):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return highpass(rng.standard_normal(n), 7000, 3) * np.exp(-t / length) * vel


def clap(vel=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = spectral(rng.standard_normal(n), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 1500)) ** 2) / 0.5))
    e = sum(np.exp(-(t - d) / 0.012) * (t >= d) for d in (0, 0.011, 0.022)) + np.exp(-t / 0.09) * 0.6
    return noise * e * vel


def tick(m=96):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * hz(m) * t) * np.exp(-t / 0.008)


def boom(length=1.6, f0=55):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = f0 + 70 * np.exp(-t / 0.06)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (length / 3))
    y += lowpass(rng.standard_normal(n), 900) * np.exp(-t / 0.12) * 0.5
    return y


def thud():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 48 + 60 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    y += lowpass(rng.standard_normal(n), 1800) * np.exp(-t / 0.025) * 0.7
    return y


def riser(length):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = highpass(rng.standard_normal(n), 1200)
    return x * (t / length) ** 2.2


def whoosh(length=0.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = spectral(rng.standard_normal(n), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 2500)) ** 2) / 1.2))
    return x * np.sin(np.pi * t / length) ** 3


# --------------------------------------------------------------------------- score

# A minor: Am – Fmaj7 – C – G, then Fmaj7 – Gsus for the emotional beat, Cmaj9 on the logo.
CHORDS = {
    "Am": dict(bass=45, pad=[57, 60, 64, 67], arp=[69, 72, 76, 79]),
    "F": dict(bass=41, pad=[53, 57, 60, 64], arp=[65, 69, 72, 76]),
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "G": dict(bass=43, pad=[55, 59, 62, 67], arp=[67, 71, 74, 79]),
    "Gsus": dict(bass=43, pad=[55, 60, 62, 67], arp=[67, 72, 74, 79]),
    "Cmaj9": dict(bass=36, pad=[52, 55, 59, 62, 64], arp=[64, 67, 71, 74]),
}
ARP = [0, 1, 2, 3, 2, 1, 2, 3]


def counter_progress(t):
    t = min(max((t - 0.25) / 1.6, 0), 1)
    return 1 - (1 - t) ** 3


def compose(starts, total, path):
    """starts: scene start times [s1..s6] in seconds; total: video length."""
    s1, s2, s3, s4, s5, s6 = starts
    tr = Track(total + 0.5)
    bar = (s5 - s2) / 4          # four bars from "on the road" to "your skin deserves"
    beat = bar / 4

    # --- Scene 1: hook. Pad, ticks that slow down with the counter, boom when 700+ lands.
    tr.add(0.0, pad(CHORDS["Am"]["pad"], s2 + 0.3, attack=0.4), 0.30, verb=0.5)
    last = -1
    for i in range(int(1.85 * SR / 400)):
        t = i * 400 / SR
        step = int(counter_progress(t) * 24)
        if step != last and 0.25 <= t <= 1.85:
            tr.add(t, tick(96 + (step % 2) * 3), 0.10, pan=0.3 if step % 2 else -0.3, verb=0.15)
            last = step
    tr.add(0.35, riser(1.5), 0.05, verb=0.3)
    tr.add(1.85, boom(), 0.38, verb=0.35)
    tr.add(1.85, bell(81), 0.12, verb=0.6)
    tr.add(s2 - 0.45, whoosh(0.6), 0.10, verb=0.2)

    # --- Scenes 2–4: soft groove, Am – F – C – G.
    for b, name in enumerate(["Am", "F", "C", "G"]):
        t0 = s2 + b * bar
        ch = CHORDS[name]
        tr.add(t0, pad(ch["pad"], bar, attack=0.3, release=0.6), 0.22, verb=0.4)
        tr.add(t0, bass(ch["bass"], beat * 2.5), 0.20)
        tr.add(t0 + beat * 2.5, bass(ch["bass"], beat * 1.5), 0.15)
        for k in range(8):
            vel = 0.85 if k % 2 == 0 else 0.6
            tr.add(t0 + k * beat / 2, epiano(ch["arp"][ARP[k]], 1.2, vel), 0.15,
                   pan=-0.35 + 0.1 * k, verb=0.35)
        for q in range(4):
            tq = t0 + q * beat
            if q in (0, 2):
                tr.add(tq, kick(), 0.34)
            else:
                tr.add(tq, clap(), 0.10, verb=0.25)
            tr.add(tq + beat / 2, hat(), 0.05, pan=0.25)
            if tq >= s4 - 0.01:  # extra drive under the REJECTED stamps
                tr.add(tq + beat / 4, hat(0.6, 0.03), 0.04, pan=-0.25)
                tr.add(tq + 3 * beat / 4, hat(0.6, 0.03), 0.04, pan=-0.25)
    for t in (s3, s4):
        tr.add(t - 0.35, whoosh(0.5), 0.06, verb=0.2)

    # REJECTED stamps (render.py: scene 4 at +0.55, +1.15, +1.75)
    for d in (0.55, 1.15, 1.75):
        tr.add(s4 + d, thud(), 0.42, verb=0.2)

    # --- Scene 5: drums drop out, keys + pad carry the line.
    tr.add(s5 - 0.6, riser(0.6), 0.03, verb=0.4)
    tr.add(s5, boom(2.0, 45), 0.14, verb=0.5)
    half = (s6 - s5) / 2
    for i, name in enumerate(["F", "Gsus"]):
        t0 = s5 + i * half
        ch = CHORDS[name]
        tr.add(t0, pad(ch["pad"], half, attack=0.5, release=1.2, bright=1.3), 0.30, verb=0.6)
        tr.add(t0, bass(ch["bass"], half), 0.16)
        for k, m in enumerate(ch["arp"]):
            tr.add(t0 + k * 0.12, epiano(m, 2.2, 0.8), 0.09, pan=-0.3 + 0.2 * k, verb=0.6)
        tr.add(t0 + half / 2, epiano(ch["arp"][-1] + 5, 1.8, 0.6), 0.07, pan=0.3, verb=0.7)
    tr.add(s6 - 0.5, whoosh(0.7), 0.07, verb=0.4)

    # --- Scene 6: Cmaj9 resolve on the logo, bell, long tail to the end.
    tail = total - s6
    ch = CHORDS["Cmaj9"]
    tr.add(s6, pad(ch["pad"], tail - 0.8, attack=0.6, release=1.0, bright=1.2), 0.32, verb=0.7)
    tr.add(s6, bass(ch["bass"], tail), 0.15)
    for k, m in enumerate(ch["arp"]):
        tr.add(s6 + 0.15 + k * 0.16, epiano(m, 2.8, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.7)
    tr.add(s6 + 0.1, bell(84), 0.12, verb=0.8)
    tr.add(s6 + 1.5, bell(91, 3.0), 0.05, pan=0.4, verb=0.9)

    # --- Mix
    wet = np.stack([reverb(tr.send[0], seed=11), reverb(tr.send[1], seed=23)])
    mix = tr.dry + 0.55 * wet
    mix = highpass(mix[0], 45)[None, :], highpass(mix[1], 45)[None, :]
    mix = np.concatenate(mix)
    n = int(total * SR)
    mix = mix[:, :n]
    rms = np.sqrt(np.mean(mix ** 2))
    mix *= 10 ** (-17 / 20) / rms                 # ~-17 dBFS RMS
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)       # gentle soft-clip
    mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))  # -1 dBFS peak
    t = np.arange(n) / SR
    mix *= np.minimum(1, t / 0.03)
    mix *= np.clip((total - t) / 1.6, 0, 1) ** 1.5

    pcm = (mix.T * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    import render

    starts, total = render.scene_timing()
    out = compose(starts, total, os.path.join(here, "out", "spot_day01_music.wav"))
    print("wrote", out, [round(s, 2) for s in starts], round(total, 2))
