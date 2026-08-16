"""The interlaced sensor stream of Sections 5.2-5.3, and what its byte budget allows.

Section 5.2 describes the data path: sensors -> A/D converter -> microcontroller ->
serial line -> host computer.  Section 5.3 gives one number for the whole path:
"The awareness device provides about 1100 Bytes of sensor readings per second.  The
data from different sensors is transmitted interlaced to ensure recognition of
sudden changes in the readings."

That single number is the only quantitative fact in the paper's experimental
section, so it is worth spending arithmetic on: it bounds the per-channel sampling
rate, and therefore bounds which cues can be computed at all.
"""

from __future__ import annotations

import numpy as np

from assumptions import value

TOTAL_BYTES_PER_S = 1100.0  # Section 5.3, "about 1100 Bytes ... per second"


def interlace(channels: dict[str, np.ndarray], order: list[str]) -> bytes:
    """Round-robin interleave of one byte per channel per slot (D3)."""
    n = min(len(channels[c]) for c in order)
    out = bytearray()
    for i in range(n):
        for c in order:
            out.append(int(channels[c][i]) & 0xFF)
    return bytes(out)


def deinterlace(raw: bytes, order: list[str]) -> dict[str, np.ndarray]:
    """Inverse of `interlace`, given the channel order out of band (D3)."""
    k = len(order)
    arr = np.frombuffer(raw[: (len(raw) // k) * k], dtype=np.uint8).reshape(-1, k)
    return {c: arr[:, i].astype(float) for i, c in enumerate(order)}


def per_channel_rate(n_channels: int, bytes_per_sample: int = 1,
                     total_bytes_per_s: float = TOTAL_BYTES_PER_S) -> float:
    """Equal-share sampling rate per channel implied by the paper's 1100 B/s."""
    return total_bytes_per_s / (n_channels * bytes_per_sample)


def budget_table(max_channels: int = 8, bytes_per_sample: int = 1,
                 mains_hz: float | None = None) -> list[dict]:
    """For 1..max_channels equally interlaced channels: rate, and flicker headroom.

    A 100 Hz flicker component (50 Hz mains) needs a channel rate above 200 Hz to
    be resolved in frequency rather than aliased.
    """
    mains = mains_hz if mains_hz is not None else value("D6", "mains_hz")
    need = 2.0 * (2.0 * mains)
    rows = []
    for n in range(1, max_channels + 1):
        r = per_channel_rate(n, bytes_per_sample)
        rows.append({
            "channels": n,
            "bytes_per_sample": bytes_per_sample,
            "per_channel_rate_hz": round(r, 1),
            "rate_needed_for_flicker_hz": need,
            "flicker_resolvable": bool(r > need),
        })
    return rows


def max_channels_for_flicker(bytes_per_sample: int = 1, mains_hz: float | None = None,
                             total_bytes_per_s: float = TOTAL_BYTES_PER_S) -> int:
    """Largest equally-interlaced channel count that still resolves the flicker."""
    mains = mains_hz if mains_hz is not None else value("D6", "mains_hz")
    need = 2.0 * (2.0 * mains)
    n = 0
    while per_channel_rate(n + 1, bytes_per_sample, total_bytes_per_s) > need:
        n += 1
    return n


if __name__ == "__main__":
    import json

    print(json.dumps({
        "total_bytes_per_s": TOTAL_BYTES_PER_S,
        "budget": budget_table(),
        "max_channels_resolving_100hz_flicker": max_channels_for_flicker(),
    }, indent=2))
