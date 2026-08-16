# Unverified

Everything this audit could not confirm, each with the blocker that stopped it. Nothing
below is presented as a finding about the paper; these are the limits of the audit.

## The text

1. **The version of record was never read.** The audited text is the authors' draft PDF
   (MD5 `81ea8c4246cfe16b6c6842c47daa9280`, 10 pages, created 2000-08-17), which Semantic
   Scholar and Unpaywall list as the green open-access copy of this DOI.
   *Blocker*: `sciencedirect.com` is refused by this environment's fetch tool
   (`url_not_allowed`), and Elsevier's text-mining endpoint returns HTTP 400 without an
   institutional key. Consequences that cannot be ruled out: the published version may
   contain copy-edited wording, an acknowledgements section, figure axis labels or units
   that the draft lacks, corrected reference numbering, or additional detail added in
   review. Section, figure and table numbers used here are the draft's.
2. **Whether the published article has a supplementary-material tab.** *Blocker*: same. The
   inference that it does not rests on Crossref registering no supplementary-material
   relation for the DOI and on search-engine renderings of the ScienceDirect page showing
   only abstract, section snippets and references.
3. **Page range.** Publisher metadata says 893–901; the first author's own abstract page
   and the Wikipedia citation say 893–902. *Blocker*: no access to the printed issue.
4. **The 1998 IMC workshop version was not compared line by line.** It is available as
   PostScript (`imc98.ps`, HTTP 200) and might, for instance, quote thresholds the journal
   version dropped. *Blocker*: no PostScript converter in this environment (`gs` absent).
   If it does contain such detail, that would change the *reporting* diagnosis for the
   1999 paper but not the reproduction outcomes, which are about this DOI.
5. **The unnumbered first reference.** In the draft, the Abowd et al. Classroom2000 entry
   sits before `[1]` without a number and the body cites it as "the Classroom2000 study 0".
   Whether this is fixed in the version of record is unknown (blocker as in 1), so it is
   not recorded as a mismatch.

## The artifact hunt

6. **"Dead" verdicts describe the live web only.** The TEA project pages
   (`teco.edu/tea/tea_hrd2.html`, `teco.edu/research/tea-technology-for-enabling-awareness/`,
   `tea.starlab.net`, `omega.it/tea`) return 404 or fail to resolve today.
   *Blocker*: `web.archive.org` returns HTTP 403 / is blocked by this environment's egress
   policy, and the fetch tool refuses the host, so no archived snapshot could be inspected.
   An archived copy may well still describe the awareness-device hardware; it would not
   change the finding that the paper's own artifacts are not available at any URL the paper
   or its authors advertise.
7. **GitHub code search.** Repository searches ran and returned nothing relevant; the code
   search endpoint returned HTTP 403 (unauthenticated rate limit), so "no code on GitHub
   mentions this paper" is *not* established. Repository-level absence is established.
8. **The `teco-kit` organisation listing** was established through web search of the
   organisation's repository pages, because the GitHub REST API rate-limited the org
   endpoint. A private or archived repository would not be visible either way.
9. **Unpaywall was not queried properly.** Its API requires a real contact address and this
   audit contacts no one, so the OA-location list comes from OpenAlex and Semantic Scholar
   instead.
10. **No author was contacted**, by design. Anything only the authors could supply — the
    sensor list of the awareness board, the thresholds, the Fig. 4 traces — stays unverified.

## The reproduction

11. **No inner-loop output can be checked against the paper.** The paper reports no
    accuracy, error rate, sample count, duration, unit or threshold, so every number in
    `results/` is a statement about the synthetic input in `src/synth.py`. Nothing here
    confirms or refutes the paper's qualitative claim that the two lighting conditions of
    Fig. 4 are "easily and reliably distinguished".
12. **The cue functions are inventions, not reconstructions.** "Artificial light" as mains
    flicker (D5/D6) is a plausible reading of "simple statistical functions", and it is the
    reading that makes the cue mean something; it is not what the paper says, because the
    paper says nothing. The authors may have used a coarse intensity comparison, a colour
    or IR ratio, or a hand-tuned rule.
13. **The byte-budget arithmetic assumes one byte per sample and equal interlacing.** Both
    come from D3. With 10- or 12-bit samples, or with the light channel polled
    preferentially, the channel counts in I8/I10 change; the arithmetic is reproducible, its
    premises are assumed.
14. **The three hardware components (I7, I13, I14) were not built.** No Palm Pilot, no
    Newton MessagePad, no TEA board, and — more importantly — no part list, schematic
    values or firmware to build them from. The logic is reimplemented; the devices are not.
15. **Whether the awareness device could in fact run this pipeline in 1999** is untested.
    The paper says explicitly that its prototype was "focussed on data acquisition, rather
    than elegant processing", with cue generation, context calculation and script execution
    done in software on a host computer; timing and CPU budgets are never given.
16. **Cross-paper tension noted but not resolved.** A companion paper by overlapping
    authors (HUC'99, LNCS 1707) describes a TEA board whose accelerometers are "filtered
    down to 200 Hz" and whose fast channels are polled "on the order of every
    millisecond" — rates that do not obviously fit inside 1100 bytes per second. Whether
    the two papers describe the same board revision is unknown; the audited paper gives no
    revision, so this is left as an observation about the literature, not a mismatch inside
    this paper.

## The outer loop

17. **Nothing about the six outer-loop claims (O1–O6) was verified, and nothing was
    simulated.** No participant data were generated, no effect was estimated, and no user
    study was reconstructed. The audit's claim is only that the paper describes no
    procedure for any of them — which is a statement about the paper's text, checked
    against the whole text, including its footnotes and reference list.
18. **`instrument.json` has a null `protocol`.** That is a refusal, not an omission: the
    paper's only procedural sentence about data collection is one clause of Section 5.3. The
    reason is recorded in `absent_reasons.protocol`.
