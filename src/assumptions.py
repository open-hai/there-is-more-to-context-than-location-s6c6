"""Every free parameter this reimplementation had to invent, in one place.

Each entry is a decision the paper leaves unwritten.  `where` is where the paper
leaves it open, `assumed` is the value this code uses, `sensitivity` is how much
the result moves if the choice is wrong.  The ids (D1...) are the same ids used
in REPRODUCIBILITY.md and verdict.json, so the three can be checked against each
other.
"""

from __future__ import annotations

ASSUMPTIONS: dict[str, dict] = {
    "D1": dict(
        question="At what rate and resolution is the light channel sampled?",
        where="Section 5.3 gives only an aggregate: 'about 1100 Bytes of sensor "
              "readings per second' for the whole interlaced stream; no per-channel "
              "rate, no ADC width, no units on Fig. 4.",
        assumed="275 Hz, 8-bit unsigned (0-255 counts) per channel -- derived from "
                "the paper's own 1100 B/s at one byte per sample and the four "
                "channels of D2 (1100/4 = 275); a second run at 128 Hz is reported "
                "to show what changes below the flicker Nyquist rate",
        sensitivity="high: below 200 Hz the 100 Hz mains flicker used by the "
                    "'artificial light' cue is aliased, so a frequency-domain "
                    "reading of that cue is replaced by a variance fallback and the "
                    "flicker frequency can no longer be identified",
        value=dict(sample_rate_hz=275.0, adc_bits=8),
    ),
    "D2": dict(
        question="Which sensors does the awareness device carry, and how many?",
        where="Section 5.2 says only that it was 'designed to allow experimentation "
              "with a greater number of possibly relevant sensors'; no sensor list, "
              "no part numbers, no schematic values in Fig. 3.",
        assumed="4 channels: one light sensor, two accelerometer axes, one temperature "
                "sensor -- enough to exercise every cue the paper names",
        sensitivity="high for the per-channel sampling budget (D1, D3); low for the "
                    "structure of the pipeline itself",
        value=dict(channels=["light", "acc_x", "acc_y", "temp"]),
    ),
    "D3": dict(
        question="What is the frame format of the interlaced serial stream?",
        where="Section 5.3: 'The data from different sensors is transmitted interlaced "
              "to ensure recognition of sudden changes in the readings.' No frame "
              "layout, channel order, sync marker or word width is given.",
        assumed="fixed round-robin over the channel list, one byte per sample, no "
                "sync marker, decoder told the channel order out of band",
        sensitivity="total for decoding raw device output (a wrong order silently "
                    "swaps channels); none once the data are in per-channel arrays",
        value=dict(bytes_per_sample=1, order="round-robin"),
    ),
    "D4": dict(
        question="What function turns light readings into the 'brightness' cue, and "
                 "at what symbol boundaries?",
        where="Section 5.3: 'Simple statistical functions can be applied to extract "
              "cues such as \"artificial light\" and \"brightness\"' -- the functions "
              "and thresholds are not given.",
        assumed="mean of the window, mapped to dark / dim / bright at 0.20 and 0.55 "
                "of ADC full scale",
        sensitivity="high: the boundaries decide directly whether an indoor window is "
                    "called dim or bright, and hence whether the office rule fires",
        value=dict(dark_below=0.20, bright_above=0.55),
    ),
    "D5": dict(
        question="What function produces the 'artificial light' cue?",
        where="Section 5.3 names the cue and says only that simple statistical "
              "functions suffice; no method is described.",
        assumed="mains-flicker detection: mean spectral power in a +/-6 Hz band "
                "around 2x mains frequency divided by the median power above a 10 Hz "
                "cutoff, cue = 'artificial' when that prominence exceeds 4; a "
                "variance-only fallback is used when the channel rate is below the "
                "flicker Nyquist rate",
        sensitivity="very high: this is the whole cue; it also interacts with D1 "
                    "(sample rate) and D6 (mains frequency)",
        value=dict(band_hz=6.0, prominence_threshold=4.0, hp_cutoff_hz=10.0),
    ),
    "D6": dict(
        question="What mains frequency should the flicker cue assume?",
        where="Never stated; the work was done in Karlsruhe, Germany (50 Hz mains, "
              "100 Hz flicker from fluorescent lighting), but the paper does not say "
              "so and does not mention flicker at all.",
        assumed="50 Hz mains, i.e. 100 Hz illumination flicker",
        sensitivity="medium: a 60 Hz deployment moves the band to 120 Hz and the cue "
                    "must be retuned; the dark/bright cue is unaffected",
        value=dict(mains_hz=50.0),
    ),
    "D7": dict(
        question="Over what window, with what overlap, is a cue computed?",
        where="Section 5.1 says a cue takes 'the values of a single sensor up to a "
              "certain time' -- the time is never quantified.",
        assumed="1.0 s non-overlapping windows for every cue",
        sensitivity="medium: shorter windows make the flicker estimate noisy, longer "
                    "windows delay context changes and smear transitions",
        value=dict(window_s=1.0, overlap=0.0),
    ),
    "D8": dict(
        question="What thresholds separate the motion cues stationary / walking / "
                 "running?",
        where="Section 5.3 names 'stationary', 'walking' and so on as accelerometer "
              "cues, with no feature, no threshold and no axis convention.",
        assumed="standard deviation of the accelerometer magnitude within the window, "
                "in ADC counts: < 2 stationary, < 12 walking, else running",
        sensitivity="high for the absolute labels (they scale with sensor sensitivity "
                    "and mounting); the ordering stationary < walking < running is "
                    "robust",
        value=dict(stationary_below=2.0, walking_below=12.0),
    ),
    "D9": dict(
        question="How is the certainty number of a context vector computed?",
        where="Section 5.1 says each context vector carries 'a number indicating the "
              "certainty' -- no scale, no normalisation, no combination rule.",
        assumed="fraction of the rule's required cues that are satisfied, in [0, 1]; "
                "certainties across contexts are not normalised and may sum above 1",
        sensitivity="high: it sets the scale on which every scripting threshold (D10) "
                    "is compared, so it changes which events fire",
        value=dict(rule="satisfied_required_cues / required_cues"),
    ),
    "D10": dict(
        question="What threshold and what time do the scripting triggers use?",
        where="Section 5.1 states the enter / leave / while semantics but gives no "
              "threshold value and no time value for any of them.",
        assumed="enter above 0.70 sustained 2 s; leave below 0.50 sustained 2 s; while "
                "in context, fire every 5 s",
        sensitivity="high on event counts: with a single 0.5 threshold and no dwell "
                    "time the synthetic run produces markedly more transitions",
        value=dict(enter=0.70, leave=0.50, dwell_s=2.0, while_every_s=5.0),
    ),
    "D11": dict(
        question="Do enter and leave share one threshold (i.e. is there hysteresis)?",
        where="Section 5.1 describes the two triggers separately and never relates "
              "their thresholds.",
        assumed="two thresholds, 0.70 / 0.50, giving hysteresis",
        sensitivity="high near the boundary: a single threshold makes the context "
                    "state chatter on noisy cue windows",
        value=dict(hysteresis=True),
    ),
    "D12": dict(
        question="How does the negative time of context prediction work?",
        where="Footnote to Section 5.1: 'In case of context prediction the time might "
              "be negative.' No prediction mechanism appears anywhere in the paper.",
        assumed="not implemented; the scripting layer raises NotImplementedError on a "
                "negative time",
        sensitivity="not applicable: the feature cannot be built from the paper at all",
        value=dict(implemented=False),
    ),
    "D13": dict(
        question="At what light level does the light-sensitive display switch its "
                 "backlight, and with what time constant?",
        where="Section 4.2 says a light sensor was integrated in a Palm Pilot 'to "
              "provide it with an awareness of surrounding lighting conditions, which "
              "can be applied for control of its display's backlight' -- no lux scale, "
              "no threshold, no timing, no hysteresis.",
        assumed="backlight on below 0.25 of full scale, off above 0.35, with a 1.0 s "
                "debounce",
        sensitivity="high and user-visible: the transition count on the synthetic "
                    "trace changes by an order of magnitude across plausible "
                    "threshold/debounce settings (reported by src/analyze.py)",
        value=dict(on_below=0.25, off_above=0.35, debounce_s=1.0),
    ),
    "D14": dict(
        question="Which mercury-switch state corresponds to which screen orientation?",
        where="Section 4.2 says the Newton MessagePad was enhanced 'by adding two "
              "mercury switches and simple electronics' and describes the resulting "
              "behaviour, but neither the switch geometry nor the state-to-orientation "
              "mapping is given.",
        assumed="switches mounted orthogonally; (a,b) = (0,0) portrait, (0,1) "
                "landscape-right, (1,1) portrait-inverted, (1,0) landscape-left",
        sensitivity="high: two binary switches admit 24 bijections onto four "
                    "orientations and the text rules out none of them, so a wrong "
                    "choice mirrors or inverts the interface",
        value=dict(n_bijections=24, constrained_by_text=0),
    ),
    "D15": dict(
        question="How long must a switch state be stable before the interface rotates?",
        where="Section 4.2 describes rotation on turning the device but gives no "
              "debounce, no latency and no filter.",
        assumed="300 ms of stable switch state before rotating",
        sensitivity="high for perceived behaviour (rotation while handing the device "
                    "over), and untestable without participants",
        value=dict(debounce_s=0.3),
    ),
    "D16": dict(
        question="What are the operational definitions of the situations that were "
                 "recorded ('indoors', 'outdoors', 'in the office', 'jogging')?",
        where="Section 5.3: 'we collected raw data in different situations, for "
              "instance \"indoors\" and \"outdoors\"'. No place, duration, time of "
              "day, weather, lighting type, activity script or labelling procedure.",
        assumed="the synthetic generator's own definitions (src/synth.py), which are "
                "stand-ins and reproduce nothing of the paper's data",
        sensitivity="high: any accuracy figure is a figure about these definitions, "
                    "which is why none is claimed here",
        value=dict(source="src/synth.py"),
    ),
    "D17": dict(
        question="How much data lies behind Fig. 4, and over what interval?",
        where="Fig. 4 is captioned only 'Light sensor data'; the text says the two "
              "traces come from 'two different contexts'. No axes units, no duration, "
              "no sample count, no repetitions, no separability measure.",
        assumed="10 s per condition in the synthetic stand-in",
        sensitivity="high for any statistical statement; nothing in the paper "
                    "constrains it",
        value=dict(seconds_per_condition=10),
    ),
    "D18": dict(
        question="What rule form maps cues to a context, and how are Table 1's cues "
                 "combined?",
        where="Section 5.3 offers 'explicit rule specification to infer context from "
              "cues, informed by prior statistical analysis' as one of two options, "
              "and gives no rule, no weights and no statistics.",
        assumed="conjunction over the cues of Table 1, each cue satisfied by a set of "
                "admissible symbols; certainty as in D9",
        sensitivity="high: a weighted or disjunctive form changes both the ranking of "
                    "contexts and the certainty values",
        value=dict(form="conjunctive, unweighted"),
    ),
}


def value(dec_id: str, key: str):
    return ASSUMPTIONS[dec_id]["value"][key]


def as_records() -> list[dict]:
    return [
        {"id": k, "question": v["question"], "where": v["where"],
         "assumed": v["assumed"], "sensitivity": v["sensitivity"]}
        for k, v in ASSUMPTIONS.items()
    ]


if __name__ == "__main__":
    import json

    print(json.dumps(as_records(), indent=2))
