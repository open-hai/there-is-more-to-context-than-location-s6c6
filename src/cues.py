"""Cue functions: the sensor-to-cue mapping of Section 5.3.

The paper names the cues -- "artificial light", "brightness", "stationary",
"walking", "running" -- and says only that "simple statistical functions can be
applied" to obtain them.  Every function below is therefore a reconstruction; the
free parameters live in src/assumptions.py (D4-D8) and are reported by
src/analyze.py so a reader can see what was invented.
"""

from __future__ import annotations

import numpy as np

from assumptions import value

BRIGHTNESS_VALUES = ("dark", "dim", "bright")
LIGHT_TYPE_VALUES = ("artificial", "natural")
MOTION_VALUES = ("stationary", "walking", "running")
TEMP_VALUES = ("cold", "room temperature", "warm")


def brightness(window: np.ndarray, full_scale: float = 255.0) -> str:
    """Mean level of the light channel, cut into three symbols (D4)."""
    frac = float(np.mean(window)) / full_scale
    if frac < value("D4", "dark_below"):
        return "dark"
    if frac > value("D4", "bright_above"):
        return "bright"
    return "dim"


def flicker_prominence(window: np.ndarray, sample_rate_hz: float, mains_hz: float) -> float:
    """How far the mains-flicker band stands out of the window's noise floor (D5, D6).

    Mean spectral power in a band around twice the mains frequency, divided by the
    median spectral power above a low-frequency cutoff.  A value near 1 means no
    peak at all; the cue calls the light artificial above the D5 threshold.
    """
    x = np.asarray(window, dtype=float)
    x = x - x.mean()
    if x.size < 8 or not np.any(x):
        return 0.0
    spec = np.abs(np.fft.rfft(x * np.hanning(x.size))) ** 2
    freqs = np.fft.rfftfreq(x.size, d=1.0 / sample_rate_hz)
    band = value("D5", "band_hz")
    cutoff = value("D5", "hp_cutoff_hz")
    target = 2.0 * mains_hz
    sel = np.abs(freqs - target) <= band
    # Power is compared only above a low-frequency cutoff, so that slow changes in
    # illumination (drifting cloud, walking past a window) do not swamp the ratio.
    floor = np.median(spec[freqs > cutoff]) if np.any(freqs > cutoff) else 0.0
    if floor <= 0 or not np.any(sel):
        return 0.0
    return float(spec[sel].mean() / floor)


def flicker_observable(sample_rate_hz: float, mains_hz: float) -> bool:
    """Is 2x mains below the Nyquist frequency of this channel?"""
    return sample_rate_hz > 2.0 * (2.0 * mains_hz)


def light_type(window: np.ndarray, sample_rate_hz: float, mains_hz: float) -> str:
    """"artificial light" vs natural light (D5).

    Above Nyquist for the flicker component the cue reads the flicker band
    directly.  Below it, the flicker still shows up as excess high-frequency
    variance (aliased), so a variance fallback is used -- but the frequency can no
    longer be identified, which is exactly the sensitivity D1/D5 record.
    """
    if flicker_observable(sample_rate_hz, mains_hz):
        prom = flicker_prominence(window, sample_rate_hz, mains_hz)
        return "artificial" if prom > value("D5", "prominence_threshold") else "natural"
    x = np.asarray(window, dtype=float)
    ac = float(np.std(np.diff(x))) if x.size > 1 else 0.0
    return "artificial" if ac > 1.0 else "natural"


def motion(acc_window: np.ndarray) -> str:
    """Accelerometer cue: stationary / walking / running (D8).

    acc_window is an (n, k) array of k accelerometer axes in ADC counts.
    """
    a = np.atleast_2d(np.asarray(acc_window, dtype=float))
    if a.shape[0] < a.shape[1]:
        a = a.T
    mag = np.linalg.norm(a - a.mean(axis=0), axis=1)
    sd = float(np.std(mag))
    if sd < value("D8", "stationary_below"):
        return "stationary"
    if sd < value("D8", "walking_below"):
        return "walking"
    return "running"


def temperature(window: np.ndarray) -> str:
    """No temperature cue is named in the paper beyond Table 1's 'room temperature'."""
    m = float(np.mean(window))
    if m < 16.0:
        return "cold"
    if m > 26.0:
        return "warm"
    return "room temperature"
