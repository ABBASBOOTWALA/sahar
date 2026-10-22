"""Pull real matching documents for every bundled concept.

Counts alone ask to be trusted. Titles can be checked. For each concept we take
the earliest matches, which is where contamination shows itself, and the matches
around the detected onset, which is what made the detector fire.
"""
import io
import json
import time
import urllib.parse
import urllib.request

from sahar import admit, concepts, controls_v2, openalex, resolve, threshold

C_REF, BETA = 12, 0.0
API = "https://api.openalex.org/works"


def works(filters, per_page=6, sort="publication_year"):
    url = API + "?" + urllib.parse.urlencode(
        {"filter": ",".join(filters), "per-page": per_page, "sort": sort})
    req = urllib.request.Request(url, headers={"User-Agent": "SaharProject"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            break
        except Exception:
            if attempt == 2:
                return []
            time.sleep(2)
    out = []
    for w in d.get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {})
        out.append({
            "y": w.get("publication_year"),
            "t": (w.get("title") or "untitled")[:150],
            "v": (src.get("display_name") or "")[:70],
            "ty": w.get("type") or "",
        })
    return out


def main():
    totals = openalex.total_counts()
    strat = resolve.PhraseField()
    pool = controls_v2.UNCONTESTED + list(concepts.CONTROLS) + controls_v2.CONTESTED
    samples = {}

    for i, c in enumerate(pool, 1):
        key = c.terms[0].lower()
        phrase = openalex.phrase_query(c.terms)
        det = strat.counts(c)
        on = threshold.onset(det, totals, C_REF, BETA)

        # earliest matches anywhere, which is where contamination surfaces
        earliest = works([f"title_and_abstract.search:{phrase}",
                          openalex.exclude_leonardo(),
                          f"publication_year:<{c.science_origin}"],
                         per_page=6, sort="publication_year")

        # what the detector was looking at when it fired
        around = []
        if on:
            ids = "|".join(f"https://openalex.org/fields/{j}" for j in
                           [11, 12, 13, 16, 17, 21, 22, 25, 27, 31])
            around = works([f"title_and_abstract.search:{phrase}",
                            openalex.exclude_leonardo(),
                            f"primary_topic.field.id:{ids}",
                            f"publication_year:{on}-{on + 1}"],
                           per_page=6, sort="publication_year")

        samples[key] = {"e": earliest, "a": around, "on": on}
        print(f"{i:>3}/{len(pool)}  {c.name:<34} earliest {len(earliest):>2}  onset {len(around):>2}")

    b = json.loads(io.open('data/ui_bundle.json', encoding='utf-8').read())
    b["samples"] = samples
    s = json.dumps(b, separators=(',', ':'))
    io.open('data/ui_bundle.json', 'w', encoding='utf-8').write(s)
    print(f"\nbundle now {len(s)/1024:.0f} KB")


if __name__ == "__main__":
    main()
