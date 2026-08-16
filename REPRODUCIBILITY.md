# Reproducibility verdict

**Paper.** Albrecht Schmidt, Michael Beigl, Hans-W. Gellersen, "There is more to context
than location", *Computers & Graphics* 23(6), December 1999, 893–901.
DOI [10.1016/S0097-8493(99)00120-X](https://doi.org/10.1016/S0097-8493(99)00120-X).
Text audited: the authors' own draft PDF (see [SOURCES.md](SOURCES.md)).

**Verdict: partial.** The paper's conceptual and architectural machinery re-runs: the
working model of context (Section 3.1, Fig. 1), the four-layer sensor→cue→context→scripting
architecture (Section 5.1) and the scripting semantics are specified tightly enough to
rebuild, and they are rebuilt and executed in `src/`. Everything that touches measurement
is blocked or partial, for one reason: **the paper reports no quantitative result at all.**
Its "experiment" (Section 5.3) is one unlabelled figure of light-sensor traces, plus an
illustrative table of cue-to-context descriptions; no accuracy, no error rate, no sample
count, no duration, no units, no sensor list, no thresholds, and no data or code were ever
released. So a reimplementation can be *built* from the paper but cannot be *checked*
against it.

The paper's human-facing claims — that the light-sensitive display "substantially add[s] to
usability", that orientation awareness "can be used very effectively for improvement of
human–computer interaction", that OS-provided rotation "is hardly used, if at all" — rest
on no described study. They are outer-loop rows below and are not scored, because there is
nothing to score: no participants, no task, no measure, and no procedure appear anywhere in
the paper.

## Per-component reproduction table

`inner` = mechanically re-runnable; `outer` = needs human participants, never attempted and
never scored. Citations are to the audited draft.

### Inner loop

| # | Component / claim | Outcome | Evidence, or the specific blocker | Citation |
|---|---|---|---|---|
| I1 | The working model of context: four stated rules, and a feature space with two branches and three categories each | **verified** | `src/context_model.py` encodes the four rules and all six categories with the 18 example features the prose lists; `python src/selftest.py` asserts `branches=2`, `six categories of three`, `four rules` — all pass | Section 3.1, Fig. 1 |
| I2 | That the model can actually express a context, i.e. rule 3 (a set of relevant features) plus rule 4 (a determined range of values for each) | **partial** | The structure instantiates, but the paper determines a value range for no feature anywhere, so rule 4 cannot be satisfied for any context; and 2 of the 8 cues in the paper's own Table 1 (device motion: "stationary or walking", "walking or running") have no category at all in Fig. 1, while "room temperature" and "dry" fall in a category whose listed features are only noise, light and pressure. Printed by `src/analyze.py`. See mismatch 4 | Section 3.1 rules 3–4; Fig. 1; Table 1 |
| I3 | Table 1: two contexts described in terms of cues ("In the office", "Jogging") | **partial** | Encoded as rules in `src/contexts.py` and evaluated over 44 cue windows. But the rule form, the weights and the certainty arithmetic are unstated (D9, D18), and two required cues — wetness and pulse — have no sensor named anywhere in the paper, which caps attainable certainty at 0.75 for "In the office" and 0.50 for "Jogging". With a threshold above 0.5 (the paper gives no threshold at all) "Jogging" can never be entered | Table 1; Sections 5.1, 5.3 |
| I4 | The four-layer architecture: sensors as time-dependent functions with declared value sets, cues over a single sensor, contexts as (symbol, certainty) vectors | **verified** | `src/architecture.py` implements all four layers and enforces the stated constraints (a two-sensor cue is refused; a certainty outside the assumed [0,1] scale is refused). Executed over the recorded run: 4 sensors → 4 cues → 2 context layers → 44 context rows. See mismatch 3 | Section 5.1 |
| I5 | Scripting semantics: entering, leaving, and while-in a context, each with a certainty threshold and a time | **verified** | `src/architecture.py::ScriptingLayer`; the self-test shows exactly one `enter` after the dwell time and one `leave`; the recorded run fires 12 events. Threshold and time *values* are assumed (D10, D11) — the semantics, which is what the paper states, reproduce | Section 5.1 |
| I6 | "In case of context prediction the time might be negative" | **blocked** | No prediction mechanism is described anywhere in the paper — no model, no horizon, no input. The scripting layer raises `NotImplementedError` on a negative time rather than inventing one | Footnote to Section 5.1 |
| I7 | The awareness device: sensors → A/D converter → microcontroller → serial line to a host computer | **blocked** | Fig. 3 is a block diagram. No sensor list ("a greater number of possibly relevant sensors"), no part numbers, no component values, no firmware, no sampling schedule, no A/D resolution. Nothing to build and nothing to run. This is an inner-loop blocker of documentation, not an outer-loop boundary: rebuilding hardware needs no participants | Section 5.2, Fig. 3 |
| I8 | "The awareness device provides about 1100 Bytes of sensor readings per second… transmitted interlaced" | **partial** | The arithmetic reproduces and is informative (`src/stream.py`): at one byte per sample, 1100 B/s gives 275 Hz per channel for four channels, and **at most 5 equally interlaced channels** stay above the 200 Hz needed to resolve 100 Hz mains flicker. The interlacing itself (channel order, word width, sync marker, per-channel priority) is unspecified (D3), so my decoder round-trips my own stream and can never be validated against the device | Sections 5.2–5.3 |
| I9 | The "brightness" cue, obtained from light-sensor readings by "simple statistical functions" | **partial** | Implemented as a windowed mean with symbol boundaries (D4) and run over 44 windows: dark in the synthetic corridor, dim at the desk, bright outdoors. The paper names neither the function, nor the thresholds, nor the units, nor the ADC scale, and released no data to check against | Section 5.3 |
| I10 | The "artificial light" cue, likewise from simple statistical functions | **partial** | Implemented as mains-flicker prominence with an aliased-variance fallback (D5, D6); it separates the synthetic indoor and outdoor traces at both 275 Hz and 128 Hz. But the method is entirely mine: the paper names the cue and stops. See mismatch 2 | Section 5.3 |
| I11 | Accelerometer cues: "stationary", "walking", and so on | **partial** | Implemented as within-window dispersion of the accelerometer magnitude with thresholds (D8); the ordering stationary < walking < running holds on synthetic data. The paper gives no feature, no threshold, no axis convention and no sensor range | Section 5.3 |
| I12 | Fig. 4 and its claim: light-sensor data from two different contexts, which "can be easily and reliably distinguished" | **blocked** | The data were never released (every location searched is listed in [SOURCES.md](SOURCES.md) — 34 URLs across publisher records, the authors' pages and five repositories); the figure carries no units, duration or sample count; and the text reports no separability measure, accuracy, error rate or *n*. There is no number in the paper to reproduce, so a synthetic separation demonstrates only my generator. See mismatch 1 | Fig. 4, Section 5.3 |
| I13 | The light-sensitive display: a light sensor in a Palm Pilot, applied to control the backlight | **blocked** | The prototype is described in three sentences: no sensor, no circuit, no software, no lux scale, no threshold, no timing. My stand-in hysteresis controller (`src/prototypes.py`) shows why that matters: on the same trace, plausible settings give 2 to 6 backlight switches and a duty cycle from 0.164 to 0.545 (D13). Nothing in the paper picks among them | Section 4.2 |
| I14 | The orientation-sensitive user interface: two mercury switches, portrait / landscape / upside-down rotation | **partial** | The state machine reproduces (`src/prototypes.py`), and two binary switches do supply exactly the four states that "always right way up" needs. But the paper constrains **none** of the 24 possible switch-state→orientation bijections (D14) and gives no debounce or latency (D15); Fig. 2's Newton MessagePad and its software are unavailable. See mismatch 5 | Section 4.2, Fig. 2 |
| I15 | Conclusion: "deploying multiple sensors of the same type (e.g. several light sensors) contributes valuable additional information (e.g. direction of light, sunny, shade)" | **blocked** | "First experiments" with no data, no method, no metric and no result. Worse, the quantity claimed cannot be expressed in the paper's own architecture: Section 5.1 requires a cue to depend on a single sensor, and `src/architecture.py` refuses to build a two-light-sensor cue with exactly that message | Section 6; cf. Section 5.1 |

Counts: **3 verified, 7 partial, 5 blocked, 15 inner-loop components.**

### Outer loop — not attempted, not scored

| # | Component / claim | Why it is outer loop | Citation |
|---|---|---|---|
| O1 | That integrating a light sensor "can substantially add to usability of ultra-mobile devices" | A claim about what people experience. No participants, task, measure or procedure is reported — the paper asserts the usability benefit | Section 4.2 |
| O2 | The three interaction benefits claimed for orientation awareness: "always right way up"; alternating portrait/landscape for spreadsheets and browsing; taking turns and showing the display in face-to-face collaboration over a PDA | Each is a claim about users, one of them about two people in a social setting. Establishing them needs participants; none appear | Section 4.2 |
| O3 | "The Newton MessagePad and also other PDAs actually offer operating system support for rotation of the user interface but experience shows that this feature is hardly used, if at all" | An empirical statement about user behaviour, with no study, no source and no data behind it | Section 4.2 |
| O4 | Collecting the raw sensor data "in different situations, for instance 'indoors' and 'outdoors'" | Someone has to carry the device through those situations; the target contexts the paper names ("engaged in conversation", "in a meeting", jogging) exist only when a person enacts them | Section 5.3 |
| O5 | The ground truth of context recognition: that a recognised context is the situation the user is actually in | The labels are human situations, so the reference against which any recognition rate would be computed can only come from people | Section 5, Table 1 |
| O6 | The application benefits that motivate the paper: filtering the information flow to address information overload, context-aware communication (urgency, interruptibility), proactive application scheduling | Claims about human attention, interruption and task behaviour. The paper offers them as motivation and reports no study of them | Section 3.3 |

### Derived rate — read the table, not this number

With the decomposition above, 3 of 15 inner-loop components verify, 7 are partial and 5 are
blocked (a 20% verified / 47% partial / 33% blocked split). That split is a summary of *this*
slicing and nothing more. Merge I9–I11 into one "cue extraction" row and I7 with I8 into one
"awareness device" row and the same evidence becomes 3 verified of 11; split the scripting
semantics into its three triggers and it becomes 5 of 17. The number is not comparable
across papers or across runs of this audit; the table is the result.

## Mismatches

Recorded as data in `verdict.json` on the rows they belong to.

1. **I12 — contradiction between the abstract and the body.** The abstract states "Based on
   an implementation of the model an experiment is described and the feasibility of the
   approach is demonstrated". Section 5.3 describes data collection in "different
   situations" and shows Fig. 4; it reports no measurement of any kind — no accuracy, no
   sample count, no duration, no separability statistic, no repetitions. The delta is
   everything a reader would need: the demonstration is asserted, not shown.
2. **I10 — the paper's one number leaves its own cue undetermined.** Section 5.3 offers
   "artificial light" as a cue obtainable with "simple statistical functions" from light
   readings, and separately gives the device's total output as "about 1100 Bytes … per
   second", interlaced. Distinguishing artificial from natural light by mains flicker needs
   more than 200 Hz on the light channel (100 Hz flicker at 50 Hz mains). At one byte per
   sample the budget supports that for at most 5 equally interlaced channels, while
   Section 5.2 says the board was built for "a greater number of possibly relevant
   sensors". Reproduced arithmetic, not a reproduced result: 1100/4 = 275 Hz (feasible),
   1100/6 = 183 Hz (not). A variance-based reading of the cue survives below Nyquist, but
   the frequency can no longer be identified — which is why this is a real fork in any
   reimplementation, not a quibble.
3. **I4 (a verified row) — the conclusion contradicts the architecture it verified.** Section 5.1: "Each cue is
   dependent on a single sensor." Section 6: several light sensors together yield "direction
   of light". Two separate light sensors are two sensors, so that quantity cannot be a cue
   in the paper's own layering; it would have to live at the context layer, which the paper
   does not say; the row stays verified, because the architecture as stated is what reproduced, and
   the contradiction is recorded on it rather than hidden by the outcome. (A two-axis accelerometer is not the same case: Section 5.1 explicitly
   allows a sensor to return a vector, so my motion cue over both axes stays inside the
   rule.)
4. **I2 — the feature space does not cover the paper's own sensing.** Section 4.1 proposes
   sensors that report "the handling of ultra-mobile devices", and Section 4.2's second
   prototype is built entirely on device orientation, but the Fig. 1 feature space has no
   branch, category or feature for device state or handling; the two motion cues of Table 1
   have nowhere to live in it either.

5. **I14 — three modes named, four needed.** Section 4.2 names three display modes
   (portrait upright, landscape turned sideways, "also rotated accordingly" upside down),
   but its own first bullet — "the adaptive user interface is always the right way up
   whichever way a device is held" — requires four distinguishable orientations, because
   the two landscape directions differ. Two mercury switches do supply exactly four states,
   so the design works; the count in the prose is one short, and which landscape direction
   each state means is left open (D14).

A metadata-level typo, recorded in [SOURCES.md](SOURCES.md) rather than in the table: the
publisher's page range (893–901) and the authors' own abstract page (893–902) disagree.

## The inner/outer boundary, and how it was drawn

The rule applied: a component is outer loop **only** when it genuinely requires human
participants — not when it is merely hard, expensive, obsolete or undocumented.

Two consequences worth stating plainly, because they are where this paper tests the rule:

- **Unavailable 1999 hardware is an inner-loop blocker, not an outer-loop component.**
  Rebuilding a Palm Pilot with a light sensor (I13), a Newton MessagePad with two mercury
  switches (I14) or the TEA awareness board (I7) needs no participants. These sit inside
  the inner loop and are marked blocked or partial because the *documentation* is
  insufficient — no part list, no schematic values, no firmware, no thresholds. Calling
  them "outer loop" would be hiding a reporting gap behind the human-subjects boundary.
- **Situated data collection is outer loop.** The Section 5.3 recordings (O4) look like a
  pure engineering activity, but the data only exist because a person carried the device
  through the situations, and the labels ("indoors", "in a meeting", jogging, "engaged in
  conversation") are enacted by people. Simulating that would mean fabricating the study.
  So `src/synth.py` generates a stream with the *structure* the paper describes, is labelled
  synthetic in every output it touches, and is never presented as a stand-in for what the
  authors measured.

### What a follow-up human study would have to cover

Stated here so the boundary is actionable rather than only descriptive; the machine-readable
form, with the criteria each component fails, is `servability` in `instrument.json`. None of
the six is servable in a browser.

- **O1, the backlight claim.** Participants using a handheld display under controlled
  ambient light — lighting is the manipulation, so it cannot be administered by a page, and
  the device needs a light sensor and a switching rule the paper never specifies (D13).
- **O2, the orientation benefits.** Participants physically turning a device, and a second
  person for the collaboration claim; turn-taking and "showing the display to another" can
  only be captured by observation or video coding, and the Newton interface of Fig. 2 would
  have to be rebuilt first, including the switch-to-orientation mapping the text leaves open
  (D14, D15).
- **O3, "hardly used, if at all".** A survey or log study of people's own devices, with an
  instrument the paper does not contain; the behaviour happens in software no page controls
  or can verify.
- **O4, the situated recordings.** A person carrying a documented multi-sensor board through
  named indoor and outdoor situations — which first requires the sensor list and the frame
  format the paper omits (D2, D3) and operational definitions of the situations (D16).
- **O5, recognition ground truth.** Experience sampling of real situations over more than
  one session, plus a labelling protocol, before any recognition rate could be quoted.
- **O6, the three application benefits.** Working context-aware applications driven by real
  sensed context — interruptibility, filtering, scheduling — none of which exists in the
  paper as an interface, task or stimulus set.

What follows from the boundary is the shape of the whole audit: the outer loop of this
paper is **absent rather than unreproducible**. Six human-facing claims (O1–O6) carry the
paper's argument about usability, interaction and application benefit, and not one of them
is backed by a described procedure. That is the single most important finding here, and no
amount of inner-loop code can compensate for it.

## Hidden decisions

Every free parameter a reimplementation must choose that the paper does not state. The same
ids appear in `src/assumptions.py` (from which the code actually reads them),
`results/assumptions.json` after a run, and `verdict.json`.

| id | Question the paper leaves open | Where | Assumed here | Sensitivity |
|---|---|---|---|---|
| D1 | Per-channel sample rate and ADC resolution | Section 5.3 gives only "about 1100 Bytes … per second" for the whole interlaced stream; Fig. 4 has no units | 275 Hz, 8-bit — derived from the paper's own budget at 1 byte/sample over the four channels of D2 (1100/4); a second run at 128 Hz is recorded | High. Above 200 Hz the artificial-light cue can read the flicker band; below it the same cue must fall back to aliased variance and can no longer identify the frequency |
| D2 | Which sensors the awareness device carries, and how many | Section 5.2: "a greater number of possibly relevant sensors", never enumerated | 4 channels: light, two accelerometer axes, temperature | High for the byte budget (D1, D3), low for the pipeline structure |
| D3 | Frame format of the interlaced serial stream | Section 5.3 says only "transmitted interlaced" | Fixed round-robin, one byte per sample, no sync marker, channel order supplied out of band | Total for decoding real device output — a wrong order silently swaps channels; none once data are per-channel arrays |
| D4 | The "brightness" cue function and its symbol boundaries | Section 5.3: "simple statistical functions" | Window mean, dark below 0.20 and bright above 0.55 of full scale | High: the boundaries decide whether an indoor window reads dim or bright, and therefore whether the office rule fires |
| D5 | The "artificial light" cue function | Section 5.3 names the cue only | Flicker prominence: mean power in ±6 Hz around 2× mains, over the median power above 10 Hz, artificial above 4; variance fallback below Nyquist | Very high — this is the entire cue, and it interacts with D1 and D6 |
| D6 | Mains frequency | Never stated (the work was done in Germany; flicker is never mentioned) | 50 Hz mains, 100 Hz flicker | Medium: a 60 Hz deployment moves the band to 120 Hz and the cue must be retuned |
| D7 | Cue window length and overlap | Section 5.1: "the values of a single sensor up to a certain time" — the time is never given | 1.0 s, non-overlapping | Medium: short windows make the flicker estimate noisy, long ones delay and smear context changes |
| D8 | Motion cue thresholds (stationary / walking / running) | Section 5.3 names the cues only | SD of accelerometer magnitude in ADC counts: <2 stationary, <12 walking, else running | High for absolute labels (they scale with sensor sensitivity and mounting); the ordering is robust |
| D9 | How the certainty number of a context vector is computed | Section 5.1 says each vector carries "a number indicating the certainty" and stops | Fraction of a rule's required cues that are satisfied, in [0,1], not normalised across contexts | High: it sets the scale against which every scripting threshold is compared |
| D10 | Scripting thresholds and times | Section 5.1 gives the semantics, no values | Enter above 0.70 held 2 s; leave below 0.50 held 2 s; while-in fires every 5 s | High on event counts (12 events on the recorded run) |
| D11 | Whether enter and leave share one threshold | Section 5.1 never relates them | Two thresholds (0.70 / 0.50), i.e. hysteresis | High near the boundary: one threshold makes the context state chatter |
| D12 | How the negative time of context prediction works | Footnote to Section 5.1 | Not implemented; a negative time raises an error | Not applicable — it cannot be built from the paper at all |
| D13 | Backlight switching level, hysteresis and time constant | Section 4.2 describes the light-sensitive display in three sentences | On below 0.25 of full scale, off above 0.35, 1.0 s debounce | High and user-visible: 2–6 switches and duty 0.164–0.545 across plausible settings on the same trace |
| D14 | Which mercury-switch state maps to which orientation | Section 4.2 describes the behaviour, not the wiring | Orthogonal mounting, (0,0) portrait, (0,1) landscape-right, (1,1) inverted, (1,0) landscape-left | High: 24 bijections are consistent with the text, and a wrong pick mirrors or inverts the interface |
| D15 | Debounce before the interface rotates | Not stated | 300 ms of stable switch state | High for perceived behaviour, and untestable without participants |
| D16 | Operational definitions of the recorded situations | Section 5.3: "different situations, for instance 'indoors' and 'outdoors'" — no place, duration, time of day, lighting type, activity script or labelling procedure | The synthetic generator's own definitions (`src/synth.py`), which stand in for nothing the authors measured | High: any accuracy figure would be a figure about these definitions, which is why none is claimed |
| D17 | How much data lies behind Fig. 4 | Fig. 4 is captioned "Light sensor data" | 10 s per condition in the synthetic stand-in | High for any statistical statement; nothing in the paper constrains it |
| D18 | The cue→context rule form and how Table 1's cues combine | Section 5.3 offers "explicit rule specification … informed by prior statistical analysis" and gives no rule and no statistics | Unweighted conjunction over Table 1's cues, certainty as in D9 | High: a weighted or disjunctive form changes both the ranking of contexts and the certainties |

## Open-science scorecard

| Criterion | Found | Where / what was searched |
|---|---|---|
| Code | **No** | Author publication list at teco.edu (draft PDF and abstract page only), the authors' legacy and current homepages, the `teco-kit` GitHub organisation, three GitHub repository searches, Zenodo, OSF, Papers with Code, Crossref `relation`, KITopen. Full list with HTTP results in [SOURCES.md](SOURCES.md) |
| Data | **No** | Same places. Fig. 4's light-sensor traces, the raw recordings of Section 5.3 and the awareness-device stream were never deposited; the paper contains no data-availability statement (the 1999 Elsevier format has none) |
| License | **No** | The article is "Copyright © 1999 Elsevier Science B.V. All rights reserved"; the only licence Crossref registers is Elsevier's text-mining user licence (`https://www.elsevier.com/tdm/userlicense/1.0/`), which is not an open licence. The authors' draft PDF carries no licence statement at all. No artifact exists to license |
| Preregistration | **No** | Not mentioned in the paper; OSF title search and OSF search API returned nothing; the practice postdates the paper. Recorded as a fact, not a criticism of 1999 practice |
| Supplement | **No** | Crossref registers no supplementary-material relation; the paper has no appendix and no ancillary files; the article predates arXiv deposit by these authors. **One caveat**: ScienceDirect itself could not be fetched by this tooling, so the absence of a supplementary tab there is inferred from Crossref and from search-engine renderings of the page, not verified directly — see [UNVERIFIED.md](UNVERIFIED.md) |

## What was actually run

Commands and their real output, on the recorded run (Python 3.11, numpy 2.4.6, pandas 3.0.5,
matplotlib 3.11.1):

```
$ python src/selftest.py
ok   Fig. 1 has two branches ['human factors', 'physical environment']
ok   Fig. 1 has six categories of three example features
ok   Section 3.1 states four model rules
ok   Table 1 motion cues have no category in Fig. 1 ['stationary or walking', 'walking or running']
ok   cue layer enforces 'each cue is dependent on a single sensor'
ok   negative scripting time (prediction footnote) is refused, not faked
ok   context certainty is constrained to the assumed [0,1] scale
ok   enter fires once after the dwell time, then leave fires once [('enter', 3.0), ('leave', 8.0)]
ok   1100 B/s over 4 one-byte channels is 275 Hz each
ok   at most 5 equally interlaced one-byte channels resolve 100 Hz flicker max=5
ok   interlace/deinterlace round-trips
ok   synthetic stream is generated at the D1 rate 275.0 Hz
ok   indoor windows read as artificial light {'indoors-dark-corridor': 'artificial', 'indoors-near-window': 'artificial', 'indoors-office-desk': 'artificial', 'outdoors-running': 'natural', 'outdoors-walking': 'natural'}
ok   outdoor windows read as natural light {'indoors-dark-corridor': 'artificial', 'indoors-near-window': 'artificial', 'indoors-office-desk': 'artificial', 'outdoors-running': 'natural', 'outdoors-walking': 'natural'}
ok   motion cue orders desk < walking < running {'indoors-dark-corridor': 'walking', 'indoors-near-window': 'stationary', 'indoors-office-desk': 'stationary', 'outdoors-running': 'running', 'outdoors-walking': 'walking'}
ok   'Jogging' cannot exceed certainty 0.5 with the sensors the paper describes {'In the office': 0.75, 'Jogging': 0.5}
ok   two switches leave all 24 state-to-orientation mappings open
ok   orientation only changes after the assumed debounce portrait -> portrait-inverted
ok   analyze.py runs to completion
ok   analyze.py wrote cues.csv
ok   analyze.py wrote contexts.csv
ok   analyze.py wrote events.json
ok   analyze.py wrote summary.json
ok   analyze.py wrote report.md

24 checks passed
```

```
$ python src/synth.py --out /tmp/run/synth_275hz.csv
wrote /tmp/run/synth_275hz.csv: 12100 rows, 44.00 s, 5 labelled situations (SYNTHETIC, not the paper's data)

$ python src/analyze.py /tmp/run/synth_275hz.csv --outdir /tmp/run/results_275
samples=12100 rate=275.0Hz windows=44
model Fig.1 structure ok: branches=True six_categories=True
Table 1 cues unhoused by Fig. 1: ['stationary or walking', 'walking or running']
byte budget: the paper's 1100 B/s over 4 one-byte channels allows 275.0 Hz each (at most 5 channels stay above the 200.0 Hz needed for 100 Hz flicker); this input runs at 275.0 Hz, cue path: flicker band (frequency domain)
single-sensor rule: cue 'direction of light' reads 2 sensors; Section 5.1: 'Each cue is dependent on a single sensor'
Table 1 certainty ceilings with the paper's sensors: {'In the office': 0.75, 'Jogging': 0.5}
  indoors-dark-corridor    light={'artificial': 6} motion={'walking': 6}
  indoors-near-window      light={'artificial': 8} motion={'stationary': 7, 'walking': 1}
  indoors-office-desk      light={'artificial': 10} motion={'stationary': 10}
  outdoors-running         light={'natural': 10} motion={'running': 10}
  outdoors-walking         light={'natural': 10} motion={'walking': 10}
scripting events: 12
backlight: on 0.164 of the trace, 2 switches (over five D13 settings: switches [2, 6, 6, 2, 2], duty [0.164, 0.221, 0.219, 0.318, 0.545])
orientation: 3 rotations, 24 mappings left open by the text
wrote /tmp/run/results_275/: cues.csv contexts.csv events.json summary.json assumptions.json report.md fig4_style_light.png
```

The D1 sensitivity, run a second time below the flicker Nyquist rate:

```
$ python src/synth.py --out /tmp/run/synth_128hz.csv --rate 128
wrote /tmp/run/synth_128hz.csv: 5632 rows, 43.99 s, 5 labelled situations (SYNTHETIC, not the paper's data)

$ python src/analyze.py /tmp/run/synth_128hz.csv --outdir /tmp/run/results_128
byte budget: the paper's 1100 B/s over 4 one-byte channels allows 275.0 Hz each (at most 5 channels stay above the 200.0 Hz needed for 100 Hz flicker); this input runs at 128.0 Hz, cue path: aliased-variance fallback
  indoors-dark-corridor    light={'artificial': 6} motion={'walking': 6}
  indoors-near-window      light={'artificial': 8} motion={'stationary': 5, 'walking': 3}
  indoors-office-desk      light={'artificial': 10} motion={'stationary': 10}
  outdoors-running         light={'natural': 10} motion={'running': 10}
  outdoors-walking         light={'natural': 10} motion={'walking': 10}
```

Both runs classify the synthetic situations the same way by two different mechanisms, which
is a statement about the synthetic generator and about the fork D1/D5 opens — not a
reproduction of any result in the paper, because the paper states none.
