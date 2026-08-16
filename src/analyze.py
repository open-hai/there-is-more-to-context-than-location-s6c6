"""Run the paper's inner loop end to end over a sensor CSV.

    python src/analyze.py <input.csv> [--outdir results]

What it does, in the order the paper builds it:

  Section 3.1 / Fig. 1  validate the working model and check whether the paper's
                        own Table 1 contexts can be expressed in it
  Section 5.2 / 5.3     the 1100 B/s byte budget and what per-channel rate it buys
  Section 5.1 sensors   declare the channels as sensors with value sets
  Section 5.1 cues      brightness, artificial light, motion, temperature
  Section 5.1 contexts  Table 1 rules and the indoors/outdoors pair of Section 5.3
  Section 5.1 scripting enter / leave / while triggers over the certainty stream
  Section 4.2           the light-sensitive display and orientation-aware UI logic

Every free parameter comes from src/assumptions.py and is written to
results/assumptions.json with the run, so no number here can be mistaken for one
of the paper's.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import assumptions as A  # noqa: E402
import context_model  # noqa: E402
import contexts as C  # noqa: E402
import cues as Q  # noqa: E402
import stream  # noqa: E402
from architecture import (Cue, Script, ScriptingLayer, Sensor,  # noqa: E402
                          cue_layer_rejects_multi_sensor_cue)
from prototypes import (BacklightController, OrientationDecoder,  # noqa: E402
                        backlight_sensitivity, n_consistent_mappings)

REQUIRED_COLUMNS = ["t_s", "light_adc", "acc_x_adc", "acc_y_adc"]


def declare_sensors(rate_hz: float) -> list[Sensor]:
    """Section 5.1: sensors are time-dependent functions with declared value sets.

    The accelerometer is one *vector*-valued sensor (Section 5.1 explicitly allows
    a sensor to return a vector), which is why a two-axis motion cue does not
    breach the single-sensor rule -- whereas two separate light sensors would.
    """
    return [
        Sensor("light", "physical", "scalar", "0..255 ADC counts", rate_hz),
        Sensor("accelerometer", "physical", "vector", "(x, y) in 0..255 ADC counts", rate_hz),
        Sensor("temperature", "physical", "scalar", "degrees Celsius", rate_hz),
        Sensor("tilt switches", "physical", "symbol", "{(0,0),(0,1),(1,0),(1,1)}", rate_hz),
    ]


def build_cues(rate_hz: float, mains_hz: float) -> list[Cue]:
    w = A.value("D7", "window_s")
    return [
        Cue("brightness", ("light",), Q.brightness, Q.BRIGHTNESS_VALUES, w),
        Cue("light type", ("light",),
            lambda h: Q.light_type(np.asarray(h), rate_hz, mains_hz),
            Q.LIGHT_TYPE_VALUES, w),
        Cue("motion", ("accelerometer",), Q.motion, Q.MOTION_VALUES, w),
        Cue("temperature", ("temperature",), Q.temperature, Q.TEMP_VALUES, w),
    ]


def run(input_csv: str, outdir: str, rate_override: float | None = None) -> dict:
    os.makedirs(outdir, exist_ok=True)
    df = pd.read_csv(input_csv)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"input {input_csv} is missing required columns: {missing}")

    dt = float(np.median(np.diff(df.t_s.values)))
    rate_hz = rate_override or (1.0 / dt)
    mains_hz = A.value("D6", "mains_hz")
    window_s = A.value("D7", "window_s")
    n_win = int(round(window_s * rate_hz))

    sensors = declare_sensors(rate_hz)
    cue_defs = {c.name: c for c in build_cues(rate_hz, mains_hz)}

    # ---- cue layer ----------------------------------------------------------
    cue_rows = []
    for start in range(0, len(df) - n_win + 1, n_win):
        seg = df.iloc[start:start + n_win]
        acc = np.column_stack([seg.acc_x_adc.values, seg.acc_y_adc.values])
        vals = {
            "brightness": cue_defs["brightness"](seg.light_adc.values),
            "light type": cue_defs["light type"](seg.light_adc.values),
            "motion": cue_defs["motion"](acc),
        }
        if "temp_c" in df.columns:
            vals["temperature"] = cue_defs["temperature"](seg.temp_c.values)
        cue_rows.append({
            "t_s": round(float(seg.t_s.iloc[0]), 3),
            "situation_label": (seg.situation.iloc[0] if "situation" in df.columns else ""),
            **vals,
            "light_mean_adc": round(float(seg.light_adc.mean()), 2),
            "flicker_prominence": round(
                Q.flicker_prominence(seg.light_adc.values, rate_hz, mains_hz), 3),
        })
    cue_df = pd.DataFrame(cue_rows)
    cue_df.to_csv(os.path.join(outdir, "cues.csv"), index=False)

    available_cues = {c for c in ("brightness", "light type", "motion", "temperature")
                      if c in cue_df.columns}

    # ---- context layer + scripting layer -----------------------------------
    layers = {"table1": C.table1_layer(), "indoor_outdoor": C.indoor_outdoor_layer()}
    scripts = []
    for sym in layers["indoor_outdoor"].symbols:
        scripts += [
            Script("enter", sym, A.value("D10", "enter"), A.value("D10", "dwell_s"),
                   f"on entering {sym}"),
            Script("leave", sym, A.value("D10", "leave"), A.value("D10", "dwell_s"),
                   f"on leaving {sym}"),
            Script("while", sym, A.value("D10", "enter"), A.value("D10", "while_every_s"),
                   f"while in {sym}"),
        ]
    scripting = ScriptingLayer(scripts)

    ctx_rows, events = [], []
    for _, r in cue_df.iterrows():
        cue_values = {k: r[k] for k in available_cues}
        row = {"t_s": r.t_s, "situation_label": r.situation_label}
        for lname, layer in layers.items():
            for v in layer.evaluate(cue_values):
                row[f"{lname}:{v.symbol}"] = round(v.certainty, 3)
        ctx_rows.append(row)
        events += scripting.step(float(r.t_s),
                                 layers["indoor_outdoor"].evaluate(cue_values))
    ctx_df = pd.DataFrame(ctx_rows)
    ctx_df.to_csv(os.path.join(outdir, "contexts.csv"), index=False)
    with open(os.path.join(outdir, "events.json"), "w") as fh:
        json.dump(events, fh, indent=2)

    # ---- Section 4.2 prototypes -------------------------------------------
    t = df.t_s.values
    backlight = BacklightController().run(t, df.light_adc.values)
    orientation = None
    if {"switch_a", "switch_b"}.issubset(df.columns):
        dec = OrientationDecoder()
        states = dec.run(t, df.switch_a.values, df.switch_b.values)
        rotations = sum(1 for i in range(1, len(states)) if states[i] != states[i - 1])
        orientation = {
            "n_states_from_two_switches": 4,
            "n_bijections_left_open_by_the_text": n_consistent_mappings(),
            "rotations_observed": rotations,
            "final_state": states[-1],
        }

    # ---- summary ------------------------------------------------------------
    per_situation = {}
    if "situation" in df.columns:
        for label, grp in cue_df.groupby("situation_label"):
            per_situation[label] = {
                "windows": int(len(grp)),
                "light type": grp["light type"].value_counts().to_dict(),
                "brightness": grp["brightness"].value_counts().to_dict(),
                "motion": grp["motion"].value_counts().to_dict(),
                "mean_flicker_prominence": round(float(grp.flicker_prominence.mean()), 2),
            }

    summary = {
        "input": os.path.abspath(input_csv),
        "n_samples": int(len(df)),
        "duration_s": round(float(t[-1] - t[0]), 3),
        "sample_rate_hz": round(rate_hz, 3),
        "window_s": window_s,
        "n_windows": int(len(cue_df)),
        "sensors_declared": [s.name for s in sensors],
        "model_section_3_1": context_model.validate_feature_space(),
        "table_1_in_the_model": context_model.audit_table_1(),
        "byte_budget_section_5_3": {
            "total_bytes_per_s": stream.TOTAL_BYTES_PER_S,
            "channels_in_this_input": 4,
            "equal_share_rate_hz": round(stream.per_channel_rate(4), 1),
            "rate_needed_to_resolve_flicker_hz": 4.0 * mains_hz,
            "max_channels_resolving_flicker": stream.max_channels_for_flicker(),
            "flicker_resolvable_at_this_rate": Q.flicker_observable(rate_hz, mains_hz),
            "cue_path_used": ("flicker band (frequency domain)"
                              if Q.flicker_observable(rate_hz, mains_hz)
                              else "aliased-variance fallback"),
            "table": stream.budget_table(),
        },
        "single_sensor_rule_check": cue_layer_rejects_multi_sensor_cue(),
        "table1_certainty_ceilings": {
            r.symbol: round(C.max_attainable_certainty(r, available_cues), 3)
            for r in C.RULES
        },
        "cues_table1_cannot_supply": {k: v for k, v in C.UNAVAILABLE_CUES.items()},
        "per_situation_cue_counts": per_situation,
        "scripting_events": {"n": len(events), "first": events[:4]},
        "backlight": {
            "fraction_of_time_on": round(float(np.mean(backlight)), 3),
            "switches": int(np.sum(backlight[1:] != backlight[:-1])),
            "sensitivity_to_D13": backlight_sensitivity(t, df.light_adc.values),
        },
        "orientation": orientation,
        "assumptions_used": A.as_records(),
    }
    with open(os.path.join(outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2, default=str)
    with open(os.path.join(outdir, "assumptions.json"), "w") as fh:
        json.dump(A.as_records(), fh, indent=2)

    _write_figure(df, outdir)
    _write_report(summary, outdir)
    return summary


def _write_figure(df: pd.DataFrame, outdir: str) -> None:
    """A Fig. 4-style plot of the light channel. Synthetic input, not the paper's data."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print(f"[figure skipped: {exc}]")
        return
    fig, ax = plt.subplots(figsize=(8, 3.2))
    if "situation" in df.columns:
        for label, grp in df.groupby("situation", sort=False):
            ax.plot(grp.t_s, grp.light_adc, lw=0.7, label=label)
    else:
        ax.plot(df.t_s, df.light_adc, lw=0.7)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("light sensor (ADC counts)")
    ax.set_title("Fig. 4-style light sensor trace - SYNTHETIC data, not the paper's")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "fig4_style_light.png"), dpi=130)
    plt.close(fig)


