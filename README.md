# Sahar

**How wrong is it when we date an idea?**

Detecting when a concept enters a literature is a routine operation in
scientometrics. It underpins work on emerging topics, novelty indicators and
research priority. It is rarely validated against a standard established outside
the data, because such standards are scarce.

This repository is an attempt to validate it anyway, and to report what that
costs.

The method is simple. Take concepts whose origin is documented independently,
such as Shannon on information theory in 1948, detect them in OpenAlex, and
report the signed error. An instrument that dates information theory to 1953 is
five years late, and there is no argument about it.

## What we found

| | |
|---|---|
| calibration cases | 28 usable, from 39 screened |
| raw detection error | 3.8 years, mean absolute |
| after a leave-one-out correction | 2.6 years |
| direction of the error | late, almost never early |

Three findings that transfer beyond this project:

**Search strategy dominates everything else.** Across five strategies scored
identically against the same controls, mean absolute error ranges from 25.0
years for unfiltered phrase search to 8.0 for multi-word phrases restricted to
relevant fields. Anchoring on modern topic assignments is among the worst, at
23.8, because a topic label reflects how a literature is classified now and not
how it read when the concept was new.

**Two failure modes operate with opposite signs.** Terms carrying an older
unrelated sense are detected too early. Holography is dated to 1939, nine years
before Gabor, because *holograph* is a probate term centuries older than the
physics. Once those are screened out the residual error is uniformly late.

**A screen validated against one detector gives no protection to another.** Our
proportional contamination screen passed a concept carrying 140 documents dated
before its origin, the earliest from 1828, because those documents were 0.047
per cent of a large literature. A count-based detector was then fooled into
dating the concept twenty years early. The screen's sensitivity falls as a
concept grows; the detector's does not. Any pipeline pairing a proportional
filter with an absolute detector is exposed to this, and the failure is silent.

`sahar/admit.py` is the remedy: run the detector itself over the pre-origin
window, and if it fires there, the concept cannot calibrate that detector.

## Status and caveat

**The origin dates are still being verified against primary sources, so every
figure here is provisional.** Checking the dates we were least sure of found
four carrying genuine priority disputes, including carbon nanotubes against
Radushkevich 1952 and public-key cryptography against Ellis at GCHQ. All four
were removed, which improved accuracy rather than merely shrinking the set.
Concepts whose origin the field disputes are listed separately in
`sahar/controls_v2.py` and excluded by default.

## Quick start

```bash
pip install pytest                      # the package itself needs no dependencies
export OPENALEX_MAILTO=you@example.org  # optional, for OpenAlex's polite pool
python -m pytest tests/ -q
python build_controls.py                # screen the candidate set
```

Every figure above is reproducible:

| script | what it produces |
|---|---|
| `build_controls.py` | the calibration set, screened, with per-concept errors |
| `sweep_controls.py` | coverage against accuracy across detector settings |
| `fit_correction.py` | correction models, scored by leave-one-out |
| `tracer_study.py` | why song-title tracers cannot calibrate concept dating |
| `reproduce_paper3.py` | the figures in the screens paper |

Responses are cached under `data/cache`, so a second run is offline and
identical. The cache is committed, which means the numbers can be checked
without network access and without waiting on a rate limit.

## Layout

```
sahar/
  openalex.py     API client with on-disk caching
  resolve.py      five disambiguation strategies behind one interface
  onset.py        onset detection and temporal relations
  threshold.py    a detector whose threshold scales with corpus size
  polysemy.py     screen for terms carrying an older unrelated sense
  admit.py        screen for whether a concept can calibrate a given detector
  concepts.py     the original six documented controls
  controls_v2.py  the expanded candidate set, with sources and disputes marked
  cultural.py     song-title tracers, used to validate the screens
  evaluate.py     scores strategies against documented origins
ui/index.html     a browser instrument; queries OpenAlex live, no server
tests/            regression tests for both screens
```

## The interface

`ui/index.html` is a single page with no build step and no backend. It queries
OpenAlex directly from the browser, runs both screens, and reports the signed
error for any concept you give it. Open the file locally, or see it published
through GitHub Pages.

The detection, screening and polysemy logic is ported to JavaScript and gives
the same answers as the Python: information theory returns onset 1953,
admissible, polysemy ok, in both.

## Data

Bibliographic metadata comes from [OpenAlex](https://openalex.org), used under
its open licence. No content was taken from any publisher. The second corpus
referenced in the papers, 10,441 art-science records, is bibliographic metadata
only.

## Citing

See `CITATION.cff`. A DOI will be minted on the first tagged release.

## Note on AI assistance

The software was written and executed with AI assistance under the first
author's direction. The research judgements are the authors': validating by
leave-one-out, treating the twenty-year miss as a diagnosis rather than
overfitting, reporting a parameter as unidentified instead of publishing a
fitted value, and excluding concepts whose origins the field disputes.

Two of our own errors are preserved in the history rather than removed. An
earlier version attributed the late bias to thin coverage of older literature,
which the measurements contradict. An earlier analysis concluded that a model
had overfitted, which `admit.py` shows was the wrong diagnosis.

## Authors

Abbas Bootwala and Roger F. Malina
ArtSciLab and Off-Center for Emergence Studies, The University of Texas at Dallas

## Licence

MIT, see `LICENSE`.
