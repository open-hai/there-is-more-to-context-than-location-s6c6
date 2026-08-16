# There is more to context than location — reproduction audit

A reproducibility audit and best-effort reproduction of:

> Albrecht Schmidt, Michael Beigl, Hans-W. Gellersen. **"There is more to context than
> location."** *Computers & Graphics* 23(6), December 1999, 893–901.
> [doi:10.1016/S0097-8493(99)00120-X](https://doi.org/10.1016/S0097-8493(99)00120-X)

## What the paper is

A concept-and-prototype paper from TecO, University of Karlsruhe, arguing that mobile
computing's habit of equating context with location is too narrow. It contributes: a
*working model* of context (four rules and a two-branch, six-category feature space,
Section 3.1 and Fig. 1); a survey of cheap sensors and what context each can yield
(Section 4.1); two prototypes — a Palm Pilot with a light sensor driving its backlight, and a
Newton MessagePad with two mercury switches that rotates its interface (Section 4.2); and a
four-layer sensor-fusion architecture — sensors → cues → contexts → scripting — with an
"awareness device" built for experimentation under the ESPRIT project TEA (Section 5). It is
one of the most-cited papers in context-aware computing (≈1,300 citations).

## What this repository is

An audit that asks three questions and answers them in files:

- **What can be reproduced without human participants?** → [REPRODUCIBILITY.md](REPRODUCIBILITY.md),
  whose per-component table is the result: 15 inner-loop components, each marked verified,
  partial or blocked with its evidence or its specific blocker, and 6 outer-loop components
  that are never scored.
- **What did the authors leave unwritten?** → 18 hidden decisions (D1–D18), each with where
  the paper leaves it open, what this code assumed instead, and how sensitive the outcome is.
  They live in [`src/assumptions.py`](src/assumptions.py), so the code reads the same values
  the report describes.
- **How open is the science?** → the scorecard in [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
  and the full search log in [SOURCES.md](SOURCES.md). No code, no data, no preregistration,
  no supplement, and no open licence; the only artifact the authors published is a draft PDF.

The headline finding: the paper's architecture re-runs, but the paper reports **no
quantitative result of any kind**, so nothing can be checked against it — and its six
human-facing claims about usability, interaction and application benefit rest on **no
described study at all**. The outer loop here is absent, not merely unreproducible.

| File | What is in it |
|---|---|
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | The verdict, the per-component table, the mismatches, the inner/outer boundary and how it was drawn, the 18 hidden decisions, the open-science scorecard, and the exact commands with their real output |
| [SOURCES.md](SOURCES.md) | The paper's identity and every artifact search performed, with the HTTP result of each |
| [UNVERIFIED.md](UNVERIFIED.md) | Everything that could not be confirmed, each with its blocker |
| [verdict.json](verdict.json) | The same verdict, boundary table, mismatches, decisions, scorecard and release log, as data |
| [instrument.json](instrument.json) | The declared protocol (null, with the reason), the analysis entrypoint contract, and the servability assessment for every outer-loop component |
| [`src/`](src) | The inner loop, runnable |
| [`examples/sample_input.csv`](examples/sample_input.csv) | Twelve rows illustrating the input contract |

## The code

| Module | What it reproduces |
|---|---|
| `src/context_model.py` | Section 3.1 and Fig. 1: the four model rules and the feature space, as data plus a validator; audits whether the paper's own Table 1 contexts can be expressed in it |
| `src/architecture.py` | Section 5.1: the sensor, cue, context and scripting layers, with the paper's own constraints enforced (a cue may read one sensor; a negative scripting time is refused rather than invented) |
| `src/cues.py` | Section 5.3: the "brightness", "artificial light" and motion cues, reconstructed (D4–D8) |
| `src/contexts.py` | Table 1 as rules, plus the indoors/outdoors pair the experiment actually names; declares the two cues no described sensor can supply |
| `src/stream.py` | Sections 5.2–5.3: interlacing, and what the paper's "about 1100 Bytes … per second" allows per channel |
| `src/prototypes.py` | Section 4.2: the backlight controller and the two-switch orientation state machine, with their sensitivity to the assumptions |
| `src/assumptions.py` | D1–D18, the single source of every invented parameter |
| `src/synth.py` | Synthetic stand-in data, because none was released — labelled synthetic in every output |
| `src/analyze.py` | The entrypoint: runs the whole inner loop over a sensor CSV |
| `src/selftest.py` | 24 checks of things the paper actually states |

## How to run it

```bash
pip install -r requirements.txt

# 24 checks of the paper's stated structure, plus an end-to-end run
python src/selftest.py

# generate synthetic input (nothing of the paper's data was ever released) and analyse it
python src/synth.py --out /tmp/synth.csv
python src/analyze.py /tmp/synth.csv --outdir results

# the same pipeline below the flicker Nyquist rate, which is the D1/D5 sensitivity
python src/synth.py --out /tmp/synth_128.csv --rate 128
python src/analyze.py /tmp/synth_128.csv --outdir results_128
```

`src/analyze.py` accepts any CSV with the columns declared in `instrument.json`
(`t_s`, `light_adc`, `acc_x_adc`, `acc_y_adc` required; `temp_c`, `switch_a`, `switch_b`,
`situation` optional) and writes `cues.csv`, `contexts.csv`, `events.json`, `summary.json`,
`assumptions.json`, `report.md` and a Fig. 4-style plot into the output directory.

Real output of these commands is transcribed in
[REPRODUCIBILITY.md](REPRODUCIBILITY.md#what-was-actually-run).

## What this repository does not do

It never simulates the outer loop. No participant data are generated, no user study is
reconstructed, and no effect on people is estimated — for the plain reason that the paper
describes no such study to reconstruct. Any number produced by `src/` is a number about the
synthetic input, and is labelled as such wherever it appears.
