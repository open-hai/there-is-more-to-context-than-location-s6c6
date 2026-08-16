"""Smoke test: build the paper's pipeline, run it, and check what the paper asserts.

    python src/selftest.py

The assertions are only of things the paper actually states (the structure of the
Fig. 1 feature space, the single-sensor rule for cues, the enter/leave/while
semantics, the ordering of the motion cues, the separation of "artificial light"
from daylight).  Nothing here checks a number against the paper, because the paper
reports none.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import context_model  # noqa: E402
import contexts as C  # noqa: E402
import cues as Q  # noqa: E402
import stream  # noqa: E402
import synth  # noqa: E402
from architecture import (ArchitectureError, ContextVector, Cue, Script,  # noqa: E402
                          ScriptingLayer)
from prototypes import OrientationDecoder, n_consistent_mappings  # noqa: E402

PASS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if not cond:
        raise AssertionError(f"FAILED: {name} {detail}")
    PASS.append(f"ok   {name} {detail}".rstrip())


def main() -> int:
    # --- Section 3.1 / Fig. 1 ------------------------------------------------
    v = context_model.validate_feature_space()
    check("Fig. 1 has two branches", v["branches_ok"], str(v["branches"]))
    check("Fig. 1 has six categories of three example features", v["six_categories_ok"])
    check("Section 3.1 states four model rules", v["n_model_rules"] == 4)
    a = context_model.audit_table_1()
    check("Table 1 motion cues have no category in Fig. 1",
          a["cues_with_no_category_in_fig1"] == ["stationary or walking", "walking or running"],
          str(a["cues_with_no_category_in_fig1"]))

    # --- Section 5.1 rules --------------------------------------------------
    try:
        Cue("two sensors", ("a", "b"), lambda h: 1, (1,), 1.0)
        raise AssertionError("FAILED: the single-sensor rule was not enforced")
    except ArchitectureError:
        check("cue layer enforces 'each cue is dependent on a single sensor'", True)
    try:
        Script("enter", "x", 0.7, -1.0)
        raise AssertionError("FAILED: negative time silently accepted")
    except NotImplementedError:
        check("negative scripting time (prediction footnote) is refused, not faked", True)
    try:
        ContextVector("x", 1.4)
        raise AssertionError("FAILED: certainty outside [0,1] accepted")
    except ArchitectureError:
        check("context certainty is constrained to the assumed [0,1] scale", True)

    sl = ScriptingLayer([Script("enter", "indoors", 0.7, 2.0),
                         Script("leave", "indoors", 0.5, 2.0)])
    fired = []
    for t in range(0, 12):
        c = 1.0 if t < 6 else 0.0
        fired += sl.step(float(t), [ContextVector("indoors", c)])
    kinds = [e["kind"] for e in fired]
    check("enter fires once after the dwell time, then leave fires once",
          kinds == ["enter", "leave"], str([(e["kind"], e["t_s"]) for e in fired]))

    # --- Section 5.3 byte budget -------------------------------------------
    check("1100 B/s over 4 one-byte channels is 275 Hz each",
          abs(stream.per_channel_rate(4) - 275.0) < 1e-9)
    check("at most 5 equally interlaced one-byte channels resolve 100 Hz flicker",
          stream.max_channels_for_flicker() == 5,
          f"max={stream.max_channels_for_flicker()}")
    ch = {"light": np.arange(10) % 256, "temp": np.full(10, 21)}
    back = stream.deinterlace(stream.interlace(ch, ["light", "temp"]), ["light", "temp"])
    check("interlace/deinterlace round-trips", np.allclose(back["light"], ch["light"]))

    # --- cue layer on synthetic data ---------------------------------------
    df = synth.generate()
    fs = 1.0 / float(np.median(np.diff(df.t_s.values)))
    check("synthetic stream is generated at the D1 rate", abs(fs - 275.0) < 1.0, f"{fs:.1f} Hz")
    per = {}
    for label, grp in df.groupby("situation"):
        seg = grp.light_adc.values[: int(fs)]
        per[label] = Q.light_type(seg, fs, 50.0)
    check("indoor windows read as artificial light",
          all(v == "artificial" for k, v in per.items() if k.startswith("indoors")), str(per))
    check("outdoor windows read as natural light",
          all(v == "natural" for k, v in per.items() if k.startswith("outdoors")), str(per))

    sds = {}
    for label, grp in df.groupby("situation"):
        acc = np.column_stack([grp.acc_x_adc.values, grp.acc_y_adc.values])[: int(fs)]
        sds[label] = Q.motion(acc)
    check("motion cue orders desk < walking < running",
          sds["indoors-office-desk"] == "stationary"
          and sds["outdoors-walking"] == "walking"
          and sds["outdoors-running"] == "running", str(sds))

    # --- Table 1 reachability ----------------------------------------------
    avail = {"brightness", "light type", "motion", "temperature"}
    ceil = {r.symbol: C.max_attainable_certainty(r, avail) for r in C.RULES}
    check("'Jogging' cannot exceed certainty 0.5 with the sensors the paper describes",
          abs(ceil["Jogging"] - 0.5) < 1e-9, str(ceil))

    # --- Section 4.2 orientation -------------------------------------------
    check("two switches leave all 24 state-to-orientation mappings open",
          n_consistent_mappings() == 24)
    dec = OrientationDecoder()
    t = np.arange(0, 2.0, 0.01)
    a = (t > 1.0).astype(int)
    b = np.ones_like(a)
    out = dec.run(t, a, b)
    check("orientation only changes after the assumed debounce",
          out[len(out) // 2 - 1] != out[-1], f"{out[0]} -> {out[-1]}")

    # --- end-to-end ---------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        csv = os.path.join(td, "s.csv")
        df.to_csv(csv, index=False)
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "analyze.py"),
                            csv, "--outdir", os.path.join(td, "out")],
                           capture_output=True, text=True)
        check("analyze.py runs to completion", r.returncode == 0, r.stderr[-300:])
        for f in ["cues.csv", "contexts.csv", "events.json", "summary.json", "report.md"]:
            check(f"analyze.py wrote {f}", os.path.exists(os.path.join(td, "out", f)))

    print("\n".join(PASS))
    print(f"\n{len(PASS)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
