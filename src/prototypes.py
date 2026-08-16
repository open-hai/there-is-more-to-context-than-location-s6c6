"""The two Section 4.2 prototypes, reduced to the logic a reimplementation needs.

Section 4.2, light-sensitive display: "we integrated a light sensor in a Palm
Pilot, to provide it with an awareness of surrounding lighting conditions, which
can be applied for control of its display's backlight."  That is the whole
specification -- hence D13.

Section 4.2, orientation-sensitive user interface: "we have enhanced a PDA, in
this case a Newton MessagePad, with awareness for its orientation by adding two
mercury switches and simple electronics.  ... if the device is held upright the
user interface is displayed in the usual portrait mode, if it is turned sideways
the user interface is switched to landscape mode, and if it is further turned
upside down the user interface is also rotated accordingly."  The behaviour is
specified; the switch geometry and the state-to-orientation mapping are not --
hence D14 and D15.
"""

from __future__ import annotations

from itertools import permutations

import numpy as np

from assumptions import value

ORIENTATIONS = ("portrait", "landscape-right", "portrait-inverted", "landscape-left")
SWITCH_STATES = ((0, 0), (0, 1), (1, 1), (1, 0))

# D14: one arbitrary choice out of the 24 bijections the text does not constrain.
ASSUMED_MAPPING = dict(zip(SWITCH_STATES, ORIENTATIONS))


def n_consistent_mappings() -> int:
    """How many state-to-orientation bijections the paper's prose leaves open."""
    # The prose names the behaviours but never ties a switch state to an
    # orientation, so every bijection remains consistent with the text.
    return len(list(permutations(ORIENTATIONS)))


class OrientationDecoder:
    """Two mercury switches -> one of four screen orientations, with debounce (D15)."""

    def __init__(self, mapping: dict | None = None, debounce_s: float | None = None):
        self.mapping = dict(mapping or ASSUMED_MAPPING)
        self.debounce_s = value("D15", "debounce_s") if debounce_s is None else debounce_s
        self._candidate: tuple | None = None
        self._since: float | None = None
        self.state: str = ASSUMED_MAPPING[(0, 0)]

    def step(self, t_s: float, a: int, b: int) -> str:
        key = (int(a), int(b))
        target = self.mapping[key]
        if target != self.state:
            if self._candidate != key:
                self._candidate, self._since = key, t_s
            elif self._since is not None and t_s - self._since >= self.debounce_s:
                self.state = target
                self._candidate, self._since = None, None
        else:
            self._candidate, self._since = None, None
        return self.state

    def run(self, t: np.ndarray, a: np.ndarray, b: np.ndarray) -> list[str]:
        return [self.step(float(ti), ai, bi) for ti, ai, bi in zip(t, a, b)]


class BacklightController:
    """Light level -> backlight on/off, with hysteresis and debounce (D13)."""

    def __init__(self, on_below: float | None = None, off_above: float | None = None,
                 debounce_s: float | None = None, full_scale: float = 255.0):
        self.on_below = value("D13", "on_below") if on_below is None else on_below
        self.off_above = value("D13", "off_above") if off_above is None else off_above
        self.debounce_s = value("D13", "debounce_s") if debounce_s is None else debounce_s
        self.full_scale = full_scale
        self.on = False
        self._pending: bool | None = None
        self._since: float | None = None

    def step(self, t_s: float, light: float) -> bool:
        frac = float(light) / self.full_scale
        want = self.on
        if frac < self.on_below:
            want = True
        elif frac > self.off_above:
            want = False
        if want != self.on:
            if self._pending != want:
                self._pending, self._since = want, t_s
            elif self._since is not None and t_s - self._since >= self.debounce_s:
                self.on = want
                self._pending, self._since = None, None
        else:
            self._pending, self._since = None, None
        return self.on

    def run(self, t: np.ndarray, light: np.ndarray) -> np.ndarray:
        return np.array([self.step(float(ti), li) for ti, li in zip(t, light)], dtype=bool)


def backlight_sensitivity(t: np.ndarray, light: np.ndarray) -> list[dict]:
    """How many backlight switches the same trace produces under other settings."""
    grid = [
        (0.25, 0.35, 1.0),   # the assumed setting (D13)
        (0.25, 0.35, 0.0),   # no debounce
        (0.30, 0.30, 0.0),   # single threshold, no hysteresis, no debounce
        (0.15, 0.45, 1.0),   # wider hysteresis band
        (0.50, 0.60, 1.0),   # a much brighter switching point
    ]
    rows = []
    for on_below, off_above, deb in grid:
        c = BacklightController(on_below=on_below, off_above=off_above, debounce_s=deb)
        s = c.run(t, light)
        rows.append({
            "on_below": on_below, "off_above": off_above, "debounce_s": deb,
            "switches": int(np.sum(s[1:] != s[:-1])),
            "fraction_of_time_on": round(float(np.mean(s)), 3),
        })
    return rows
