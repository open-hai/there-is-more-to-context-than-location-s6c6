# Sources

## The paper

| Field | Value |
|---|---|
| Title | There is more to context than location |
| Authors | Albrecht Schmidt, Michael Beigl, Hans-W. Gellersen (Telecooperation Office (TecO), University of Karlsruhe) |
| Venue | Computers & Graphics, volume 23, issue 6, December 1999 |
| Pages | 893–901 per the publisher's metadata; 893–902 per the authors' own abstract page and Wikipedia (see "Identity discrepancies" below) |
| DOI | [10.1016/S0097-8493(99)00120-X](https://doi.org/10.1016/S0097-8493(99)00120-X) |
| Publisher | Elsevier BV. Copyright © 1999 Elsevier Science B.V., all rights reserved |
| Earlier version | "There is more to Context than Location — Environment Sensing Technologies for Adaptive Mobile User Interfaces", *Interactive applications of mobile computing* (IMC'98), Rostock, 24–25 November 1998, pp. 9–14, ISBN 3-929544-96-2 |
| Funding named in the text | "The work reported in this section is conducted within the ESPRIT Project TEA 'Technology for Enabling Awareness'" (Section 5) |

### The text this audit used

The version of record sits behind Elsevier's paywall and `sciencedirect.com` cannot be
fetched by this environment's tooling. The audited text is the **authors' own draft PDF**,
still served from the first author's page at TecO and the file that Semantic Scholar and
Unpaywall point to as the green open-access copy of this DOI:

- `http://www.teco.edu/~albrecht/publication/draft_docs/context-is-more-than-location.pdf`
  — HTTP 200, 382,888 bytes, MD5 `81ea8c4246cfe16b6c6842c47daa9280`, 10 pages,
  PDF metadata `/Author albrecht`, `/Title myprint-version.PDF`, created 2000-08-17.
- A byte-identical copy (same MD5) is mirrored on a course page at
  `https://www.cs.umd.edu/class/spring2025/cmsc818G/files/moretocontext.pdf`.

Every section, figure and table reference in this repository refers to that draft. It is
plainly a pre-copyedit draft (it contains typos such as "considitons", "deviecs",
"foresee to approaches", and an unnumbered first reference that the body text cites as
"the Classroom2000 study 0"). Where the version of record might differ is recorded in
[UNVERIFIED.md](UNVERIFIED.md).

### Identity discrepancies found

- Page range: Crossref, Scopus/KITopen and the ScienceDirect record all give **893–901**;
  the first author's own abstract page and the Wikipedia citation give **893–902**. One
  page of difference, unresolved; it does not affect any claim in this audit.
- The 1998 IMC workshop paper carries the same main title, so citations to "Schmidt,
  Beigl & Gellersen, There is more to context than location" in the literature sometimes
  point at the shorter 1998 version (pp. 9–14) rather than at this DOI.

## Artifact hunt

Every place searched, with what came back. Nothing found anywhere is code, data, a
preregistration or a supplementary file: the only artifact the authors published for this
paper is the draft PDF above.

### Publisher and indexing records

| Where | What was looked for | Result |
|---|---|---|
| `https://doi.org/10.1016/S0097-8493(99)00120-X` | landing page, artifact links | resolves to ScienceDirect; page body not retrievable by this tooling |
| `https://www.sciencedirect.com/science/article/abs/pii/S009784939900120X` | supplementary-material tab, appendices | **not fetchable** (`url_not_allowed` from the fetch tool). Indirect evidence only: search-engine snippets of the page show abstract, section snippets and "References (18)" and no supplementary section |
| `https://api.crossref.org/works/10.1016/S0097-8493(99)00120-X` | `relation` (supplementary material), `assertion`, license | HTTP 200. `relation: {}` — no supplementary-material, dataset or software relations registered. Only license present is Elsevier's text-mining user licence (`https://www.elsevier.com/tdm/userlicense/1.0/`), not an open licence |
| `https://api.elsevier.com/content/article/PII:S009784939900120X?httpAccept=text/plain` (the text-mining link Crossref advertises) | full text | HTTP 400 without an institutional key |
| `https://api.openalex.org/works/doi:10.1016/s0097-8493(99)00120-x` | OA locations | HTTP 200. `is_oa: false`, two locations: the DOI and a CiteSeerX record; no PDF URL |
| `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/S0097-8493(99)00120-X` | open-access PDF, artifact fields | HTTP 200. `openAccessPdf` = the teco.edu draft (status GREEN); 1,346 citations; no artifact fields |
| `https://api.unpaywall.org/v2/10.1016/S0097-8493(99)00120-X` | OA locations | HTTP 422: the API requires a real contact address. Not pursued (no one is contacted in this audit) |
| `http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.37.2933` (the second OpenAlex location) | cached full text | HTTP 503 on repeated attempts — the record OpenAlex lists no longer serves |
| `https://paperswithcode.com/api/v1/papers/?title=There is more to context than location` | associated code | empty response, no record |
| `http://export.arxiv.org/api/query?search_query=all:"more to context than location"` | preprint, ancillary files | HTTP 200, 0 results — the paper was never on arXiv |

### The authors' own pages

| Where | What was looked for | Result |
|---|---|---|
| `https://www.teco.edu/~albrecht/publication/` (first author's publication list) | code, data, supplementary links for this paper | HTTP 200. The entry reads "draft as PDF 374KB" and "abstract" and nothing else. No paper on that page links to code or data |
| `https://www.teco.edu/~albrecht/publication/elsevir1999_abstract.html` | abstract page, artifact links | HTTP 200. Abstract plus "download draft version"; gives the page range as 893–902 |
| `https://www.teco.edu/~albrecht/publication/draft_docs/context-is-more-than-location.pdf` | the paper | HTTP 200, the audited file (see above) |
| `https://www.teco.edu/~albrecht/publication/draft_docs/` (directory listing) | other deposited files | HTTP 403, listing disabled |
| `https://www.teco.edu/~albrecht/` (first author's legacy homepage) | project and artifact links | HTTP 200. Describes the TEA project and links to `http://tea.starlab.net/`; no code or data links |
| `https://www.teco.edu/~albrecht/tea/` | TEA material | HTTP 200 — a page holding three TEA **logos**, nothing else |
| `http://www.teco.edu/tea/tea_hrd2.html` (TEA hardware page, still in search indexes) | the awareness-device hardware description | HTTP 404 — **dead** |
| `https://www.teco.edu/research/tea-technology-for-enabling-awareness/` (TEA project page, still in search indexes with a project description) | project page, artifacts | HTTP 404 by `curl`, `url_not_accessible` from the fetch tool; the current `https://www.teco.edu/research` index lists other legacy projects (`smart-its`, `media_cup`) but no TEA entry — **dead** |
| `http://tea.starlab.net/` (TEA project site linked from the first author's page) | project artifacts | connection failure, host does not resolve — **dead** |
| `http://www.omega.it/tea/` (the TEA URL cited in the authors' companion HUC'99 paper) | project artifacts | HTTP 200 but redirects to `https://www.omega.it/`, the company homepage; project pages gone — **dead** |
| `http://www.teco.uni-karlsruhe.de/` (the institutional host in the paper's own footer links) | anything | connection failure — **dead** |
| `https://publikationen.bibliothek.kit.edu/1000128233` (KITopen institutional repository) | deposited full text, data, supplement | HTTP 200. Metadata record only: no full text, no files, no data statement |
| `https://publikationen.bibliothek.kit.edu/145598` | the IMC'98 version | HTTP 200, metadata only (pp. 9–14) |
| `https://www.teco.edu/publications` (current TECO publication list) | artifact links | HTTP 200. Lists the paper with a DOI link only |
| `https://www.um.informatik.uni-muenchen.de/personen/professoren/schmidt/index.html` (first author, current position at LMU Munich) | data or code archives | HTTP 200. No mention of this paper, no artifact archive |
| `https://albrechtschmidt.info/` | personal artifact archive | does not resolve |
| `https://www.lancaster.ac.uk/scc/about-us/people/hans-gellersen` (third author) | artifacts | HTTP 200, no mention of this paper |
| `https://www.teco.edu/people` (second author's current group) | artifacts | HTTP 200, no legacy artifacts |

### Code and data repositories

| Where | What was looked for | Result |
|---|---|---|
| `github.com/teco-kit` (the authors' institutional GitHub organisation) | any 1990s TEA / awareness-device code | organisation exists; its repositories are all modern work (`edge-ml`, `OpenEarable`, `Android-Context-Framework`, `whar-datasets`, …). Nothing for this paper. (The GitHub REST API returned HTTP 403 rate-limit for the org listing, so this was established through web search of the org's repository pages) |
| GitHub repository search API: `technology for enabling awareness context`; `TEA board context awareness sensor cue`; `awareness device cue context fusion 1999` | a reimplementation or released code | 1 irrelevant hit, then 0 and 0 |
| GitHub code search API for the paper title | code citing the paper | HTTP 403 rate-limit; not established either way |
| `https://zenodo.org/api/records?q="there is more to context than location"` | deposited data/code | only unrelated works that cite the phrase; no deposit for this paper |
| `https://zenodo.org/api/records?q="Technology for Enabling Awareness"` | TEA project deposits | 0 hits |
| `https://api.osf.io/v2/nodes/?filter[title]=context than location` | OSF project | 0 results |
| `https://api.osf.io/v2/search/?q="more to context than location"` | OSF project or registration | 404 / no result |
| Web search for released TEA sensor data or replication code | data set, replication package | nothing; results are unrelated "TEA" projects |
| `web.archive.org`, `timetravel.mementoweb.org` | archived copies of the dead TEA pages | **unavailable to this audit**: `web.archive.org` returns HTTP 403 / is blocked by this environment's egress policy and the fetch tool refuses the host. Every "dead" verdict above therefore describes the live web only (see UNVERIFIED.md) |

### Related material by the same authors, used only as external context

Not artifacts of this paper, and never treated as if the audited paper contained them.
They matter only because they show how much of the awareness device the audited paper
leaves out:

- `https://www.teco.edu/~albrecht/publication/huc99/advanced_interaction_context.pdf` —
  Schmidt, Aidoo, Takaluoma, Tuomela, Van Laerhoven & Van de Velde, "Advanced Interaction
  in Context", HUC'99, LNCS 1707. HTTP 200. This companion paper *does* enumerate a TEA
  sensor board (photodiode, two accelerometers "filtered down to 200 Hz", temperature,
  pressure, CO gas sensor, microphone) and its polling scheme. The audited paper
  enumerates none of it.
- `https://www.teco.edu/~albrecht/publication/imc98.ps` — HTTP 200, the 1998 workshop
  version of the same title (PostScript; no converter available in this environment, so
  its contents were not compared line by line).

## What this repository contains

Only work written for this audit. The paper PDF and every other download live outside the
repository, under `/tmp`, and none of it is committed.
