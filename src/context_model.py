"""Working model for context (Schmidt, Beigl & Gellersen 1999, Section 3.1 and Fig. 1).

This module encodes, as data plus a validator, exactly what the paper states:

Section 3.1, the four rules of the working model:
  1. "A context describes a situation and the environment a device or user is in."
  2. "A context is identified by a unique name."
  3. "For each context a set of features is relevant."
  4. "For each relevant feature a range of values is determined (implicit or
     explicit) by the context."

Fig. 1 / Section 3.1 prose, the feature space: two top-level branches (human
factors, physical environment), three categories each, with the example features
the prose lists for every category.  The prose ends every leaf list with "...",
so the leaf lists below are the paper's examples and *not* a closed enumeration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Fig. 1 / Section 3.1: the feature space -------------------------------
# Values are the example features the paper's prose gives for each category.
# `open_ended=True` records that the paper writes "..." after the examples.
FEATURE_SPACE: dict[str, dict[str, list[str]]] = {
    "human factors": {
        "user": ["knowledge of habits", "emotional state", "biophysiological conditions"],
        "social environment": ["co-location of others", "social interaction", "group dynamics"],
        "task": ["spontaneous activity", "engaged tasks", "general goals"],
    },
    "physical environment": {
        "location": ["absolute position", "relative position", "co-location"],
        "infrastructure": [
            "surrounding resources for computation",
            "surrounding resources for communication",
            "surrounding resources for task performance",
        ],
        "physical conditions": ["noise", "light", "pressure"],
    },
}

# Section 3.1: "Additional context is provided by history, that is by changes in
# the feature space over time."  History is a modifier over the space above, not
# a seventh category; the paper gives it no features of its own.
HISTORY_IS_ADDITIONAL_CONTEXT = True

MODEL_RULES = [
    "a context describes a situation and the environment a device or user is in",
    "a context is identified by a unique name",
    "for each context a set of features is relevant",
    "for each relevant feature a range of values is determined (implicit or explicit)",
]


@dataclass(frozen=True)
class Feature:
    """A leaf of the feature space, plus the value range rule 4 demands."""

    name: str
    branch: str
    category: str
    value_range: tuple | None = None  # None == the paper determines no range

    @property
    def range_determined(self) -> bool:
        return self.value_range is not None


@dataclass
class Context:
    """A context in the sense of the four rules of Section 3.1."""

    name: str
    relevant_features: list[Feature] = field(default_factory=list)
    citation: str = ""

    def violations(self) -> list[str]:
        """Which of the four rules this context cannot satisfy as written."""
        out = []
        if not self.name:
            out.append("rule 2: no unique name")
        if not self.relevant_features:
            out.append("rule 3: no set of relevant features")
        undetermined = [f.name for f in self.relevant_features if not f.range_determined]
        if undetermined:
            out.append(
                "rule 4: no value range determined for " + ", ".join(sorted(undetermined))
            )
        return out


def leaves() -> list[Feature]:
    return [
        Feature(name=feat, branch=branch, category=cat)
        for branch, cats in FEATURE_SPACE.items()
        for cat, feats in cats.items()
        for feat in feats
    ]


def find_leaf(name: str) -> Feature | None:
    for leaf in leaves():
        if leaf.name == name:
            return leaf
    return None


def validate_feature_space() -> dict:
    """Structural checks against Fig. 1 as the prose describes it."""
    branches = list(FEATURE_SPACE)
    cats = {b: list(FEATURE_SPACE[b]) for b in branches}
    n_cat = sum(len(v) for v in cats.values())
    dupes = [f.name for f in leaves() if sum(1 for g in leaves() if g.name == f.name) > 1]
    return {
        "branches": branches,
        "branches_ok": len(branches) == 2,
        "categories_per_branch": {b: len(v) for b, v in cats.items()},
        "six_categories_ok": n_cat == 6 and all(len(v) == 3 for v in cats.values()),
        "n_example_features": len(leaves()),
        "duplicate_feature_names": sorted(set(dupes)),
        "history_modelled": HISTORY_IS_ADDITIONAL_CONTEXT,
        "n_model_rules": len(MODEL_RULES),
    }


# --- Table 1: the paper's own two example contexts -------------------------
# Table 1 describes contexts in terms of *cues* (Section 5), not in terms of the
# Fig. 1 features.  The strings on the right are the paper's cue names verbatim.
TABLE_1 = {
    "In the office": ["artificial light", "stationary or walking", "room temperature", "dry"],
    "Jogging": [
        "natural light (cloudy or sunny)",
        "walking or running",
        "dry or raining",
        "high pulse",
    ],
}

# Where each Table 1 cue would have to live in the Fig. 1 feature space for the
# Section 3.1 model to be able to express these two contexts.  `None` means no
# leaf and no category of Fig. 1 covers it.
CUE_TO_FEATURE_SPACE = {
    "artificial light": ("physical environment", "physical conditions", "light"),
    "natural light (cloudy or sunny)": ("physical environment", "physical conditions", "light"),
    "room temperature": ("physical environment", "physical conditions", None),
    "dry": ("physical environment", "physical conditions", None),
    "dry or raining": ("physical environment", "physical conditions", None),
    "stationary or walking": (None, None, None),
    "walking or running": (None, None, None),
    "high pulse": ("human factors", "user", "biophysiological conditions"),
}


def audit_table_1() -> dict:
    """Can the Section 3.1 model express the paper's own Table 1 contexts?"""
    unhoused, uncovered_leaf = [], []
    for cues in TABLE_1.values():
        for cue in cues:
            branch, cat, leaf = CUE_TO_FEATURE_SPACE[cue]
            if branch is None:
                unhoused.append(cue)
            elif leaf is None or find_leaf(leaf) is None:
                uncovered_leaf.append(cue)
    contexts = [
        Context(name=name, relevant_features=[], citation="Table 1")
        for name in TABLE_1
    ]
    return {
        "contexts": list(TABLE_1),
        "cues_total": sum(len(v) for v in TABLE_1.values()),
        "cues_with_no_category_in_fig1": sorted(set(unhoused)),
        "cues_with_category_but_no_listed_feature": sorted(set(uncovered_leaf)),
        "rule_violations": {c.name: c.violations() for c in contexts},
    }


if __name__ == "__main__":
    import json

    print(json.dumps({"feature_space": validate_feature_space(),
                      "table_1": audit_table_1()}, indent=2))
