"""Synthetic stand-in data, because the paper released none.

Nothing here reproduces the paper's measurements.  Fig. 4 shows light-sensor
traces from "two different contexts" with no units, no duration and no sample
count, and no data file was ever published (see SOURCES.md).  This generator
produces a stream with the *structure* the paper describes -- an interlaced
multi-sensor stream with a light channel that differs between indoor artificial
light and outdoor daylight -- so that the pipeline of Section 5 can be executed
end to end.  Any number computed from it is a number about this generator.

Columns written (the input contract in instrument.json):
    t_s, light_adc, acc_x_adc, acc_y_adc, temp_c, switch_a, switch_b, situation
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from assumptions import value

# Each segment: label, seconds, mean light (ADC counts), flicker amplitude,
# accelerometer agitation (counts), temperature (C), switch state (a, b).
SEGMENTS = [
    ("indoors-office-desk", 10, 95.0, 8.0, 0.8, 22.0, (0, 0)),
    ("indoors-dark-corridor", 6, 28.0, 6.0, 6.0, 21.0, (0, 1)),
    ("indoors-near-window", 8, 80.0, 6.0, 3.0, 22.0, (0, 1)),
    ("outdoors-walking", 10, 205.0, 0.0, 6.0, 17.0, (1, 1)),
    ("outdoors-running", 10, 215.0, 0.0, 22.0, 17.0, (1, 0)),
]

# The near-window segment sweeps the light level slowly across the assumed
# backlight thresholds (D13), which is what makes the hysteresis and debounce
# assumptions visible in the sensitivity table rather than free of consequence.
SWEPT_SEGMENT = "indoors-near-window"


def generate(sample_rate_hz: float | None = None, seed: int = 20250716,
             mains_hz: float | None = None) -> pd.DataFrame:
    fs = value("D1", "sample_rate_hz") if sample_rate_hz is None else sample_rate_hz
    mains = value("D6", "mains_hz") if mains_hz is None else mains_hz
    rng = np.random.default_rng(seed)
    rows = []
    t0 = 0.0
    for label, secs, mean_light, flicker, agit, temp, (sa, sb) in SEGMENTS:
        n = int(round(secs * fs))
        t = t0 + np.arange(n) / fs
        light = np.full(n, mean_light, dtype=float)
        if label == SWEPT_SEGMENT:
            # slow swing across the backlight switching band, plus flicker
            light += 45.0 * np.sin(2 * np.pi * 0.35 * t)
        if flicker > 0:
            # Fluorescent lighting flickers at twice the mains frequency.
            light += flicker * np.abs(np.sin(2 * np.pi * mains * t))
        else:
            # Daylight: slow cloud/shade drift only.
            light += 18.0 * np.sin(2 * np.pi * 0.08 * t)
        light += rng.normal(0.0, 0.3, n)
        light = np.clip(np.round(light), 0, 255)

        acc_x = np.round(128 + rng.normal(0.0, agit, n) +
                         (agit * 0.6 * np.sin(2 * np.pi * 1.9 * t) if agit > 3 else 0.0))
        acc_y = np.round(128 + rng.normal(0.0, agit, n) +
                         (agit * 0.5 * np.cos(2 * np.pi * 1.9 * t) if agit > 3 else 0.0))
        rows.append(pd.DataFrame({
            "t_s": t,
            "light_adc": light.astype(int),
            "acc_x_adc": np.clip(acc_x, 0, 255).astype(int),
            "acc_y_adc": np.clip(acc_y, 0, 255).astype(int),
            "temp_c": np.round(temp + rng.normal(0, 0.05, n), 2),
            "switch_a": sa,
            "switch_b": sb,
            "situation": label,
        }))
        t0 = float(t[-1] + 1.0 / fs)
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="CSV to write")
    ap.add_argument("--rate", type=float, default=None,
                    help="sample rate in Hz (default: the D1 assumption, 128)")
    ap.add_argument("--seed", type=int, default=20250716)
    ap.add_argument("--mains", type=float, default=None, help="mains frequency in Hz (D6)")
    a = ap.parse_args()
    df = generate(sample_rate_hz=a.rate, seed=a.seed, mains_hz=a.mains)
    df.to_csv(a.out, index=False)
    print(f"wrote {a.out}: {len(df)} rows, {df.t_s.iloc[-1]:.2f} s, "
          f"{df.situation.nunique()} labelled situations (SYNTHETIC, not the paper's data)")


if __name__ == "__main__":
    main()
