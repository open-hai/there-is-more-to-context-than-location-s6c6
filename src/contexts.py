"""Table 1 as executable rules, plus the Section 5.1 context layer wired up.

Table 1 of the paper:

    Context        | Cues
    ---------------+------------------------------------------------------------
    In the office  | Artificial light, stationary or walking, room temperature, dry
    Jogging        | Natural light (cloudy or sunny), walking or running,
                   | dry or raining, high pulse

The rule *form* (conjunction? weights? how certainty is computed?) is not in the
paper; see D9 and D18.  Two of Table 1's cues -- wetness ("dry", "dry or
raining") and "high pulse" -- need sensors that the paper never says the awareness
device has, so they are declared here as unavailable cues rather than invented.
"""

from __future__ import annotations

from architecture import ContextLayer, ContextRule

# Cues Table 1 needs but which no sensor described in the paper can supply.
UNAVAILABLE_CUES = {
    "wetness": "Table 1 needs 'dry' / 'dry or raining'; no moisture or rain sensor "
               "is named anywhere in the paper",
    "pulse": "Table 1 needs 'high pulse'; Section 4.1 discusses bio-sensors in "
             "general but the awareness device of Section 5.2 is never said to have one",
}

RULES = [
    ContextRule(
        symbol="In the office",
        require={
            "light type": {"artificial"},
            "motion": {"stationary", "walking"},
            "temperature": {"room temperature"},
            "wetness": {"dry"},
        },
    ),
    ContextRule(
        symbol="Jogging",
        require={
            "light type": {"natural"},
            "motion": {"walking", "running"},
            "wetness": {"dry", "raining"},
            "pulse": {"high"},
        },
    ),
]

# Not from Table 1: Section 5.3 says raw data were collected "in different
# situations, for instance 'indoors' and 'outdoors'", which is the only situation
# pair the paper actually names for the experiment.  These two rules use only cues
# the described device can produce.
INDOOR_OUTDOOR_RULES = [
    ContextRule(symbol="indoors", require={"light type": {"artificial"}}),
    ContextRule(symbol="outdoors", require={"light type": {"natural"},
                                            "brightness": {"bright", "dim"}}),
]


def table1_layer() -> ContextLayer:
    return ContextLayer(rules=list(RULES))


def indoor_outdoor_layer() -> ContextLayer:
    return ContextLayer(rules=list(INDOOR_OUTDOOR_RULES))


def max_attainable_certainty(rule: ContextRule, available_cues: set[str]) -> float:
    """Ceiling on a rule's certainty when some required cues cannot be produced."""
    return sum(1 for c in rule.require if c in available_cues) / len(rule.require)
