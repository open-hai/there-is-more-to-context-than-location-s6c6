"""The layered sensor-fusion architecture of Section 5.1, as runnable code.

Section 5.1 defines four layers and, importantly, constraints on them:

  Sensors  -- "Each sensor is regarded as a time dependent function that returns
              a scalar, a vector, or a symbolic value.  A set (finite or
              infinite) of possible values for each sensor is defined."
              Physical sensors measure the environment; anything read from the
              host device is a *logical* sensor.
  Cues     -- "A cue is regarded as a function taking the values of a single
              sensor up to a certain time as input and providing a symbolic or
              sub-symbolic output. ... Each cue is dependent on a single sensor
              but different cues may be based on the same sensors."
  Contexts -- "The context is described by a set of two-dimensional vectors.
              Each vector consists of a symbolic value describing the situations
              and a number indicating the certainty."
  Scripting-- entering / leaving / while-in a context, each with a threshold on
              the certainty and a time.  A footnote adds: "In case of context
              prediction the time might be negative."

The single-sensor constraint on cues is *enforced* here, because it is what makes
the Section 6 claim about several light sensors jointly yielding "direction of
light" inexpressible at the cue layer (see REPRODUCIBILITY.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence


class ArchitectureError(ValueError):
    """Raised when a construction violates a rule the paper states."""


@dataclass
class Sensor:
    """A time-dependent function with a declared value set (Section 5.1)."""

    name: str
    kind: str  # "physical" | "logical"
    returns: str  # "scalar" | "vector" | "symbol"
    value_set: str  # prose description of the declared set of possible values
    sample_rate_hz: float | None = None

    def __post_init__(self):
        if self.kind not in ("physical", "logical"):
            raise ArchitectureError(f"sensor kind must be physical or logical: {self.kind}")
        if self.returns not in ("scalar", "vector", "symbol"):
            raise ArchitectureError(f"sensor must return scalar/vector/symbol: {self.returns}")


@dataclass
class Cue:
    """A function of *one* sensor's history up to a time t (Section 5.1)."""

    name: str
    sensors: Sequence[str]
    fn: Callable[[Sequence[float]], object]
    value_set: Sequence[object]
    window_s: float

    def __post_init__(self):
        if len(self.sensors) != 1:
            raise ArchitectureError(
                f"cue {self.name!r} reads {len(self.sensors)} sensors; Section 5.1: "
                "'Each cue is dependent on a single sensor'"
            )

    def __call__(self, history: Sequence[float]):
        out = self.fn(history)
        if self.value_set and out not in self.value_set:
            raise ArchitectureError(
                f"cue {self.name!r} produced {out!r}, outside its declared value set"
            )
        return out


@dataclass(frozen=True)
class ContextVector:
    """One element of the context description: (symbolic value, certainty)."""

    symbol: str
    certainty: float

    def __post_init__(self):
        if not 0.0 <= self.certainty <= 1.0:
            raise ArchitectureError(
                "certainty outside [0, 1]; the paper gives no scale, this "
                "implementation assumes the unit interval"
            )


@dataclass
class ContextRule:
    """Explicit rule specification, the first of the two options in Section 5.3.

    `require` maps a cue name to the set of cue values that support the context.
    Certainty is the fraction of required cues that are satisfied -- an
    ASSUMPTION: the paper never says how the certainty number is computed.
    """

    symbol: str
    require: dict[str, set]

    def evaluate(self, cue_values: dict[str, object]) -> ContextVector:
        seen = [c for c in self.require if c in cue_values]
        if not seen:
            return ContextVector(self.symbol, 0.0)
        hit = sum(1 for c in seen if cue_values[c] in self.require[c])
        # Cues that are required but unavailable count as unsatisfied, so that a
        # missing sensor lowers certainty rather than silently helping.
        return ContextVector(self.symbol, hit / len(self.require))


@dataclass
class ContextLayer:
    rules: list[ContextRule] = field(default_factory=list)

    @property
    def symbols(self) -> list[str]:
        return [r.symbol for r in self.rules]

    def evaluate(self, cue_values: dict[str, object]) -> list[ContextVector]:
        return [r.evaluate(cue_values) for r in self.rules]


# --- Scripting layer -------------------------------------------------------

@dataclass
class Script:
    """One scripting-layer trigger (Section 5.1).

    kind: "enter" | "leave" | "while"
    threshold: certainty threshold (paper states no value)
    time_s: the "certain time" / "specified time interval" (paper states no value)
    """

    kind: str
    symbol: str
    threshold: float
    time_s: float
    action: str = "action"

    def __post_init__(self):
        if self.kind not in ("enter", "leave", "while"):
            raise ArchitectureError(f"unknown scripting semantics: {self.kind}")
        if self.time_s < 0:
            # Footnote to Section 5.1: "In case of context prediction the time
            # might be negative."  No prediction mechanism is described anywhere
            # in the paper, so negative times cannot be implemented from it.
            raise NotImplementedError(
                "negative time (context prediction, footnote to Section 5.1) is "
                "not specified in the paper and is not implemented"
            )


class ScriptingLayer:
    """Evaluates enter/leave/while triggers over a stream of context vectors."""

    def __init__(self, scripts: Iterable[Script]):
        self.scripts = list(scripts)
        self._above_since: dict[tuple[str, str], float | None] = {}
        self._below_since: dict[tuple[str, str], float | None] = {}
        self._in_context: dict[str, bool] = {}
        self._last_fire: dict[tuple[str, str], float] = {}

    def step(self, t_s: float, vectors: Sequence[ContextVector]) -> list[dict]:
        cert = {v.symbol: v.certainty for v in vectors}
        events: list[dict] = []
        for s in self.scripts:
            key = (s.kind, s.symbol)
            c = cert.get(s.symbol, 0.0)
            if s.kind == "enter":
                if c > s.threshold:
                    start = self._above_since.get(key) or t_s
                    self._above_since[key] = start
                    if t_s - start >= s.time_s and not self._in_context.get(s.symbol, False):
                        self._in_context[s.symbol] = True
                        events.append({"t_s": t_s, "kind": "enter", "context": s.symbol,
                                       "certainty": c, "action": s.action})
                else:
                    self._above_since[key] = None
            elif s.kind == "leave":
                if c < s.threshold:
                    start = self._below_since.get(key) or t_s
                    self._below_since[key] = start
                    if t_s - start >= s.time_s and self._in_context.get(s.symbol, False):
                        self._in_context[s.symbol] = False
                        events.append({"t_s": t_s, "kind": "leave", "context": s.symbol,
                                       "certainty": c, "action": s.action})
                else:
                    self._below_since[key] = None
            else:  # "while"
                if c > s.threshold:
                    last = self._last_fire.get(key)
                    if last is None or t_s - last >= s.time_s:
                        self._last_fire[key] = t_s
                        events.append({"t_s": t_s, "kind": "while", "context": s.symbol,
                                       "certainty": c, "action": s.action})
                else:
                    self._last_fire.pop(key, None)
        return events


def cue_layer_rejects_multi_sensor_cue() -> str:
    """Evidence for the Section 5.1 vs Section 6 tension, as an executable check.

    Section 6 claims several light sensors together yield e.g. "direction of
    light"; Section 5.1 requires a cue to depend on a single sensor.  Building
    that cue therefore fails inside the paper's own architecture.
    """
    try:
        Cue(name="direction of light", sensors=("light_left", "light_right"),
            fn=lambda h: "left", value_set=("left", "right"), window_s=1.0)
    except ArchitectureError as exc:
        return str(exc)
    return "no error: the single-sensor rule was not enforced"