def _write_report(summary: dict, outdir: str) -> None:
    b = summary["byte_budget_section_5_3"]
    lines = [
        "# Inner-loop run report",
        "",
        f"Input: `{summary['input']}` ({summary['n_samples']} samples, "
        f"{summary['duration_s']} s at {summary['sample_rate_hz']} Hz, "
        f"{summary['n_windows']} cue windows of {summary['window_s']} s).",
        "",
        "## Section 3.1 model",
        f"- two branches: {summary['model_section_3_1']['branches_ok']}, "
        f"six categories of three example features: "
        f"{summary['model_section_3_1']['six_categories_ok']}",
        f"- Table 1 cues with no category anywhere in Fig. 1: "
        f"{summary['table_1_in_the_model']['cues_with_no_category_in_fig1']}",
        "",
        "## Section 5.3 byte budget",
        f"- 1100 B/s over 4 interlaced channels = {b['equal_share_rate_hz']} Hz per channel; "
        f"resolving 100 Hz flicker needs > {b['rate_needed_to_resolve_flicker_hz']} Hz, "
        f"so at most {b['max_channels_resolving_flicker']} channel(s) can do it.",
        f"- cue path used on this input: {b['cue_path_used']}.",
        "",
        "## Cue layer per labelled situation",
    ]
    for label, s in summary["per_situation_cue_counts"].items():
        lines.append(f"- **{label}**: {s['windows']} windows, light type "
                     f"{s['light type']}, brightness {s['brightness']}, motion {s['motion']}")
    lines += [
        "",
        "## Table 1 rules with only the sensors the paper describes",
    ]
    for sym, ceil in summary["table1_certainty_ceilings"].items():
        lines.append(f"- `{sym}`: certainty can never exceed {ceil} "
                     f"(missing cues: {list(summary['cues_table1_cannot_supply'])})")
    lines += [
        "",
        "## Scripting layer",
        f"- {summary['scripting_events']['n']} events fired with the D10 thresholds.",
        "",
        "## Section 4.2 prototypes",
        f"- backlight on {summary['backlight']['fraction_of_time_on'] * 100:.1f}% of the "
        f"trace, {summary['backlight']['switches']} switch(es) with the assumed D13 "
        f"setting; over the five settings tried, switch counts "
        f"{[r['switches'] for r in summary['backlight']['sensitivity_to_D13']]} and "
        f"duty cycles "
        f"{[r['fraction_of_time_on'] for r in summary['backlight']['sensitivity_to_D13']]}.",
    ]
    if summary["orientation"]:
        o = summary["orientation"]
        lines.append(f"- orientation: two switches give {o['n_states_from_two_switches']} "
                     f"states; the paper's prose leaves all "
                     f"{o['n_bijections_left_open_by_the_text']} state-to-orientation "
                     f"mappings open; {o['rotations_observed']} rotations on this input.")
    lines += ["", "All numbers above describe the input file, which is synthetic.",
              "The paper reports no quantitative result to compare them with."]
    with open(os.path.join(outdir, "report.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="sensor CSV (see instrument.json for the columns)")
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--rate", type=float, default=None,
                    help="override the sample rate in Hz instead of inferring it from t_s")
    a = ap.parse_args()
    s = run(a.input, a.outdir, a.rate)
    b = s["byte_budget_section_5_3"]
    print(f"samples={s['n_samples']} rate={s['sample_rate_hz']}Hz windows={s['n_windows']}")
    print(f"model Fig.1 structure ok: branches={s['model_section_3_1']['branches_ok']} "
          f"six_categories={s['model_section_3_1']['six_categories_ok']}")
    print(f"Table 1 cues unhoused by Fig. 1: "
          f"{s['table_1_in_the_model']['cues_with_no_category_in_fig1']}")
    print(f"byte budget: the paper's 1100 B/s over 4 one-byte channels allows "
          f"{b['equal_share_rate_hz']} Hz each (at most "
          f"{b['max_channels_resolving_flicker']} channels stay above the "
          f"{b['rate_needed_to_resolve_flicker_hz']} Hz needed for 100 Hz flicker); "
          f"this input runs at {s['sample_rate_hz']} Hz, cue path: {b['cue_path_used']}")
    print(f"single-sensor rule: {s['single_sensor_rule_check']}")
    print(f"Table 1 certainty ceilings with the paper's sensors: "
          f"{s['table1_certainty_ceilings']}")
    for label, st in s["per_situation_cue_counts"].items():
        print(f"  {label:24s} light={st['light type']} motion={st['motion']}")
    print(f"scripting events: {s['scripting_events']['n']}")
    print(f"backlight: on {s['backlight']['fraction_of_time_on']:.3f} of the trace, "
          f"{s['backlight']['switches']} switches (over five D13 settings: switches "
          f"{[r['switches'] for r in s['backlight']['sensitivity_to_D13']]}, duty "
          f"{[r['fraction_of_time_on'] for r in s['backlight']['sensitivity_to_D13']]})")
    if s["orientation"]:
        print(f"orientation: {s['orientation']['rotations_observed']} rotations, "
              f"{s['orientation']['n_bijections_left_open_by_the_text']} mappings left open "
              f"by the text")
    print(f"wrote {a.outdir}/: cues.csv contexts.csv events.json summary.json "
          f"assumptions.json report.md fig4_style_light.png")


if __name__ == "__main__":
    main()
