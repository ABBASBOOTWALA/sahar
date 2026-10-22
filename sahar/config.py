"""Pre-registered parameters, held as data so a run can be reproduced from them.

Nothing here may be tuned after results are examined without recording the change
in CHANGELOG below and re-running every control.
"""
from dataclasses import dataclass, asdict, field

import os

# OpenAlex asks for a contact address so they can reach you if a script
# misbehaves. Set OPENALEX_MAILTO in your environment. Without it the
# client still works, just outside the polite pool and with lower limits.
MAILTO = os.environ.get("OPENALEX_MAILTO", "")
LEONARDO_ISSN = "0024-094X"

# The Leonardo family, excluded from the science side so that one document cannot
# appear on both sides of a comparison.
EXCLUDE_ISSN = ["0024-094X", "0961-1215", "1071-4391", "1748-7331"]

# OpenAlex records carry metadata errors at both extremes of the range; the floor
# is a guard, and any onset landing exactly on it is reported as censored.
MIN_YEAR = 1900


@dataclass(frozen=True)
class OnsetParams:
    """Asymmetric by design: the corpora differ by four orders of magnitude."""
    art_k: int = 2                 # substantive documents ...
    art_window: int = 3            # ... within this many years
    sci_share: float = 0.00002     # share of annual output
    sci_sustain: int = 3           # sustained for this many years
    simultaneous_tolerance: int = 2

    def as_dict(self):
        return asdict(self)


DEFAULT = OnsetParams()

CHANGELOG = [
    ("2026-09-04", "v1 absolute threshold both sides. Failed: science side fired on "
                   "metadata errors in a 320M corpus."),
    ("2026-09-04", "v2 proportional both sides. Failed: art side never fired on a "
                   "corpus of ~160 articles a year."),
    ("2026-09-04", "v3 asymmetric, current. Thresholds were tuned across these three "
                   "iterations against the same data, so v3 figures are exploratory."),
    ("2026-09-21", "Concept set rebuilt from the corpus after five of the original "
                   "eight were found to have zero presence before 1985."),
]
