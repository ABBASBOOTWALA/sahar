"""Thin OpenAlex client with on-disk caching.

Caching matters more than speed here: a cached run is a reproducible run, and the
cache key records exactly which query produced which numbers.
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import config

BASE = "https://api.openalex.org/works"
CACHE = Path(__file__).resolve().parent.parent / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)


def _get(params, retries=4):
    key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()[:20]
    hit = CACHE / f"{key}.json"
    if hit.exists():
        return json.loads(hit.read_text(encoding="utf-8"))

    q = dict(params)
    if config.MAILTO:
        q["mailto"] = config.MAILTO
    url = BASE + "?" + urllib.parse.urlencode(q)
    agent = f"SaharProject ({config.MAILTO})" if config.MAILTO else "SaharProject"
    req = urllib.request.Request(url, headers={"User-Agent": agent})
    for attempt in range(retries):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=90))
            hit.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def year_counts(filters):
    """Publication year -> document count, for a filter list."""
    d = _get({"filter": ",".join(filters), "group_by": "publication_year"})
    return {int(g["key"]): g["count"] for g in d.get("group_by", []) if g["key"].isdigit()}


def group_by(filters, dimension):
    d = _get({"filter": ",".join(filters), "group_by": dimension})
    return [(g["key"], g.get("key_display_name", g["key"]), g["count"])
            for g in d.get("group_by", [])]


def total_counts():
    """Yearly totals for the whole index, used to normalise the science side."""
    path = CACHE.parent / "openalex_totals.json"
    if path.exists():
        return {int(k): v for k, v in json.loads(path.read_text()).items()}
    t = year_counts(["primary_location.source.issn:!" + "|".join(config.EXCLUDE_ISSN)])
    path.write_text(json.dumps(t))
    return t


def phrase_query(terms):
    """Quoted OR query. Quoting matters: unquoted, 'artificial life' matches any
    document containing either word, which returns 133k instead of 6k."""
    return " OR ".join(f'"{t}"' for t in terms)


def exclude_leonardo():
    return "primary_location.source.issn:!" + "|".join(config.EXCLUDE_ISSN)
